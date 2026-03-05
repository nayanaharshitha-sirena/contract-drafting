import os
import json
import random
from pathlib import Path

def scan_dataset(dataset_path):
    """Scan the dataset and return list of contract files"""
    contract_files = []
    
    print(f"📂 Scanning dataset at: {dataset_path}")
    
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            if file.endswith('.txt') or file.endswith('.json') or file.endswith('.pdf'):
                file_path = os.path.join(root, file)
                contract_files.append({
                    'path': file_path,
                    'name': file,
                    'size': os.path.getsize(file_path)
                })
    
    return contract_files

def extract_contract_type(filename, content_preview):
    """Use LLM to determine contract type"""
    # This is a simple classifier - in production, use a small model
    filename_lower = filename.lower()
    content_lower = content_preview.lower()
    
    if any(word in filename_lower or word in content_lower 
           for word in ['nda', 'confidential', 'non-disclosure', 'secrecy']):
        return 'nda'
    elif any(word in filename_lower or word in content_lower 
             for word in ['employ', 'job', 'worker', 'staff', 'hire', 'salary']):
        return 'employment'
    elif any(word in filename_lower or word in content_lower 
             for word in ['lease', 'rent', 'landlord', 'tenant', 'property']):
        return 'lease'
    elif any(word in filename_lower or word in content_lower 
             for word in ['service', 'consult', 'contractor', 'freelance']):
        return 'service'
    elif any(word in filename_lower or word in content_lower 
             for word in ['purchase', 'sale', 'buyer', 'seller', 'acquisition']):
        return 'purchase'
    elif any(word in filename_lower or word in content_lower 
             for word in ['partner', 'joint venture', 'partnership']):
        return 'partnership'
    elif any(word in filename_lower or word in content_lower 
             for word in ['loan', 'borrow', 'lender', 'promissory', 'debt']):
        return 'loan'
    elif any(word in filename_lower or word in content_lower 
             for word in ['license', 'licensing', 'ip', 'intellectual property']):
        return 'license'
    else:
        return 'general'

def create_training_examples(contract_files):
    """Create training examples from contract files"""
    training_data = []
    
    for i, file_info in enumerate(contract_files[:500]):  # Limit to 500 for now
        try:
            file_path = file_info['path']
            
            # Read file content (handle different encodings)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                except:
                    continue
            
            # Skip very small files
            if len(content) < 500:
                continue
            
            # Get first 1000 chars for type detection
            preview = content[:1000]
            
            # Determine contract type
            contract_type = extract_contract_type(file_info['name'], preview)
            
            # Create instruction based on type
            if contract_type == 'nda':
                instruction = "Generate a comprehensive Non-Disclosure Agreement"
            elif contract_type == 'employment':
                instruction = "Create a detailed Employment Agreement"
            elif contract_type == 'lease':
                instruction = "Draft a professional Lease Agreement"
            elif contract_type == 'service':
                instruction = "Generate a Service Agreement"
            elif contract_type == 'purchase':
                instruction = "Create a Purchase Agreement"
            elif contract_type == 'partnership':
                instruction = "Draft a Partnership Agreement"
            elif contract_type == 'loan':
                instruction = "Generate a Loan Agreement"
            elif contract_type == 'license':
                instruction = "Create a License Agreement"
            else:
                instruction = "Generate a legal contract"
            
            # Try to extract parties from first few lines
            lines = content.split('\n')[:10]
            parties_text = ' '.join(lines)
            if 'between' in parties_text.lower() and 'and' in parties_text.lower():
                instruction += " " + parties_text[:200]
            
            # Create training example in Llama format
            example = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert legal document drafter with 30 years of experience at top law firms. You create comprehensive, professionally formatted contracts that are court-ready and include all necessary clauses."
                    },
                    {
                        "role": "user",
                        "content": instruction
                    },
                    {
                        "role": "assistant",
                        "content": content
                    }
                ]
            }
            
            training_data.append(example)
            
            if (i + 1) % 50 == 0:
                print(f"✅ Processed {i + 1} contracts")
                
        except Exception as e:
            print(f"⚠️ Error processing {file_info['name']}: {e}")
            continue
    
    return training_data

def main():
    print("🚀 LEGAL CONTRACT DATASET PREPARATION")
    print("="*50)
    
    # Use your dataset path
    dataset_path = "/Users/nhreddy/Downloads/archive"
    
    # Scan for contract files
    print("\n🔍 Scanning for contract files...")
    contract_files = scan_dataset(dataset_path)
    
    print(f"\n📊 Found {len(contract_files)} potential contract files")
    
    if len(contract_files) == 0:
        print("❌ No contract files found in the dataset")
        return
    
    # Create training examples
    print("\n🔄 Creating training examples...")
    training_data = create_training_examples(contract_files)
    
    print(f"\n✅ Created {len(training_data)} training examples")
    
    # Split into train/validation
    random.shuffle(training_data)
    split_idx = int(len(training_data) * 0.9)
    train_data = training_data[:split_idx]
    val_data = training_data[split_idx:]
    
    # Save datasets
    output_dir = "training_data"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(f"{output_dir}/train.json", 'w', encoding='utf-8') as f:
        json.dump(train_data, f, indent=2, ensure_ascii=False)
    
    with open(f"{output_dir}/val.json", 'w', encoding='utf-8') as f:
        json.dump(val_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved training data to {output_dir}/")
    print(f"   - train.json: {len(train_data)} examples")
    print(f"   - val.json: {len(val_data)} examples")
    
    # Create a sample for inspection
    if len(training_data) > 0:
        with open(f"{output_dir}/sample.json", 'w', encoding='utf-8') as f:
            json.dump(training_data[:3], f, indent=2, ensure_ascii=False)
        print(f"\n📝 Sample saved to {output_dir}/sample.json")
    
    print("\n🚀 Next steps:")
    print("1. Install unsloth: pip install unsloth")
    print("2. Run fine-tuning: python finetune_with_dataset.py")

if __name__ == "__main__":
    main()
