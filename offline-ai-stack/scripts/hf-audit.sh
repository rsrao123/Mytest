#!/usr/bin/env bash
# Audit HuggingFace dependencies for runtime offline operation.
#
# Two checks:
#   1. File presence — every model directory listed below must exist
#      under ~/offline-ai-stack/models/<name>/ with a config.json.
#   2. Source-level repo-ID usage — flag any reference to "Qwen/...",
#      "BAAI/...", "mistralai/...", "Systran/...", or
#      "sentence-transformers/..." in *runtime* code (excludes offline-prep
#      and the design doc). If a runtime path uses a repo ID, it's an
#      online dependency in disguise.
#
# Usage:
#   bash scripts/hf-audit.sh                # report only
#   bash scripts/hf-audit.sh --strict       # exit 1 on any finding
#
# Pairs with scripts/offline-doctor.sh: hf-audit is structural (what
# could leak), offline-doctor is observed (what did leak).

set -euo pipefail

STRICT=0
[[ "${1:-}" == "--strict" ]] && STRICT=1

STACK_HOME="${STACK_HOME:-$HOME/offline-ai-stack}"
MODELS="$STACK_HOME/models"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Expected models (must match offline-prep.sh)
REQUIRED_MODELS=(
  "all-minilm-l6-v2"
  "bge-reranker-v2-m3"
  "faster-whisper-large-v3"
  "qwen3-embedding-8b"
  "qwen3-coder-next"
  "devstral-small-2"
)

FAILED=0

# ---- 1. File presence ------------------------------------------------------

echo "==> Model file presence under $MODELS/"
for name in "${REQUIRED_MODELS[@]}"; do
  dir="$MODELS/$name"
  if [[ ! -d "$dir" ]]; then
    echo "    MISSING  $name (directory not found)"
    FAILED=1
    continue
  fi
  if [[ ! -f "$dir/config.json" ]]; then
    # faster-whisper uses a different layout (no config.json at root)
    if [[ "$name" == faster-whisper-* ]] && [[ -d "$dir" ]]; then
      echo "    OK       $name (faster-whisper layout, present)"
      continue
    fi
    echo "    INCOMPLETE  $name (no config.json — re-run offline-prep)"
    FAILED=1
    continue
  fi
  echo "    OK       $name"
done

# ---- 2. Repo-ID usage in runtime code -------------------------------------

echo
echo "==> Repo-ID usage in runtime code"
# Files explicitly allowed to mention repo IDs. Two categories:
#   1. Setup-time scripts / configs / docs — repo IDs are part of the
#      one-time download flow or human-readable documentation.
#   2. Runtime code that uses repo IDs as labels passed to ChatOpenAI(model=...)
#      — these are vLLM --served-model-name aliases, NOT model loaders.
#      vLLM serves a local path under that label; the runtime never resolves
#      the label against the HF Hub.
ALLOWED_PATHS=(
  # Category 1: setup / config / docs
  "scripts/offline-prep.sh"
  "scripts/hf-audit.sh"
  "scripts/install-offline-superpowers.sh"
  "scripts/aider-mem"                # references model alias for aider CLI
  "configs/vllm-primary.service"     # --served-model-name alias
  "configs/vllm-devstral.service"    # same
  "OFFLINE_AI_STACK.md"
  "docs/SUPERPOWERS.md"
  "README.md"
  "promptfooconfig.yaml"             # provider names
  # Category 2: runtime crews that pass the alias to ChatOpenAI(model=)
  "scripts/claude_mem_local.py"
  "crews/dev_team.py"
  "crews/code_review.py"
  "crews/exec_review.py"
  "crews/security_review.py"
  "crews/merge_gate.py"
)

# Repo-ID prefixes to flag
PATTERNS='(Qwen/|BAAI/|mistralai/|Systran/|sentence-transformers/|meta-llama/)'

# Grep, then filter out allowed paths.
hits=$(grep -RIEn "$PATTERNS" "$REPO_ROOT" \
       --include='*.py' --include='*.sh' --include='*.yml' \
       --include='*.yaml' --include='*.toml' --include='*.service' --include='*.md' \
       2>/dev/null | grep -v -E '\.(pytest_cache|venv|__pycache__)' || true)

while IFS= read -r line; do
  [[ -z "$line" ]] && continue
  file="${line%%:*}"
  rel="${file#$REPO_ROOT/}"
  content="${line#*:*:}"          # drop "path:lineno:"

  # Strip leading whitespace from the content for context checks.
  stripped="${content#"${content%%[![:space:]]*}"}"

  # Path-level allowlist (setup-time scripts, configs, docs).
  allowed=0
  for p in "${ALLOWED_PATHS[@]}"; do
    if [[ "$rel" == "$p" || "$rel" == */"$p" ]]; then
      allowed=1
      break
    fi
  done

  # Context-level allowlist:
  # - Python / shell comment lines (start with #)
  # - vLLM service-name aliases passed to ChatOpenAI(model=...) — these
  #   are labels matching --served-model-name, not HF Hub lookups.
  if [[ "$stripped" == \#* ]] \
     || echo "$content" | grep -qE 'ChatOpenAI|served-model-name|LLM_MODEL=' ; then
    allowed=1
  fi

  if [[ $allowed -eq 0 ]]; then
    echo "    UNEXPECTED  $line"
    FAILED=1
  fi
done <<< "$hits"

# ---- 3. Runtime Python imports of huggingface_hub -------------------------

echo
echo "==> huggingface_hub imports in runtime Python"
hf_hub_hits=$(grep -RIEn "^(from huggingface_hub|import huggingface_hub)" "$REPO_ROOT" \
              --include='*.py' 2>/dev/null \
              | grep -v -E '/(scripts/offline-prep|scripts/hf-audit|tests/)' \
              || true)
if [[ -n "$hf_hub_hits" ]]; then
  echo "$hf_hub_hits" | while IFS= read -r line; do
    echo "    UNEXPECTED  $line"
  done
  FAILED=1
else
  echo "    none in runtime code"
fi

echo
if [[ $FAILED -eq 0 ]]; then
  echo "PASS: every required model is present and no runtime code references HF repo IDs or imports huggingface_hub."
  exit 0
fi

echo "FAIL: see findings above."
if [[ $STRICT -eq 1 ]]; then
  exit 1
fi
exit 0
