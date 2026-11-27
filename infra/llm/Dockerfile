FROM ghcr.io/ggml-org/llama.cpp:server-b11960@sha256:8052c13edd987de8858f8150031e025ac3d66823f09cf3ec8220899c4abce220

ENV LLM_CACHE_DIR=/models LLAMA_SERVER=/app/llama-server LLM_HOST=:: PORT=8081
COPY start.sh /app/start-llm.sh
EXPOSE 8081
HEALTHCHECK CMD ["curl", "-fsS", "--noproxy", "*", "http://localhost:8081/health"]
ENTRYPOINT ["sh", "/app/start-llm.sh"]
