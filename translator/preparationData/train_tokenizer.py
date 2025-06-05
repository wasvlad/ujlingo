"""
Script to train a Byte-Pair Encoding (BPE) tokenizer on the Ukrainian-English dataset,
then save the tokenizer and provide basic evaluation (vocab size, sample tokenization).
Assumes data splits10k are in `data/splits10k/train.csv` and `data/splits10k/validation.csv`.
"""

import os
import random
from tokenizers import Tokenizer, models, trainers, pre_tokenizers, processors
import pandas as pd


def train_tokenizer(
    train_file: str,
    vocab_size: int = 30000,
    special_tokens=None,
    output_dir: str = "data/tokenizer"
):
    """
    Train a BPE tokenizer on the combined Ukrainian and English text.
    """
    if special_tokens is None:
        special_tokens = ["<pad>", "<s>", "</s>", "<unk>", "<mask>"]

    df_train = pd.read_csv(train_file)
    if 'Ukrainian' not in df_train.columns or 'English' not in df_train.columns:
        raise ValueError("Train file must contain 'Ukrainian' and 'English' columns")

    iterator = (
        s for s in pd.concat([df_train['Ukrainian'], df_train['English']], axis=0).tolist()
    )

    tokenizer = Tokenizer(models.BPE())
    tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()
    trainer = trainers.BpeTrainer(vocab_size=vocab_size, special_tokens=special_tokens)
    tokenizer.train_from_iterator(iterator, trainer=trainer)

    tokenizer.post_processor = processors.TemplateProcessing(
        single="<s> $A </s>",
        pair="<s> $A </s> <s> $B </s>",
        special_tokens=[
            ("<s>", tokenizer.token_to_id("<s>")),
            ("</s>", tokenizer.token_to_id("</s>")),
        ],
    )

    os.makedirs(output_dir, exist_ok=True)
    tokenizer.save(os.path.join(output_dir, "tokenizer.json"))
    print(f"Tokenizer trained and saved to {output_dir}")

    return tokenizer


def evaluate_tokenizer(tokenizer: Tokenizer, sample_sentences: list, num_samples: int = 5):
    """
    Evaluate tokenizer by showing vocabulary size and encoding examples.
    """
    vocab_size = tokenizer.get_vocab_size()
    print(f"Vocabulary size: {vocab_size}")
    print(f"Showing tokenization for {num_samples} random samples:")

    for i, sent in enumerate(random.sample(sample_sentences, min(num_samples, len(sample_sentences)))):
        enc = tokenizer.encode(sent)
        print(f"\nSample {i+1}:")
        print(f"  Input: {sent}")
        print(f"  Tokens: {enc.tokens}")
        print(f"  IDs: {enc.ids}")

def compute_tokenization_stats(tokenizer, sentences):
    total_tokens = 0
    total_unk = 0
    lengths = []

    for sent in sentences:
        enc = tokenizer.encode(sent)
        tokens = enc.ids
        total_tokens += len(tokens)
        total_unk += tokens.count(tokenizer.token_to_id("<unk>"))
        lengths.append(len(tokens))

    unk_rate = total_unk / total_tokens if total_tokens > 0 else 0
    avg_len  = sum(lengths) / len(lengths) if lengths else 0

    print(f"Total sentences evaluated: {len(sentences)}")
    print(f"Total tokens: {total_tokens}")
    print(f"Unknown tokens: {total_unk} ({unk_rate:.2%})")
    print(f"Average tokens per sentence: {avg_len:.2f}")



if __name__ == "__main__":
    train_path = os.path.join(os.getcwd(), "data", "splits10k", "train.csv")
    val_path = os.path.join(os.getcwd(), "data", "splits10k", "validation.csv")

    tokenizer = train_tokenizer(train_path, vocab_size=30000, output_dir=os.path.join(os.getcwd(), "data", "tokenizer"))

    df_val = pd.read_csv(val_path)
    sentences = df_val['Ukrainian'].tolist() + df_val['English'].tolist()

    evaluate_tokenizer(tokenizer, sentences, num_samples=5)


    sentences = df_val['Ukrainian'].tolist() + df_val['English'].tolist()
    compute_tokenization_stats(tokenizer, sentences)

