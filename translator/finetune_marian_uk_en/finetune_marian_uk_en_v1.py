from pathlib import Path
import torch
import numpy as np
import sacrebleu
from datasets import load_dataset
from evaluate import load as load_evaluate_metric
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    DataCollatorForSeq2Seq
)

root = Path.cwd()
data_dir = root / "data" / "splits_merged_ukr_dataset"
train_file = data_dir / "train.tsv"
valid_file = data_dir / "validation.tsv"
test_file = data_dir / "test.tsv"

datasets = load_dataset("csv", data_files={
    "train": str(train_file),
    "validation": str(valid_file),
    "test": str(test_file)
}, delimiter="\t")

model_name = "Helsinki-NLP/opus-mt-uk-en"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def preprocess_function(batch):
    model_inputs = tokenizer(batch["uk"], max_length=128, truncation=True)
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(batch["en"], max_length=128, truncation=True)
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

tokenized_datasets = datasets.map(
    preprocess_function,
    batched=True,
    remove_columns=["uk", "en"]
)

output_dir = root / "data" / "marian_finetuned_uk_en_v1"

training_args = Seq2SeqTrainingArguments(
    output_dir=str(output_dir),
    do_train=True,
    do_eval=True,
    eval_steps=1000,
    save_steps=2000,
    save_total_limit=2,
    logging_steps=100,
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    gradient_accumulation_steps=2,
    num_train_epochs=2,
    predict_with_generate=True,
    logging_dir=str(root / "data" / "logs"),
    optim="adamw_torch"
)

data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)
bleu_metric = load_evaluate_metric("sacrebleu")

def postprocess_text(preds, labels):
    preds = [pred.strip() for pred in preds]
    labels = [[label.strip()] for label in labels]
    return preds, labels

def compute_metrics(eval_preds):
    preds, labels = eval_preds
    if isinstance(preds, tuple):
        preds = preds[0]
    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
    decoded_preds, decoded_labels = postprocess_text(decoded_preds, decoded_labels)
    result = bleu_metric.compute(predictions=decoded_preds, references=decoded_labels)
    result = {"bleu": result["score"]}
    prediction_lens = [np.count_nonzero(pred != tokenizer.pad_token_id) for pred in preds]
    result["gen_len"] = float(np.mean(prediction_lens))
    return {k: round(v, 4) for k, v in result.items()}

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["validation"],
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics
)

trainer.train()
trainer.save_model(str(output_dir))

test_dataset = datasets["test"]
predictions = []
references = []

for i in range(0, len(test_dataset), 8):
    batch = test_dataset[i: i + 8]
    uk_sentences = batch["uk"]
    inputs = tokenizer(uk_sentences, return_tensors="pt", padding=True, truncation=True)
    if torch.backends.mps.is_available():
        inputs = {k: v.to("mps") for k, v in inputs.items()}
        model.to("mps")
    output_sequences = model.generate(**inputs, max_length=128)
    for seq in output_sequences:
        pred_text = tokenizer.decode(seq, skip_special_tokens=True)
        predictions.append(pred_text)
    references.extend(batch["en"])

bleu = sacrebleu.corpus_bleu(predictions, [references])
print(f"BLEU score on test set: {bleu.score:.2f}")
