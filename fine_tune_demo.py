"""
CCPA Model Fine-Tuning Script (Demo)

This script demonstrates how to fine-tune DistilBERT on CCPA violation data.
For hackathon: Shows capability without full training time.
For production: Run with full dataset and training epochs.
"""

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from torch.utils.data import Dataset
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Sample CCPA training data (expanded for better coverage)
TRAINING_DATA = [
    # Section 1798.100 - Notice violations (label=1)
    {"text": "We sell user data to advertisers without informing users", "label": 1},
    {"text": "We collect personal information without notice", "label": 1},
    {"text": "Data collection happens automatically without disclosure", "label": 1},
    {"text": "We gather consumer data secretly", "label": 1},
    {"text": "Personal information is collected without informing consumers", "label": 1},
    {"text": "We don't tell users what data we collect", "label": 1},
    {"text": "Data is obtained without consumer knowledge", "label": 1},
    {"text": "We collect information without prior notification", "label": 1},
    
    # Section 1798.105 - Deletion violations (label=1)
    {"text": "We refuse to delete user data when requested", "label": 1},
    {"text": "We ignore deletion requests from consumers", "label": 1},
    {"text": "User data is kept forever even after deletion requests", "label": 1},
    {"text": "We don't delete data when users ask", "label": 1},
    {"text": "Deletion requests are denied", "label": 1},
    {"text": "We retain all data permanently regardless of requests", "label": 1},
    {"text": "Consumer data is archived indefinitely even after removal requests", "label": 1},
    {"text": "We keep information forever even when users request deletion", "label": 1},
    {"text": "Data is stored permanently despite deletion requests", "label": 1},
    {"text": "We never delete user information when asked", "label": 1},
    
    # Section 1798.106 - Correction violations (label=1)
    {"text": "We deny requests to correct inaccurate information", "label": 1},
    {"text": "Users cannot correct their personal data", "label": 1},
    {"text": "We refuse to fix incorrect information", "label": 1},
    {"text": "Correction requests are ignored", "label": 1},
    
    # Section 1798.120 - Opt-out violations (label=1)
    {"text": "Users cannot opt out of data sales", "label": 1},
    {"text": "We don't allow opting out of data sharing", "label": 1},
    {"text": "Opt-out is not available for consumers", "label": 1},
    {"text": "We make it extremely difficult to opt out", "label": 1},
    {"text": "The opt-out process is very complicated", "label": 1},
    {"text": "There is no way to stop data sales", "label": 1},
    {"text": "We sell data without opt-out option", "label": 1},
    
    # Section 1798.121 - Sensitive data violations (label=1)
    {"text": "We sell personal data of minors without consent", "label": 1},
    {"text": "We share sensitive information of users under 16", "label": 1},
    {"text": "Children's data is sold to third parties", "label": 1},
    {"text": "We sell geolocation data without permission", "label": 1},
    
    # Section 1798.125 - Discrimination violations (label=1)
    {"text": "We charge higher prices to users who opt out", "label": 1},
    {"text": "Users who exercise privacy rights pay more", "label": 1},
    {"text": "We discriminate against consumers who opt out", "label": 1},
    {"text": "Premium users get better service if they don't opt out", "label": 1},
    {"text": "We penalize users for exercising privacy rights", "label": 1},
    
    # Section 1798.130 - Response violations (label=1)
    {"text": "We never respond to consumer privacy requests", "label": 1},
    {"text": "We ignore all privacy requests", "label": 1},
    {"text": "Consumer requests are not answered", "label": 1},
    {"text": "We don't respond to data requests", "label": 1},
    {"text": "Privacy requests take months to process", "label": 1},
    
    # Section 1798.135 - Do Not Sell link violations (label=1)
    {"text": "Our website has no Do Not Sell link", "label": 1},
    {"text": "There is no Do Not Sell My Personal Information option", "label": 1},
    {"text": "We don't have an opt-out link on our site", "label": 1},
    
    # Safe practices (label=0)
    {"text": "We provide clear privacy notices before collecting data", "label": 0},
    {"text": "We honor all deletion requests within 45 days", "label": 0},
    {"text": "Users can easily opt out of data sales", "label": 0},
    {"text": "We do not discriminate against users who exercise privacy rights", "label": 0},
    {"text": "Our website has a prominent Do Not Sell My Personal Information link", "label": 0},
    {"text": "We respond to all consumer requests promptly", "label": 0},
    {"text": "We allow users to correct their personal information", "label": 0},
    {"text": "We obtain parental consent before collecting data from minors", "label": 0},
    {"text": "We disclose all data collection practices in our privacy policy", "label": 0},
    {"text": "We provide free opt-out mechanisms for all users", "label": 0},
    {"text": "Users can delete their accounts and all associated data", "label": 0},
    {"text": "We inform consumers about data collection before it happens", "label": 0},
    {"text": "Privacy rights are easy to exercise on our platform", "label": 0},
    {"text": "We respect all consumer privacy choices", "label": 0},
    {"text": "Data deletion is simple and fast", "label": 0},
    {"text": "We don't sell personal information", "label": 0},
    {"text": "Consumer data is protected and not shared", "label": 0},
    {"text": "We comply with all CCPA requirements", "label": 0},
    {"text": "Privacy is our top priority", "label": 0},
    {"text": "We give users full control over their data", "label": 0},
]


class CCPADataset(Dataset):
    """PyTorch Dataset for CCPA violation detection"""
    
    def __init__(self, data, tokenizer, max_length=128):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        encoding = self.tokenizer(
            item["text"],
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )
        
        return {
            "input_ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten(),
            "labels": torch.tensor(item["label"], dtype=torch.long)
        }


def fine_tune_model(epochs=1, output_dir="./ccpa_model"):
    """
    Fine-tune DistilBERT on CCPA violation data
    
    Args:
        epochs: Number of training epochs (use 1 for demo, 3-5 for production)
        output_dir: Where to save the fine-tuned model
    """
    logger.info("Starting CCPA model fine-tuning...")
    
    # Load base model and tokenizer
    model_name = "distilbert-base-uncased"
    logger.info(f"Loading base model: {model_name}")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=2  # harmful vs not harmful
    )
    
    # Create dataset
    logger.info(f"Creating dataset with {len(TRAINING_DATA)} examples")
    train_dataset = CCPADataset(TRAINING_DATA, tokenizer)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=4,
        warmup_steps=10,
        weight_decay=0.01,
        logging_dir="./logs",
        logging_steps=5,
        save_strategy="epoch",
        eval_strategy="no",  # Fixed: was evaluation_strategy
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
    )
    
    # Train
    logger.info("Training model...")
    trainer.train()
    
    # Save
    logger.info(f"Saving fine-tuned model to {output_dir}")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    logger.info("Fine-tuning complete!")
    logger.info(f"To use: Update model_name in app/model.py to '{output_dir}'")
    
    return model, tokenizer


def test_fine_tuned_model(model_path="./ccpa_model"):
    """Test the fine-tuned model on sample inputs"""
    logger.info(f"Loading fine-tuned model from {model_path}")
    
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    model.eval()
    
    # Test cases
    test_cases = [
        "We sell user data without consent",
        "We provide clear privacy notices",
        "We ignore deletion requests",
        "We honor all user privacy rights"
    ]
    
    logger.info("\nTesting fine-tuned model:")
    for text in test_cases:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1)
            harmful_prob = probs[0][1].item()
            
        logger.info(f"Text: {text[:50]}...")
        logger.info(f"Harmful probability: {harmful_prob:.3f}")
        logger.info(f"Prediction: {'VIOLATION' if harmful_prob > 0.5 else 'SAFE'}\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fine-tune CCPA violation detection model")
    parser.add_argument("--epochs", type=int, default=1, help="Number of training epochs")
    parser.add_argument("--output", type=str, default="./ccpa_model", help="Output directory")
    parser.add_argument("--test-only", action="store_true", help="Only test existing model")
    
    args = parser.parse_args()
    
    if args.test_only:
        test_fine_tuned_model(args.output)
    else:
        # Fine-tune
        model, tokenizer = fine_tune_model(epochs=args.epochs, output_dir=args.output)
        
        # Test
        logger.info("\n" + "="*50)
        test_fine_tuned_model(args.output)
        
        logger.info("\n" + "="*50)
        logger.info("NEXT STEPS:")
        logger.info("1. Update app/model.py line 35:")
        logger.info(f"   model_name = '{args.output}'")
        logger.info("2. Restart server")
        logger.info("3. Model will now use fine-tuned weights!")
