#!/bin/bash

echo "🚀 LEGAL LLM TRAINING SETUP"
echo "============================"

# Step 1: Install required packages
echo "📦 Installing Python packages..."
pip install kagglehub pandas transformers datasets accelerate torch unsloth trl

# Step 2: Download and prepare dataset
echo "📥 Preparing training data..."
cd backend/train
python prepare_training_data.py

# Step 3: Fine-tune the model
echo "🎯 Starting fine-tuning (this will take several hours)..."
python finetune_unsloth.py

# Step 4: Create Ollama model
echo "🔄 Creating Ollama model..."
ollama create legal-expert -f Modelfile

# Step 5: Test the model
echo "✅ Testing fine-tuned model..."
ollama run legal-expert "Generate a short NDA between two companies"

echo "✨ Training complete! Update your .env file to use: OLLAMA_MODEL=legal-expert:latest"