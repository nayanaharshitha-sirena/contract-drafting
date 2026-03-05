import json
import torch
from unsloth import FastLanguageModel
from datasets import Dataset
from transformers import TrainingArguments
from trl import SFTTrainer
import os

print("🚀 STARTING LEGAL LLM FINE-TUNING")
print("="*50)

# Configuration
MODEL_NAME = "unsloth/llama-3-8b-bnb-4bit"  # You can change to smaller model if needed
MAX_SEQ_LENGTH = 4096
LORA_R = 16
BATCH_SIZE = 2
GRADIENT_ACCUMULATION = 4
LEARNING_RATE = 2e-4
NUM_EPOCHS = 3

# Check if training data exists
if not os.path.exists("training_data/train.json"):
    print("❌ Training data not found. Run prepare_legal_dataset.py first")
    exit(1)

# Load training data
print("\n📚 Loading training data...")
with open("training_data/train.json", 'r', encoding='utf-8') as f:
    train_data = json.load(f)

with open("training_data/val.json", 'r', encoding='utf-8') as f:
    val_data = json.load(f)

print(f"✅ Loaded {len(train_data)} training examples")
print(f"✅ Loaded {len(val_data)} validation examples")

# Format data for training
def format_for_training(examples):
    texts = []
    for ex in examples:
        messages = ex['messages']
        system = messages[0]['content']
        user = messages[1]['content']
        assistant = messages[2]['content']
        
        # Format with proper chat template
        text = f"<s>[INST] <<SYS>>\n{system}\n<</SYS>>\n\n{user} [/INST] {assistant} </s>"
        texts.append({"text": text})
    return texts

# Load model with Unsloth
print("\n🔄 Loading model...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=None,
    load_in_4bit=True,
)

# Add LoRA adapters
print("🔧 Adding LoRA adapters...")
model = FastLanguageModel.get_peft_model(
    model,
    r=LORA_R,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha=LORA_R * 2,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing=True,
)

# Prepare datasets
print("\n📝 Formatting datasets...")
train_formatted = format_for_training(train_data)
val_formatted = format_for_training(val_data[:50])  # Use subset for validation

train_dataset = Dataset.from_list(train_formatted)
val_dataset = Dataset.from_list(val_formatted)

print(f"✅ Train dataset size: {len(train_dataset)}")
print(f"✅ Validation dataset size: {len(val_dataset)}")

# Training arguments
training_args = TrainingArguments(
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRADIENT_ACCUMULATION,
    warmup_steps=100,
    num_train_epochs=NUM_EPOCHS,
    learning_rate=LEARNING_RATE,
    fp16=True,
    logging_steps=10,
    optim="adamw_8bit",
    weight_decay=0.01,
    lr_scheduler_type="linear",
    seed=42,
    output_dir="checkpoints",
    save_strategy="epoch",
    evaluation_strategy="steps",
    eval_steps=100,
    save_total_limit=2,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
)

# Create trainer
print("\n🎯 Initializing trainer...")
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    args=training_args,
)

# Train
print("\n🚀 Starting training...")
print("This will take several hours depending on your GPU\n")
trainer.train()

# Save the model
print("\n💾 Saving model...")
model.save_pretrained("legal_expert_final")
tokenizer.save_pretrained("legal_expert_final")

print("\n✅ Training complete!")
print(f"📁 Model saved to: legal_expert_final/")

# Convert to Ollama format
print("\n🔄 Converting to Ollama format...")

# Create Modelfile
modelfile = f"""FROM {MODEL_NAME}

PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER num_ctx 4096

TEMPLATE """
{{ .Prompt }}
"""

SYSTEM """
You are an expert legal document drafter trained on thousands of professional contracts. Generate complete, court-ready legal documents based on user requests.
"""

ADAPTER legal_expert_final
"""

with open("Modelfile", "w") as f:
    f.write(modelfile)

print("\n📝 Modelfile created")
print("\n🚀 To use with Ollama:")
print("1. ollama create legal-expert -f Modelfile")
print("2. ollama run legal-expert 'Generate an NDA between two companies'")
print("\n✨ All done!")
