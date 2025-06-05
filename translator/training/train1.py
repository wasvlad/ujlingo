from datasets import load_dataset
from evaluate import load as load_metric
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Seq2SeqTrainingArguments, Seq2SeqTrainer

#  CSV  'uk_norm' і 'en_norm'
dataset = load_dataset(
    'csv', data_files={'data': 'ua_to_en_sentence_normalized.csv'}
)['data']

dataset = dataset.rename_column('uk_norm', 'uk').rename_column('en_norm', 'en')

split = dataset.train_test_split(test_size=0.1, seed=42)
train_dataset, eval_dataset = split['train'], split['test']

model_name = 'Helsinki-NLP/opus-mt-uk-en'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

max_input_length = 128
max_target_length = 128

def preprocess_function(batch):
    inputs = batch['uk']
    targets = batch['en']
    model_inputs = tokenizer(
        inputs,
        max_length=max_input_length,
        truncation=True,
        padding='max_length'
    )
    labels = tokenizer(
        targets,
        max_length=max_target_length,
        truncation=True,
        padding='max_length'
    )
    model_inputs['labels'] = labels['input_ids']
    return model_inputs

train_tokenized = train_dataset.map(
    preprocess_function,
    batched=True,
    remove_columns=['uk', 'en']
)
eval_tokenized = eval_dataset.map(
    preprocess_function,
    batched=True,
    remove_columns=['uk', 'en']
)

training_args = Seq2SeqTrainingArguments(
    output_dir='../results',
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    learning_rate=5e-5,
    weight_decay=0.01,
    save_total_limit=3,
    predict_with_generate=True
)

metric = load_metric('sacrebleu')

def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    decoded_preds = tokenizer.batch_decode(
        predictions, skip_special_tokens=True
    )
    labels = [
        [(l if l != -100 else tokenizer.pad_token_id) for l in lab]
        for lab in labels
    ]
    decoded_labels = tokenizer.batch_decode(
        labels, skip_special_tokens=True
    )
    result = metric.compute(
        predictions=decoded_preds,
        references=[[ref] for ref in decoded_labels]
    )
    result['bleu'] = result['score']
    return result

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_tokenized,
    eval_dataset=eval_tokenized,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

if __name__ == '__main__':
    trainer.train()
    trainer.save_model('uk_en_translation_model')
    print("Model fine-tuned and saved to ./uk_en_translation_model")
