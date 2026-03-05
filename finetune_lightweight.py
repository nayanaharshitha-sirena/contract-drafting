import json
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from datasets import Dataset
import torch

print("🚀 STARTING LIGHTWEIGHT FINE-TUNING")
print("="*50)

# Use a smaller model for Mac
MODEL_NAME = "microsoft/phi-2"  # Small, fast model

print(f"📚 Loading training data...")
with open("training_data/train.json", 'r') as f:
    train_data = json.load(f)

# Take a subset for faster training
train_data = train_data[:100]  # Start with 100 examples

# Format data
def format_data(examples):
    texts = []
    for ex in examples:
        system = ex['messages'][0]['content']
        user = ex['messages'][1]['content']
        assistant = ex['messages'][2]['content']
        
        # Simple formatting
        text = f"Instruction: {user}\n\nContract: {assistant}"
        texts.append({"text": text})
    return texts

formatted = format_data(train_data)
dataset = Dataset.from_list(formatted)

# Load tokenizer and model
print("🔄 Loading model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32,  # Use float32 for Mac
)

# Tokenize
def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=1024,
    )

print("📝 Tokenizing...")
tokenized_dataset = dataset.map(tokenize_function, batched=True)

# Training arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=1,
    per_device_train_batch_size=1,
    warmup_steps=10,
    logging_dir="./logs",
    logging_steps=5,
    save_strategy="epoch",
    learning_rate=2e-5,
    fp16=False,  # Disable fp16 for Mac
)

# Create trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)

# Train
print("🎯 Starting training...")
trainer.train()

# Save
model.save_pretrained("./legal_expert_mac")
tokenizer.save_pretrained("./legal_expert_mac")

print("\n✅ Training complete!")
print("📁 Model saved to ./legal_expert_mac/")
