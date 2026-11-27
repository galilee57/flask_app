#!/bin/sh
set -eu

cache_dir="${LLM_CACHE_DIR:-${HOME}/.cache/flask-portfolio-llm}"
revision=cd0c74c575b5c416f3011b5b4c298077f26ca8c2
filename=LFM3-1.7B-Q4_K_M.gguf
checksum=3793e1e6e2266919d6e015287221b41100175a98eddaba92e111aed3b05c93c4
model="$cache_dir/$revision-$filename"

mkdir -p "$cache_dir"
if [ ! -f "$model" ]; then
    temporary=$(mktemp "$cache_dir/download.XXXXXX")
    trap 'unlink "$temporary"' EXIT
    trap 'exit 1' HUP INT TERM
    curl --fail --location --retry 3 --connect-timeout 15 --output "$temporary" \
        "https://huggingface.co/LiquidAI/LFM3-1.7B-GGUF/resolve/$revision/$filename"
    if command -v sha256sum >/dev/null 2>&1; then
        printf '%s  %s\n' "$checksum" "$temporary" | sha256sum -c -
    else
        printf '%s  %s\n' "$checksum" "$temporary" | shasum -a 256 -c -
    fi
    mv "$temporary" "$model"
    trap - EXIT HUP INT TERM
fi

exec "${LLAMA_SERVER:-llama-server}" --model "$model" --alias lfm3-1.7b \
    --host "${LLM_HOST:-127.0.0.1}" --port "${PORT:-8081}" \
    --ctx-size "${LLM_CONTEXT_SIZE:-4096}" --parallel 1 --no-ui --cors-origins localhost --jinja \
    --reasoning off --temp 0.1 --top-k 50 --repeat-penalty 1.1 "$@"
