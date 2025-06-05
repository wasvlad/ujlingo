import os
import torch
from datasets import load_dataset
import evaluate
from transformers import AutoModelForSeq2SeqLM, PreTrainedTokenizerFast

def main():

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)


    tokenizer_path = os.path.join(project_root, "data", "tokenizer", "tokenizer.json")
    model_dir     = os.path.join(project_root, "checkpoints", "scratch", "final")
    test_path     = os.path.join(project_root, "data", "splits10k", "test.csv")


    if not os.path.isfile(tokenizer_path):
        raise FileNotFoundError(f"Токенізатор не знайдено: {tokenizer_path}")
    if not os.path.isdir(model_dir):
        raise FileNotFoundError(f"Модель не знайдено: {model_dir}")


    tokenizer = PreTrainedTokenizerFast(
        tokenizer_file=tokenizer_path,
        bos_token="<s>", eos_token="</s>", pad_token="<pad>"
    )
    model = AutoModelForSeq2SeqLM.from_pretrained(model_dir)


    device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
    print("Using device:", device)
    model.to(device)


    ds = load_dataset("csv", data_files={"test": test_path})["test"]

    def generate_batch(batch):
        enc = tokenizer(
            batch["Ukrainian"],
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=128
        )
        input_ids = enc["input_ids"].to(device)
        attention_mask = enc["attention_mask"].to(device)
        outputs = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_length=128
        )
        return {"pred": tokenizer.batch_decode(outputs, skip_special_tokens=True)}

    results = ds.map(generate_batch, batched=True, batch_size=16)

    bleu = evaluate.load("sacrebleu")
    references = [[r] for r in results["English"]]
    score = bleu.compute(predictions=results["pred"], references=references)
    print(f"Test BLEU: {score['score']:.2f}")

if __name__ == "__main__":
    main()
