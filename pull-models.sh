#!/bin/bash
echo "Pulling Ollama models..."
docker exec ollama ollama pull mxbai-embed-large
echo "Models pulled successfully!"