from cprint import cprint
import pandas as pd
from ast import literal_eval
import json 
from os import path, mkdir, listdir
from math import ceil
import jsonlines 
import openai
from openai_credentials import skey, org 
import tiktoken

openai.api_key = skey
openai.organization = org

tasks_and_cols = {"rent": "rent_class", "income": "income_class", "race": "race"}
sep_tk = " <SEP>\n"
max_upload_B = 150000000


def chunk_list(lst, n):
    sublist_size = ceil(len(lst) / n)
    return list(
        map(lambda x: lst[x * sublist_size:x * sublist_size + sublist_size],
        list(range(n)))
    )


def write_json_file(f: str, d: dict, n: int = None):
    filename = f"{f}{f'_{n}' if n else ''}"
    with open(f"{filename}.jsonl", "w") as f:
        for entry in d:
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


def json_setup(city: str, only_body: bool = True):
    """
    https://platform.openai.com/docs/guides/fine-tuning/preparing-your-dataset
    - Each prompt should end with a fixed separator to inform the model when the prompt ends and the 
      completion begins. A simple separator which generally works well is \n\n###\n\n. The separator 
      should not appear elsewhere in any prompt.
    - Each completion should start with a whitespace due to our tokenization, which tokenizes most words 
      with a preceding whitespace.
    - Each completion should end with a fixed stop sequence to inform the model when the completion ends. 
      A stop sequence could be \n, ###, or any other token that does not appear in any completion.
    """
    cprint(f"Started json setup for {city}", c="y")

    df = pd.read_csv(f"../../LLM_data/{city}_prepared.csv")
    
    prompt_fields = ["posting_body"] if only_body else ["posting_body", "title"]

    df["posting_body"] = df["posting_body"].apply(lambda x: literal_eval(x))
    df.dropna()  # shouldn't be any, but just in case
    
    def concat_body(body):
        return " ".join(body)  # turn list of strings into one string; TODO: fix this in text_processing
    
    df["posting_body"] = df["posting_body"].apply(concat_body)
    
    # TODO: don't actually do body token checking here; do it elsewhere
    encoding = tiktoken.get_encoding("r50k_base")  # remove prompts > 2048 tokens

    def tokenize_body(body):
        return len(encoding.encode(body))

    df["body_tokens"] = df["posting_body"].apply(tokenize_body)
    df = df.astype({"title": "string", "posting_body": "string", "rent_class": "string", 
                    "income_class": "string", "race": "string", "body_tokens": "int"})
    df = df[df["body_tokens"] <= 2048]

    for task in tasks_and_cols:
        cprint(f"    Making files for {task}", c="c")
        task_dir = f"./{task}"
        city_dir = f"{task_dir}/{city}"
        json_dir = f"{city_dir}/json_files"
        filenames = [f"{json_dir}/{city}_{task}_train", f"{json_dir}/{city}_{task}_test"]

        if not path.exists(task_dir): mkdir(task_dir)
        if not path.exists(city_dir): mkdir(city_dir)
        if not path.exists(json_dir): mkdir(json_dir)

        col = tasks_and_cols[task]
        
        for prompt_field in prompt_fields:
            cprint(f"        {prompt_field}", c="b")
            filenames = [f"{f}_TITLE" for f in filenames] if prompt_field == "title" else filenames 
            output_df = df[[prompt_field, col]]
            output_df = output_df.rename(columns={prompt_field: "prompt", col: "completion"})
            
            if task == "rent":
                output_df["prompt"] = output_df["prompt"] + " Is rent cheap, average, or expensive?"
            elif task == "income":
                output_df["prompt"] = output_df["prompt"] + " Is income low, average, or high?"
            elif task == "race":
                output_df["prompt"] = output_df["prompt"] + " Is this area white or nonwhite?" # TODO: make sure we're using nonwhite now

            output_df["prompt"] = output_df["prompt"] + sep_tk
            output_df["completion"] = " " + output_df["completion"] + " <STOP>"
        
            train_df = output_df.sample(frac=0.8)
            train = train_df.to_dict(orient="records")
            
            test_df = output_df.drop(train_df.index)
            test = test_df.to_dict(orient="records")
            
            for filename in filenames:
                write_json_file(filename, train if "train" in filename else test)
            
            cprint(f"        done", c="m")

        cprint(f"    done", c="m")

    cprint(f"Completed json setup for {city}\n", c="g")


def write_train_subfiles(city: str, task: str, train_nums: set, body_prompt: bool = True):
    if task not in tasks_and_cols:
        cprint("Please provide a valid task", c="r")
        return 
    
    original = f"./{task}/{city}/json_files/{city}_{task}_train"
    if not body_prompt: original += "_TITLE"

    dicts = []
    with jsonlines.open(f"{original}.jsonl") as reader:
            for d in reader:
                dicts.append(d)

    df = pd.DataFrame.from_records(dicts)
    temp_df = df.sample(max(train_nums))

    train_nums = list(train_nums)
    train_nums.sort(reverse=True)
    for tn in train_nums:
        temp_df = temp_df.sample(tn)
        print(f"Writing subfile with {tn} items")
        write_json_file(original, temp_df.to_dict(orient="records"), tn)


def upload_train_files(city: str):
    log_dir = "./training_logs"
    if not path.exists(log_dir): mkdir(log_dir)

    cprint(f"Uploading all train files for {city}", c="y")

    d = {}
    for task in tasks_and_cols:
        json_dir = f"./{task}/{city}/json_files"
        train_files = [f for f in listdir(json_dir) if "train" in f]
        d = d | {f:openai.File.create(file=open(f"{json_dir}/{f}"), purpose="fine-tune", 
                                      user_provided_filename=f)["id"] for f in train_files}
        
        cprint(f"    {city} {task} task upload done", c="c")
    
    with open(f"{log_dir}/{city}_train_files.json", "w") as logfile:
        json.dump(d, logfile, indent=2)

    cprint(f"Completed file upload for {city}\n", c="g")


def completion_generation(city: str, task: str, model: str, n: int = 10, randomize: bool = True):
    # ENSURE TEST DATA IS GOOD, NOT TOO LONG, ETC. USING $ openai tools fine_tunes.prepare_data -f CITY_test.jsonl
    
    # to get a fine-tuned model name, openai.FineTune.list(), pick one of the fine-tunes, and use 
    # key "fine_tuned_model"

    prefix = f"./{task}/{city}"
    json_dir = f"{prefix}/json_files"
    test_file = f"{json_dir}/{city}_{task}_test.jsonl"
    
    completions_dir = f"{prefix}/completions"
    if not path.exists(completions_dir): mkdir(completions_dir)
    
    df = None 
    with jsonlines.open(test_file) as f:
        df = pd.DataFrame(f)

    df.rename(columns={"prompt": "prompt", "completion": "expected_completion"})

    results_df = df.loc[:n-1]
    if randomize: df = df.sample(frac=1)  # shuffle df, keeping old indices (for now; probably won't matter)

    results_df["actual_completion"] = "N/A" 

    for idx, row in results_df.iterrows():
        results_df.at[idx, "actual_completion"] = openai.Completion.create(model=model, 
                                                                           prompt=row["prompt"], 
                                                                           max_tokens=5, # TODO: figure out new max  
                                                                           temperature=0)["choices"][0]["text"]
    
    print(results_df)
    results_df.to_csv(f"{completions_dir}/{city}_{n}{'_random' if randomize else ''}_completions.csv")

# TODO: some gpt4 completion maker. Ask Denis what our plan is with that and figure out how to get it going, etc.

if __name__ == "__main__":
    # ada_sizes = {100, 1000, 10000}
    # json_setup("chicago")
    # json_setup("seattle", only_body=False)
    # write_train_subfiles("seattle", "rent", ada_sizes)
    
    # upload_train_files("chicago")
    # upload_train_files("seattle")

    cprint("Nothing to do right now!", c="m")