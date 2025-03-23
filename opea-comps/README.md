
# Translation Mega Service

To explore OPEA architecture, we identified one of the examples [Translation Application](https://opea-project.github.io/latest/GenAIExamples/Translation/README.html) which could be a valuable service for the students. Specifically, we want to deploying it on local hardware via Ollama, which allows us to test and provide the service to students at predictable cost.

Compared to other examples services, an advantage of the Translation Application is that it is relative simple, which is beneficial for gaining an understanding of the OPEA project. 

We were able to run the application successfuly.

The application is consists of:
- Translation App frontend (opea/translation-ui)
- Translation MegaService (opea/translation)
- LLM MicroService (opea/llm-textgen)
- LLM Service (ollama/ollama)

OpenTelemetry and Nginx are disabled/omitted for the time being, for simplicity.


## Running the application

I encountered issues with docker container networking, where the LLM container could not connect to Ollama. 
To isolate this problem, I focused on running the application from source, with the exception of Ollama being served from Docker.


### Ollama - run from docker

Reference: https://github.com/opea-project/GenAIComps/blob/main/comps/third_parties/ollama/README.md

We can pull the pre-existing ollama image, no need to build this image

```sh
cd GenAIComps/comps/third_parties/ollama/deployment/docker_compose
docker compose up -d
```

**Pull a model**
```
docker exec -it ollama-server ollama pull gemma2:2b
```
Or from within the Docker container attached shell:
```
ollama pull gemma2:2b
```


**Validate Ollama**
```sh
curl "http://${host_ip}:${LLM_ENDPOINT_PORT}/api/generate" -d "{
    \"model\": \"${LLM_MODEL_ID}\", 
    \"prompt\":\"Why is the sky blue?\"
}"
```

Later we can update the Docker compose file to use volume, so we don't need to download the model every time.



### Install Prerequisits / Environment Variables 

```sh
pip install -r GenAIComps/comps/llms/src/text-generation/requirements.txt
pip install opea-comps
source set_env.sh
```


### LLM MicroService

```sh
cd GenAIComps/comps/llms/src/text-generation
python3 opea_llm_microservice.py
```


**Check LLM MicroService status**

```sh
curl "http://${host_ip}:${TEXTGEN_PORT}/v1/health_check" \
  -X GET \
  -H 'Content-Type: application/json'
```


**Validate LLM MicroService**

```sh
curl "http://${host_ip}:${TEXTGEN_PORT}/v1/chat/completions" \
    -X POST \
    -d '{"model": "${LLM_MODEL_ID}", "messages": "What is Deep Learning?", "max_tokens":17}' \
    -H 'Content-Type: application/json'
```


### Translation MegaService

```sh
cd GenAIExamples/Translation
python3 translation.py
```

By default, OpenTelemetry will try to export traces but can't connect to the collector, causing ConnectionError on port 4318. 
To resolve this we can disable OpenTelemetry through these environment variables.

```sh
export OTEL_SDK_DISABLED=true
export OTEL_TRACES_EXPORTER=none
```


**Validate Translation MegaService**

```sh
curl "http://${host_ip}:8888/v1/translation" -H "Content-Type: application/json" -d '{
    "language_from": "English",
    "language_to": "Japanese", 
    "source_language": "Test message"
}'
```


### Translation App frontend

```sh
cd GenAIExamples/Translation/ui/svelte 
npm install
npm run dev
```


The frontend app makes request to `/v1/translation` (defined in .env). 

The OPEA example [full instruction](https://opea-project.github.io/latest/GenAIExamples/Translation/docker_compose/intel/cpu/xeon/README.html) uses `nginx` to proxy user input query. Without it, the requests fail to resolve.

Solution: update `vite.config.ts` to proxy the request directly to the Translation MegaService running on port 8888.



----


## Deployment with Docker


### LLM MicroService - build image

Reference: https://github.com/opea-project/GenAIComps/blob/main/comps/llms/src/text-generation/README.md

```sh
cd GenAIComps
docker build -t opea/llm-textgen:latest --build-arg https_proxy=$https_proxy --build-arg http_proxy=$http_proxy -f comps/llms/src/text-generation/Dockerfile .
```

The image did not build successfully initially. After inspecting the errors, it was determined that `RUN pip install ...` failed because the following tools were missing:
`gcc`, `g++`, `git`, and insufficient version of compiler.

This is likely because the base image (python:3.11-slim) doesn't include these build tools by default to keep the image size small.


To fix the errors, the Dockerfile needs to be modified to add the following line _before_ the line that starts with `RUN pip install ...`:


```dockerfile
RUN apt-get update -y && apt-get install -y --no-install-recommends build-essential cmake git
```

The build was able to complete with this modification.


**Run LLM MicroService**

Added the text-gen service to the compose file, using `textgen-service-ollama`
https://github.com/opea-project/GenAIComps/blob/main/comps/llms/deployment/docker_compose/compose_text-generation.yaml


Failed!!! cannot get one docker service to talk to another?



#TODO: docker deployment by building other images, and making them work with docket networking


