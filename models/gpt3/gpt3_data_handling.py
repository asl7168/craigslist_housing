from cprint import cprint
import pandas as pd
from ast import literal_eval
import json 
from os import path 
from math import ceil, floor
import jsonlines 
import openai
from openai_credentials import skey, org 

openai.api_key = skey
openai.organization = org

max_upload_B = 150000000

def chunk_list(lst, n):
    sublist_size = ceil(len(lst) / n)
    return list(
        map(lambda x: lst[x * sublist_size:x * sublist_size + sublist_size],
        list(range(n)))
    )


def json_setup(city: str, bin: bool = False):
    cprint(f"Starting json setup for {city}, binning{' not' if not bin else ''} enabled", c="y")

    df = pd.read_csv(f"../../csv_no_duplicates/{city}_complete.csv")
    df = df[["posting_body", "price"]]  # only keep price (rent) and posting_body
    df = df.astype({"posting_body": "string", "price": "float"})

    df = df.loc[(df["price"] >= 500) & (df["price"] <= 6000)]

    df["posting_body"] = df["posting_body"].apply(lambda x: literal_eval(x))

    def prepare_body(body):
        return " ".join(body) + " -=>"  # turn list of strings into one string and add a unique suffix

    def prepare_price(price): 
        """
        The completion should start with a whitespace character (` `). This tends to produce better 
        results due to the tokenization we use. See 
        https://platform.openai.com/docs/guides/fine-tuning/preparing-your-dataset for more details
        """ 
        return " " + price 

    df = df.dropna()
    df["posting_body"] = df["posting_body"].apply(prepare_body)
    
    if not bin: 
        df["price"] = df["price"].apply(prepare_price)
        df = df.rename(columns={"posting_body": "prompt", "price": "completion"})
    else:
        max_price = df["price"].max()
        num_buckets = ceil(max_price / 500)
        buckets = [f" {i*500 if i == 0 else i*500 + 1}-{(i+1)*500}" for i in range(num_buckets)]
        
        def bin_price(price):
            # print(f"{floor(price / 500)} vs. {num_buckets} | price = {price} | max_price = {max_price}")
            b = floor(price / 500)
            return buckets[b if b < num_buckets else num_buckets - 1]

        df["binned_price"] = df["price"].apply(bin_price)
        df = df.rename(columns={"posting_body": "prompt", "binned_price": "completion"})
    
    
    output_df = df[["prompt", "completion"]]
    output_df = output_df.astype({"prompt": "string", "completion": "string"})
    
    train_df = output_df.sample(frac=0.8)
    train = train_df.to_dict(orient="records")
    test_df = output_df.drop(train_df.index)
    test = test_df.to_dict(orient="records")
    
    json_dir = "./json_files"

    filenames = [f"{json_dir}/{city}_train", f"{json_dir}/{city}_test"]
    for filename in filenames:
        with open(f"{filename}.jsonl", "w") as f:
            for entry in (train if "train" in filename else test):
                json.dump(entry, f)
                f.write("\n")

        filesize = path.getsize(f"{filename}.jsonl")
        if filesize > max_upload_B:  # if file size exceeds OpenAI max upload size of 150 MB, split the file
            num_files = ceil(filesize / max_upload_B)
            
            dicts = []
            with jsonlines.open(f"{filename}.jsonl", "r") as reader:
                dicts = [d for d in reader]
            
            chunked_dicts = chunk_list(dicts, num_files)
            for i in range(num_files):
                with open(f"{filename}_{i}.jsonl", "w") as f:
                    for entry in chunked_dicts[i]:
                        json.dump(entry, f)
                        f.write("\n")

    cprint(f"Completed json setup for {city}", c="g")


def completion_generation(city: str, model: str, n: int = 10, randomize: bool = True):
    # ENSURE TEST DATA IS GOOD, NOT TOO LONG, ETC. USING $ openai tools fine_tunes.prepare_data -f CITY_test.jsonl
    
    # to get a fine-tuned model name, openai.FineTune.list(), pick one of the fine-tunes, and use 
    # key "fine_tuned_model"
    
    # seattle is largest, and only has one test file, so don't need to possibly get multiple files afaik
    df = None 
    with jsonlines.open(f"./json_files/{city}_test.jsonl") as test_file:
        df = pd.DataFrame(test_file)

    df.rename(columns={"prompt": "prompt", "completion": "expected_completion"})

    results_df = df.loc[:n-1]
    if randomize: df = df.sample(frac=1)  # shuffle df, keeping old indices (for now; probably won't matter)

    results_df["actual_completion"] = "N/A" 

    for idx, row in results_df.iterrows():
        results_df.at[idx, "actual_completion"] = openai.Completion.create(model=model, 
                                                                           prompt=row["prompt"], 
                                                                           max_tokens=3, 
                                                                           temperature=0)["choices"][0]["text"]
    
    print(results_df)
    results_df.to_csv(f"./completions/{city}_{n}{'_random' if randomize else ''}_completions.csv")


if __name__ == "__main__":
    json_setup("seattle", True)
    json_setup("chicago", True)