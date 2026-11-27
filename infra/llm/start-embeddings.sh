#!/bin/sh
set -eu

exec "${LLAMA_SERVER:-llama-server}" \
    --hf-repo Qwen/Qwen3-Embedding-0.6B-GGUF:Q8_0 \
    --embedding --pooling last --alias qwen3-embedding-0.6b \
    --host 127.0.0.1 --port "${RAG_EMBEDDING_PORT:-8082}" \
    --ctx-size 2048 --parallel 4 --batch-size 2048 --ubatch-size 2048 \
    --no-ui --cors-origins localhost --log-verbosity 2
