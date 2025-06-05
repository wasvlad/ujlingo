"""
Script to train a Transformer-based seq2seq model from scratch on Ukrainian-English data.
Uses Hugging Face Transformers with a custom config (BART).
Assumes:
 - Tokenizer files available in `data/tokenizer/tokenizer.json`
 - Splits in `data/splits10k/{train,validation}.csv`
Saves model checkpoints to `checkpoints/scratch/`.
"""
import os
import torch
from datasets import load_dataset
import evaluate
from transformers import (
    BartConfig,
    AutoModelForSeq2SeqLM,
    PreTrainedTokenizerFast,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer
)


device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
print("Using device:", device)

def main():
    # Determine project root relative to this script (translator folder)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    tokenizer_path = os.path.join(project_root, "data", "tokenizer", "tokenizer.json")
    splits_dir = os.path.join(project_root, "data", "splits10k")
    output_dir = os.path.join(project_root, "checkpoints", "scratch")
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.isfile(tokenizer_path):
        raise FileNotFoundError(f"Tokenizer JSON not found at {tokenizer_path}")

    tokenizer = PreTrainedTokenizerFast(
        tokenizer_file=tokenizer_path,
        bos_token="<s>", eos_token="</s>", pad_token="<pad>"
    )

    data_files = {
        "train": os.path.join(splits_dir, "train.csv"),
        "validation": os.path.join(splits_dir, "validation.csv")
    }
    raw_datasets = load_dataset("csv", data_files=data_files)

    def tokenize_fn(examples):
        inputs = examples["Ukrainian"]
        targets = examples["English"]
        model_inputs = tokenizer(inputs, max_length=128, truncation=True)
        labels = tokenizer(text_target=targets, max_length=128, truncation=True)
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    tokenized = raw_datasets.map(
        tokenize_fn,
        batched=True,
        remove_columns=["Ukrainian", "English"]
    )

    config = BartConfig(
        vocab_size=tokenizer.vocab_size,
        d_model=512,
        encoder_layers=6,
        decoder_layers=6,
        encoder_attention_heads=8,
        decoder_attention_heads=8,
        encoder_ffn_dim=2048,
        decoder_ffn_dim=2048,
        max_position_embeddings=512,
        pad_token_id=tokenizer.pad_token_id,
        bos_token_id=tokenizer.bos_token_id,
        eos_token_id=tokenizer.eos_token_id
    )
    model = AutoModelForSeq2SeqLM.from_config(config)
    model.to(device)

    # Data collator
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding=True)

    # Training args
    training_args = Seq2SeqTrainingArguments(
        output_dir=output_dir,
        num_train_epochs=10,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        do_train=True,
        do_eval=True,
        logging_steps=100,
        eval_steps=1000,
        save_steps=1000,
        save_total_limit=3,
        learning_rate=5e-5,
        weight_decay=0.01,
        warmup_steps=500,
        predict_with_generate=True,
        logging_first_step=True
    )

    # BLEU metric
    bleu_metric = evaluate.load("sacrebleu")

    def compute_metrics(eval_pred):
        preds, labels = eval_pred
        decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
        labels = [[(l if l != -100 else tokenizer.pad_token_id) for l in label] for label in labels]
        decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
        result = bleu_metric.compute(predictions=decoded_preds, references=[[l] for l in decoded_labels])
        return {"bleu": result["score"]}

    # Trainer
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["validation"],
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics
    )

    trainer.train()
    trainer.save_model(os.path.join(output_dir, "final"))

if __name__ == "__main__":
    main()
