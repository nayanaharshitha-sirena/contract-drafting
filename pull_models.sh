#!/bin/bash

echo "📥 Downloading LLM models for contract generation..."
echo "=================================================="

# Phi-3 (3.8B) - Recommended balance of speed and quality
echo "📥 Downloading Phi-3 3.8B (Recommended)..."
ollama pull phi3:3.8b

# TinyLlama (1.1B) - Fastest option
echo "📥 Downloading TinyLlama 1.1B (Fastest)..."
ollama pull tinyllama

# Qwen2 (1.5B) - Balanced
echo "📥 Downloading Qwen2 1.5B (Balanced)..."
ollama pull qwen2:1.5b

# Mistral (7B) - Most accurate
echo "📥 Downloading Mistral 7B (Most Accurate)..."
ollama pull mistral

echo ""
echo "✅ All models downloaded successfully!"
echo ""
echo "Available models:"
ollama list