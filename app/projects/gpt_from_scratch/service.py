"""Read-only experiment catalog and bounded inference on trusted local weights."""
import csv
import json
import math
from pathlib import Path
from threading import Lock
from time import monotonic

from flask import current_app

_LOCK = Lock()
_CACHE = {}
_RATE_LOCK = Lock()


def admit_generation(address):
    """Bound requests per client and worker without storing prompts."""
    now = monotonic()
    with _RATE_LOCK:
        clients = current_app.extensions.setdefault("gpt_requests", {})
        for key in list(clients):
            clients[key] = [stamp for stamp in clients[key] if now - stamp < 60]
            if not clients[key]:
                del clients[key]
        if address not in clients and len(clients) >= 2048:
            return False
        recent = clients.setdefault(address, [])
        if len(recent) >= 6:
            return False
        recent.append(now)
        return True



def model_directory():
    return Path(current_app.config.get('GPT_MODELS_DIR', Path(__file__).parent / 'models'))


def catalog():
    models = []
    for path in sorted(model_directory().glob('*/config.json')):
        if not (path.parent / 'best_model.pt').is_file():
            continue
        config = json.loads(path.read_text())
        with (path.parent / 'metrics.csv').open(newline='') as stream:
            metrics = [{key: float(value) for key, value in row.items()} for row in csv.DictReader(stream)]
        models.append({
            'tokenizer': config.get('tokenizer', 'char'),
            'id': path.parent.name, 'language': config.get('language', 'fr'),
            'architecture': config['model_config'],
            'parameters': config.get('parameter_count'),
            'corpus_characters': config.get('corpus_characters'),
            'learning_rate': config.get('learning_rate'),
            'max_steps': config.get('max_steps'), 'metrics': metrics,
        })
    return models


def validate(payload):
    if not isinstance(payload, dict):
        raise ValueError('invalid_request')
    model_id = payload.get('model')
    if not isinstance(model_id, str) or model_id not in {model['id'] for model in catalog()}:
        raise ValueError('invalid_model')
    prompt = payload.get('prompt')
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 1000:
        raise ValueError('invalid_prompt')
    tokens = payload.get('tokens', 200)
    seed = payload.get('seed', 42)
    temperature = payload.get('temperature', 0.8)
    if type(tokens) is not int or not 1 <= tokens <= 500:
        raise ValueError('invalid_tokens')
    if type(seed) is not int or not 0 <= seed <= 2147483647:
        raise ValueError('invalid_seed')
    if type(temperature) not in (float, int) or not math.isfinite(temperature) or not 0.1 <= temperature <= 2:
        raise ValueError('invalid_temperature')
    return model_id, prompt, tokens, temperature, seed


def generate(model_id, prompt, tokens, temperature, seed):
    if not _LOCK.acquire(blocking=False):
        raise BlockingIOError('busy')
    try:
        import torch
        from .engine.models.gpt import GPT
        from .engine.tokenizer import tokenizer_from_checkpoint
        path = model_directory() / model_id / 'best_model.pt'
        key = (str(path), path.stat().st_mtime_ns)
        if key not in _CACHE:
            torch.set_num_threads(1)
            checkpoint = torch.load(path, map_location='cpu', weights_only=True)
            tokenizer = tokenizer_from_checkpoint(checkpoint)
            if tokenizer.vocab_size != checkpoint['model_config']['vocab_size']:
                raise RuntimeError('Invalid tokenizer vocabulary')
            model = GPT(**checkpoint['model_config'])
            model.load_state_dict(checkpoint['model_state_dict'])
            model.eval()
            _CACHE.clear()  # Keep only one model per server worker.
            _CACHE[key] = model, tokenizer
        model, tokenizer = _CACHE[key]
        try:
            encoded = tokenizer.encode(prompt)
        except ValueError:
            raise ValueError('unsupported_characters') from None
        with torch.random.fork_rng(devices=[]), torch.inference_mode():
            torch.manual_seed(seed)
            output = model.generate(torch.tensor([encoded], dtype=torch.long), tokens, temperature)
        return tokenizer.decode(output[0].tolist()[len(encoded):])
    finally:
        _LOCK.release()
