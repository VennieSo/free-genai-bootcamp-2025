export LLM_ENDPOINT_PORT=8008
export TEXTGEN_PORT=9000
export host_ip=localhost
# export HF_TOKEN=${HF_TOKEN}  # Hugging Face token is not needed when running on Ollama
export LLM_ENDPOINT="http://${host_ip}:${LLM_ENDPOINT_PORT}"
export LLM_MODEL_ID="gemma2:2b"
export service_name="textgen-service-ollama"