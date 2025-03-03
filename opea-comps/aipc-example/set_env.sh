#!/usr/bin/env bash

# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

# pushd "../../../../../" > /dev/null

# # Check if .set_env.sh exists before sourcing
# if [ -f ".set_env.sh" ]; then
#     source .set_env.sh
# else
#     echo "Error: .set_env.sh not found."
#     exit 1
# fi

# popd > /dev/null

export host_ip=$(hostname | awk '{print $1}')

if [ -z "${HUGGINGFACEHUB_API_TOKEN}" ]; then
    echo "Error: HUGGINGFACEHUB_API_TOKEN is not set. Please set HUGGINGFACEHUB_API_TOKEN."
fi

if [ -z "${host_ip}" ]; then
    echo "Error: host_ip is not set. Please set host_ip first."
fi

export HUGGINGFACEHUB_API_TOKEN=${HUGGINGFACEHUB_API_TOKEN}
export EMBEDDING_MODEL_ID="BAAI/bge-base-en-v1.5"
export RERANK_MODEL_ID="BAAI/bge-reranker-base"
export INDEX_NAME="rag-redis"
export OLLAMA_HOST=${host_ip}
export OLLAMA_MODEL="llama3.2:1b"
# Set it as a non-null string, such as true, if you want to enable logging facility,
# otherwise, keep it as "" to disable it.
export LOGFLAG=""
