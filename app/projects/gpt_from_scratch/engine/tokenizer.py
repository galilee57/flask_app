from pathlib import Path
from typing import List
import torch

class CharTokenizer:
    def __init__(self, text: str, charset: str = None):

        # If charset is provided, use it; otherwise, derive charset from the text
        if charset is None:
            self.chars = sorted(list(set(text)))
        elif text is not None:
            self.chars = sorted(list(set(charset)))
        else:
            raise ValueError("Either text or charset must be provided.")

        self.vocab_size = len(self.chars)

        # string -> int
        self.stoi = {ch: i for i, ch in enumerate(self.chars)}

        # int -> string
        self.itos = {i: ch for i, ch in enumerate(self.chars)}

    def encode(self, text: str) -> List[int]:

        unknown = set(text) - set(self.stoi)

        if unknown:
            raise ValueError(f"Unknown characters found in text: {unknown}")

        return [self.stoi[ch] for ch in text]

    def decode(self, tokens: List[int]) -> str:

        return "".join([self.itos[token] for token in tokens])

class BPETokenizer:
    """Byte-level BPE; all UTF-8 input can be encoded without unknown tokens."""

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.vocab_size = tokenizer.get_vocab_size()

    @classmethod
    def train(cls, text: str, vocab_size: int = 512):
        if vocab_size < 256:
            raise ValueError("Le vocabulaire BPE doit contenir au moins 256 tokens.")
        from tokenizers import Tokenizer, models, pre_tokenizers, decoders, trainers
        tokenizer = Tokenizer(models.BPE())
        tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
        tokenizer.decoder = decoders.ByteLevel()
        trainer = trainers.BpeTrainer(
            vocab_size=vocab_size, initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
            show_progress=False,
        )
        tokenizer.train_from_iterator([text], trainer=trainer)
        return cls(tokenizer)

    def encode(self, text: str) -> List[int]:
        return self.tokenizer.encode(text, add_special_tokens=False).ids

    def decode(self, tokens: List[int]) -> str:
        # Arbitrary sampled byte tokens may form invalid UTF-8; the decoder
        # replaces these sequences with the Unicode replacement character.
        return self.tokenizer.decode(tokens, skip_special_tokens=False)


def tokenizer_state(tokenizer):
    if isinstance(tokenizer, CharTokenizer):
        return {"type": "char", "chars": tokenizer.chars}
    return {"type": "bpe", "json": tokenizer.tokenizer.to_str()}


def tokenizer_from_checkpoint(checkpoint):
    state = checkpoint.get("tokenizer")
    if state is None:  # Historical character checkpoints.
        state = {"type": "char", "chars": checkpoint["tokenizer_chars"]}
    if state["type"] == "char":
        tokenizer = CharTokenizer("", charset="".join(state["chars"]))
        if tokenizer.chars != state["chars"]:
            raise ValueError("L'ordre des caracteres du checkpoint est incompatible avec le tokenizer.")
        return tokenizer
    if state["type"] == "bpe":
        from tokenizers import Tokenizer
        return BPETokenizer(Tokenizer.from_str(state["json"]))
    raise ValueError(f"Type de tokenizer inconnu : {state['type']}")


if __name__ == "__main__":

    corpus_path = Path(__file__).resolve().parents[1] / "data" / "processed" / "corpus10k.txt"
    with open(corpus_path, "r", encoding="utf-8") as f:
        text = f.read()

    tokenizer = CharTokenizer(text)

    print("Vocabulaire :", tokenizer.chars)
    print("Taille du vocabulaire :", tokenizer.vocab_size)

    # Test encoding and decoding
    sample_text = "bonjour"
    encoded = tokenizer.encode(sample_text)
    print("Encoded:", encoded)

    decoded = tokenizer.decode(encoded)
    print("Decoded:", decoded)

    tokens = tokenizer.encode(text=text)

    data = torch.tensor(
        tokens,
        dtype=torch.long
    )

    print(f"Data: {data}, Shape: {data.shape}, Dtype: {data.dtype}")