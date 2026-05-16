"""
Mini GPT - a small decoder-only Transformer language model.

Trains on a local text file (default: input.txt) using a character-level
tokenizer. Saves the trained weights so you can resume / generate later.

Usage:
    python mini_gpt.py train            # train and save checkpoint
    python mini_gpt.py generate "ROMEO:" # generate text from a prompt
    python mini_gpt.py                  # train (if no checkpoint) then sample
"""

import os
import sys
import json
import math
import argparse

import torch
import torch.nn as nn
import torch.nn.functional as F


# ==========================================
# 1. HYPERPARAMETERS
# ==========================================
# Defaults sized so this runs on CPU in a reasonable time.
# Scale up (n_embd, n_layer, block_size) if you have a GPU.
block_size = 128
n_embd = 192
n_head = 6
n_layer = 6
dropout = 0.1
batch_size = 32
learning_rate = 3e-4
max_iters = 3000
eval_interval = 200
eval_iters = 50
device = 'cuda' if torch.cuda.is_available() else 'cpu'

DATA_PATH = os.path.join(os.path.dirname(__file__), 'input.txt')
CKPT_PATH = os.path.join(os.path.dirname(__file__), 'mini_gpt.pt')


# ==========================================
# 2. CHARACTER-LEVEL TOKENIZER
# ==========================================
class CharTokenizer:
    """Maps each unique character to an integer id."""

    def __init__(self, text):
        chars = sorted(list(set(text)))
        self.vocab_size = len(chars)
        self.stoi = {ch: i for i, ch in enumerate(chars)}
        self.itos = {i: ch for i, ch in enumerate(chars)}

    def encode(self, s):
        return [self.stoi[c] for c in s if c in self.stoi]

    def decode(self, ids):
        return ''.join(self.itos[int(i)] for i in ids)

    def to_dict(self):
        return {'stoi': self.stoi, 'itos': {str(k): v for k, v in self.itos.items()}}

    @classmethod
    def from_dict(cls, d):
        obj = cls.__new__(cls)
        obj.stoi = d['stoi']
        obj.itos = {int(k): v for k, v in d['itos'].items()}
        obj.vocab_size = len(obj.stoi)
        return obj


# ==========================================
# 3. MODEL COMPONENTS
# ==========================================
class Head(nn.Module):
    """One head of causal self-attention."""

    def __init__(self, head_size):
        super().__init__()
        self.key = nn.Linear(n_embd, head_size, bias=False)
        self.query = nn.Linear(n_embd, head_size, bias=False)
        self.value = nn.Linear(n_embd, head_size, bias=False)
        self.register_buffer('tril', torch.tril(torch.ones(block_size, block_size)))
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        B, T, C = x.shape
        k = self.key(x)
        q = self.query(x)
        wei = q @ k.transpose(-2, -1) * (k.size(-1) ** -0.5)
        wei = wei.masked_fill(self.tril[:T, :T] == 0, float('-inf'))
        wei = F.softmax(wei, dim=-1)
        wei = self.dropout(wei)
        v = self.value(x)
        return wei @ v


class MultiHeadAttention(nn.Module):
    def __init__(self, num_heads, head_size):
        super().__init__()
        self.heads = nn.ModuleList([Head(head_size) for _ in range(num_heads)])
        self.proj = nn.Linear(n_embd, n_embd)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        return self.dropout(self.proj(out))


class FeedForward(nn.Module):
    def __init__(self, n_embd):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd),
            nn.GELU(),
            nn.Linear(4 * n_embd, n_embd),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        return self.net(x)


class Block(nn.Module):
    """Transformer block: self-attention + feed-forward, with residuals."""

    def __init__(self, n_embd, n_head):
        super().__init__()
        head_size = n_embd // n_head
        self.sa = MultiHeadAttention(n_head, head_size)
        self.ffwd = FeedForward(n_embd)
        self.ln1 = nn.LayerNorm(n_embd)
        self.ln2 = nn.LayerNorm(n_embd)

    def forward(self, x):
        x = x + self.sa(self.ln1(x))
        x = x + self.ffwd(self.ln2(x))
        return x


# ==========================================
# 4. THE MINI-GPT MODEL
# ==========================================
class MiniGPT(nn.Module):
    def __init__(self, vocab_size):
        super().__init__()
        self.vocab_size = vocab_size
        self.token_embedding_table = nn.Embedding(vocab_size, n_embd)
        self.position_embedding_table = nn.Embedding(block_size, n_embd)
        self.blocks = nn.Sequential(*[Block(n_embd, n_head=n_head) for _ in range(n_layer)])
        self.ln_f = nn.LayerNorm(n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size)
        self.apply(self._init_weights)

    @staticmethod
    def _init_weights(module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx, targets=None):
        B, T = idx.shape
        tok_emb = self.token_embedding_table(idx)
        pos_emb = self.position_embedding_table(torch.arange(T, device=idx.device))
        x = tok_emb + pos_emb
        x = self.blocks(x)
        x = self.ln_f(x)
        logits = self.lm_head(x)

        if targets is None:
            loss = None
        else:
            B, T, C = logits.shape
            loss = F.cross_entropy(logits.view(B * T, C), targets.view(B * T))
        return logits, loss

    @torch.no_grad()
    def generate(self, idx, max_new_tokens, temperature=1.0, top_k=None):
        self.eval()
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -block_size:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :] / temperature
            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = float('-inf')
            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)
        return idx


# ==========================================
# 5. DATA LOADING
# ==========================================
def load_data():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"Training file not found: {DATA_PATH}\n"
            "Drop a plain-text file at that path (any UTF-8 text works)."
        )
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    if len(text) < block_size + 1:
        raise ValueError(f"input.txt is too small ({len(text)} chars); need > {block_size}.")
    return text


def make_batches(data, split_data):
    def get_batch(split):
        d = data if split == 'train' else split_data
        ix = torch.randint(len(d) - block_size, (batch_size,))
        x = torch.stack([d[i:i + block_size] for i in ix])
        y = torch.stack([d[i + 1:i + block_size + 1] for i in ix])
        return x.to(device), y.to(device)
    return get_batch


@torch.no_grad()
def estimate_loss(model, get_batch):
    out = {}
    model.eval()
    for split in ('train', 'val'):
        losses = torch.zeros(eval_iters)
        for k in range(eval_iters):
            X, Y = get_batch(split)
            _, loss = model(X, Y)
            losses[k] = loss.item()
        out[split] = losses.mean().item()
    model.train()
    return out


# ==========================================
# 6. TRAIN / GENERATE ENTRY POINTS
# ==========================================
def train():
    print(f"Using device: {device}")
    text = load_data()
    tokenizer = CharTokenizer(text)
    print(f"Loaded {len(text):,} characters, vocab size = {tokenizer.vocab_size}")

    data = torch.tensor(tokenizer.encode(text), dtype=torch.long)
    n = int(0.9 * len(data))
    train_data, val_data = data[:n], data[n:]
    get_batch = make_batches(train_data, val_data)

    model = MiniGPT(tokenizer.vocab_size).to(device)
    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Total trainable parameters: {n_params:,}")

    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

    print("Starting training...")
    for step in range(max_iters):
        if step % eval_interval == 0 or step == max_iters - 1:
            losses = estimate_loss(model, get_batch)
            print(f"step {step:>5} | train {losses['train']:.4f} | val {losses['val']:.4f}")

        xb, yb = get_batch('train')
        _, loss = model(xb, yb)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

    torch.save({
        'model_state': model.state_dict(),
        'tokenizer': tokenizer.to_dict(),
        'config': {
            'block_size': block_size, 'n_embd': n_embd,
            'n_head': n_head, 'n_layer': n_layer, 'dropout': dropout,
        },
    }, CKPT_PATH)
    print(f"Saved checkpoint to {CKPT_PATH}")

    print("\nSample after training:")
    sample(model, tokenizer, prompt="\n", max_new_tokens=300)
    return model, tokenizer


def load_checkpoint():
    ckpt = torch.load(CKPT_PATH, map_location=device)
    tokenizer = CharTokenizer.from_dict(ckpt['tokenizer'])
    model = MiniGPT(tokenizer.vocab_size).to(device)
    model.load_state_dict(ckpt['model_state'])
    return model, tokenizer


def sample(model, tokenizer, prompt="\n", max_new_tokens=500, temperature=1.0, top_k=40):
    ids = tokenizer.encode(prompt) or [0]
    context = torch.tensor([ids], dtype=torch.long, device=device)
    out = model.generate(context, max_new_tokens=max_new_tokens,
                         temperature=temperature, top_k=top_k)[0].tolist()
    text = tokenizer.decode(out)
    print(text)
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', nargs='?', default='auto',
                        choices=['auto', 'train', 'generate'])
    parser.add_argument('prompt', nargs='?', default="\n")
    parser.add_argument('--tokens', type=int, default=500)
    parser.add_argument('--temperature', type=float, default=1.0)
    parser.add_argument('--top-k', type=int, default=40)
    args = parser.parse_args()

    if args.command == 'train' or (args.command == 'auto' and not os.path.exists(CKPT_PATH)):
        model, tokenizer = train()
    else:
        print(f"Loading checkpoint from {CKPT_PATH}")
        model, tokenizer = load_checkpoint()

    if args.command == 'generate' or args.command == 'auto':
        print("\n--- Generation ---")
        sample(model, tokenizer, prompt=args.prompt,
               max_new_tokens=args.tokens,
               temperature=args.temperature, top_k=args.top_k)


if __name__ == '__main__':
    main()
