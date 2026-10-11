---
title: Understanding GPT from scratch
summary: A small hand-coded language model built with PyTorch
---

### A hand-coded GPT
This project builds a character-level autoregressive model: tokenizer, embeddings, causal multi-head attention, residual connections, normalization and Transformer blocks. The model engine is **hand-coded** with PyTorch; the portfolio integration was implemented with Codex.

### How to use it
Select a model and enter a text prefix compatible with its vocabulary. Click **Generate**: the model continues the prompt. It does not necessarily follow instructions like a conversational assistant. The prompt appears in gray and the continuation in black. For char models, one token is a character; for BPE models, it represents a text fragment. Output is limited to 500 new tokens and prompts to 1,000 characters.

A low temperature favors already likely characters; a high temperature produces more varied sampling. The seed reproduces sampling in the same software environment. Results can differ across software versions or hardware. Context is the number of preceding tokens used for each prediction.

### Languages
The interface language is independent of the corpus language. Current experiments use French text; English experiments can be added later. Some vocabularies do not include uppercase letters or accents. Unsupported characters are reported without silently modifying your input.

### Training curves
The blue curve shows training loss and the orange curve validation loss. The horizontal axis counts updates; loss is cross entropy using natural logarithms. The outlined point indicates the best evaluation, whose weights are used for generation. The table provides exact measurements. These measurements come from local training runs; the website does not train models.

Lower loss indicates better predictions on the evaluated text. Different corpora or vocabularies do not provide a direct quality ranking. The synthetic general corpus contains repeated structures: low loss does not demonstrate general reasoning ability. Generated text may be incoherent or incorrect.

### Execution
Generation runs on the Flask server CPU using local checkpoints. Models load on demand; each process caches only one model. The application uses the prompt only for generation and does not store it. No external generation service is called.
