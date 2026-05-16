# Mini GPT

A small decoder-only Transformer language model (GPT-style) implemented in
PyTorch. Trains on a local plain-text file with a character-level tokenizer
and saves the trained weights to disk so you can resume or generate text
later.

## Setup

```bash
pip install -r requirements.txt
```

## Files

- `mini_gpt.py` — model, tokenizer, training and generation entry points
- `input.txt` — the training text (a Shakespeare snippet by default; replace it with any plain-text file)
- `mini_gpt.pt` — checkpoint written after training (created on first run)

## Train

```bash
python mini_gpt.py train
```

This reads `input.txt`, builds a character vocab, trains the model for
`max_iters` steps (defaults are CPU-friendly), prints periodic train/val
loss, then writes `mini_gpt.pt`.

## Generate

```bash
python mini_gpt.py generate "ROMEO:"
python mini_gpt.py generate "HAMLET:" --tokens 500 --temperature 0.8 --top-k 40
```

If no checkpoint exists yet, `python mini_gpt.py` (no args) will train one
and then sample from it.

## Train on your own data

Drop any UTF-8 plain-text file in at `input.txt` (bigger is better — at
least a few hundred KB for vaguely coherent samples) and re-run training.
A larger corpus benefits from raising `n_embd`, `n_layer`, `block_size`,
and `max_iters` at the top of `mini_gpt.py`.

## Architecture (matches GPT-style decoder)

- Token + learned positional embeddings
- N Transformer blocks: pre-LayerNorm + causal multi-head self-attention + feed-forward (GELU, 4x expansion), with residual connections
- Final LayerNorm + linear LM head
- Cross-entropy loss against next-token targets
- Sampling with temperature and top-k
