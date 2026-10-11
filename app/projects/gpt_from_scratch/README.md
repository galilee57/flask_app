# GPT portfolio demonstrator

The vendored `engine/` comes from the hand-coded local my-gpt project, with imports adapted to this blueprint. `models/<id>/` contains trusted local weights, sanitized configuration, training metrics and archived samples. No training command runs on the website.

Run `pip install -r requirements-gpt.txt` in addition to the application dependencies to enable CPU inference. PyTorch is imported lazily: the portfolio and curves remain available without it, while generation returns a translated unavailable message. Benchmark staging latency and worker memory before deployment; each Gunicorn worker caches one model and admits one concurrent inference. Requests are limited to six per minute per client IP and worker, with a bounded address table. These limits are per process; a reverse proxy may impose a shared limit. CPU intra-operation parallelism is limited to one thread to avoid oversubscription.

To add an experiment, copy `best_model.pt`, `config.json` and `metrics.csv` into a new model directory. Only install trusted checkpoints. Set `language` to `fr` or `en` in config, remove machine-local paths, and retain `model_config`, `parameter_count`, `corpus_characters`, `learning_rate` and `max_steps`. The tokenizer and weights must match. A deployment can set the `GPT_MODELS_DIR` environment variable to an external directory instead. No database migration or administrative write endpoint is introduced.

The catalog exposes only explicit public fields, never checkpoint contents or local paths. POST `/api/generate` is a read-only computation with bounded prompt, temperature, seed and output length. Persistent-write admin authorization remains unchanged.

The production Docker image installs the pinned PyTorch CPU wheel and tokenizers. No GPU runtime is required. Existing generic dependency lock files remain unchanged; inference dependencies are pinned separately in requirements-gpt.txt.

Release checkpoints contain only inference tensors, architecture, tokenizer and checkpoint step/loss. Optimizer state and machine-local training metadata have been removed. The PythonAnywhere staging workflow installs the CPU wheel before the application dependencies.
