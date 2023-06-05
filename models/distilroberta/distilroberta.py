# code adapted from https://towardsdatascience.com/how-to-fine-tune-an-nlp-regression-model-with-transformers-and-huggingface-94b2ed6f798f

from os import getcwd, mkdir
from os.path import exists

p = "./"
if "p31502" in getcwd(): p = "/projects/p31502/projects/craigslist/"

import sys
sys.path.append(p)

from cprint import cprint
import pandas as pd
from ast import literal_eval
from transformers import AutoTokenizer, RobertaForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset, load_from_disk
from sklearn.metrics import mean_squared_error


def setup_dirs(city: str):
    city_root = f"./{city}"

    if not exists(city_root): mkdir(f"./{city}")
    if not exists(f"{city_root}/datasets"): mkdir(f"./{city}/datasets")
    if not exists(f"{city_root}/tokenizer"): mkdir(f"./{city}/tokenizer")
    if not exists(f"{city_root}/train_output"): mkdir(f"./{city}/train_output")
    if not exists(f"{city_root}/model"): mkdir(f"./{city}/model")


def prep_data(city: str):
    cprint("Prepping Data", c="c")

    setup_dirs(city)
    
    df = pd.read_csv(f"../../csv_no_duplicates/{city}_complete.csv")
    df = df[["posting_body", "price"]]
    
    # we should definitely make this not have to be a step by bulk fixing at some point
    df["posting_body"] = df["posting_body"].apply(lambda x: literal_eval(x))

    def fix_body(body): 
        return " ".join(body)
    
    df["posting_body"] = df["posting_body"].apply(fix_body)
    df = df.dropna()
    df.rename(columns={"posting_body": "text", "price": "label"})

    ds = Dataset.from_pandas(df, preserve_index=False)
    ds = ds.train_test_split(test_size=0.2)
    ds.save_to_disk(f"./{city}/datasets/{city}.dataset")

    cprint("Prepping Complete", c="c")


def tokenize_data(city: str):
    cprint("Tokenizing Data", c="m")
    
    setup_dirs(city)

    ds_path = f"./{city}/datasets/{city}.dataset"
    if not exists(ds_path): prep_data(city)

    ds = load_from_disk(ds_path)
    tokenizer = AutoTokenizer.from_pretrained("distilroberta-base")

    def tokenize_function(examples): 
        return tokenizer(examples["posting_body"], padding="max_length", truncation=True) # not preferable, but seems necessary
    
    tokenized_ds = ds.map(tokenize_function, batched=True)
    tokenized_ds.save_to_disk(f"./{city}/datasets/{city}_tokenized.dataset")

    tokenizer.save_pretrained(f"./{city}/tokenizer/")
    # could probably add a final step here to remove the non-tokenized dataset, but for now don't do

    cprint("Tokenizing Complete", c="m")
    return tokenized_ds


def train(city: str):
    cprint("TRAINING START", c="y")

    setup_dirs(city)
    tokenized_ds = tokenize_data(city)

    # tokenized_ds = load_from_disk(f"./dataset_files/{city}_tokenized.dataset")
    tokenizer = AutoTokenizer.from_pretrained(f"./{city}/tokenizer/")
    model = RobertaForSequenceClassification.from_pretrained("distilroberta-base", num_labels=1)
    model.resize_token_embeddings(len(tokenizer))

    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        rmse = mean_squared_error(labels, predictions, squared=False)
        return {"rmse": rmse}
    
    # unsure if the two per_device batch sizes are optimal, but this was in the tutorial
    # increased save_total_limit from tutorial (2) to 8, just for safety
    training_args = TrainingArguments(output_dir=f"./{city}/train_output", logging_strategy="epoch", 
                                      evaluation_strategy="epoch", per_device_train_batch_size=16,
                                      per_device_eval_batch_size=16, num_train_epochs=3, save_total_limit=8,
                                      save_strategy="no", load_best_model_at_end=False)
    
    trainer = Trainer(model=model, args=training_args, train_dataset=tokenized_ds["train"], 
                      eval_dataset=tokenized_ds["test"], compute_metrics=compute_metrics)
    trainer.train()

    trainer.save_model(f"./{city}/trainer_model") # not sure which of these ways is more correct, so check both
    model.save_pretrained(f"./{city}/model")

    cprint("TRAINING COMPLETE", c="g")


if __name__ == "__main__":
    city = sys.argv[1]
    train(city)
    

"""TODO: ADAPT THIS TESTING CODE (EASY ENOUGH)
from transformers import Trainer
trainer = Trainer(model=model)
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True) 
def pipeline_prediction(text):
    df=pd.DataFrame({'text':[text]})
    dataset = Dataset.from_pandas(df,preserve_index=False) 
    tokenized_datasets = dataset.map(tokenize_function)
    raw_pred, _, _ = trainer.predict(tokenized_datasets) 
    return(raw_pred[0][0])
    pipeline_prediction("🚨 Get 50% now!")
"""
