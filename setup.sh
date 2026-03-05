#!/bin/bash

echo "🚀 LEGAL AGENT SETUP WITH FINE-TUNING"
echo "======================================"

# Step 1: Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install kagglehub transformers datasets accelerate torch

# Step 2: Download and prepare dataset
echo "📥 Downloading legal contract dataset..."
cd backend/train
python prepare_dataset.py

# Step 3: Create fine-tuned model with Ollama
echo "🎯 Creating fine-tuned legal model..."
ollama create legal-expert -f ./Modelfile

# Step 4: Test the model
echo "✅ Testing fine-tuned model..."
ollama run legal-expert "Generate a short NDA between two companies"

# Step 5: Update .env to use fine-tuned model
cd ..
echo "OLLAMA_MODEL=legal-expert:latest" >> .env

echo "✨ Setup complete! Run 'npm start' to start the agent"