#!/bin/bash
echo "📥 Downloading Phi-3 3.8B model (optimized for contract generation)..."
ollama pull phi3:3.8b

echo "📥 Downloading TinyLlama 1.1B (lightweight fallback)..."
ollama pull tinyllama

echo "📥 Downloading Qwen2 1.5B (alternative)..."
ollama pull qwen2:1.5b

echo "✅ All 3B models downloaded!"