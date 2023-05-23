import pandas as pd
from ast import literal_eval
import json 
from openai_credentials import skey

def json_setup(city: str):
    df = pd.read_csv(f"./csv_no_duplicates/{city}_complete.csv")
    df = df[["price", "posting_body"]]  # only keep price (rent) and posting_body
    
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
    
    df["posting_body"] = df["posting_body"].apply(prepare_body)
    df = df.astype({"price": "string","posting_body": "string"})
    df["price"] = df["price"].apply(prepare_price)

    df = df.rename(columns={"price": "completion", "posting_body": "prompt"})
    df = df.reindex(columns=["prompt", "completion"])  # swap column ordering to fit OpenAI preferred format
    df = df.dropna()
    
    train_df = df.sample(frac=0.8)
    train = train_df.to_dict(orient="records")
    test_df = df.drop(train_df.index)
    test = test_df.to_dict(orient="records")
    
    json_dir = "./json_files"

    for filename in [f"{json_dir}/{city}_train.jsonl", f"{json_dir}/{city}_test.jsonl"]:
        with open(filename, "w") as f:
            for entry in (train if "train" in filename else test):
                json.dump(entry, f)
                f.write("\n")

if __name__ == "__main__":
    json_setup("seattle")
    json_setup("chicago")