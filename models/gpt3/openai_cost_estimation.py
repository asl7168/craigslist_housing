import jsonlines
import tiktoken
from cprint import cprint


def get_cost(city: str, models: str or list = "ada", dataset: str = "train"):
    models_list = [models] if type(models) == str else models
    
    encoding = tiktoken.get_encoding("r50k_base")  # used for all gpt3 models
    prompts = []
    completions = []

    with jsonlines.open(f"./rent/{city}/json_files/{city}_rent_{dataset}.jsonl") as reader:
        for d in reader:
            prompts.append(d["prompt"])
            completions.append(d["completion"])

    prompts_tokens = sum([len(encoding.encode(p)) for p in prompts])
    completions_tokens = sum([len(encoding.encode(c)) for c in completions])
    tokens = prompts_tokens + completions_tokens
    
    for model in models_list:
        fine_tune_1k_tkn_cost = -1
        completion_1k_tkn_cost = -1
        c = "w"

        if model == "ada":
            fine_tune_1k_tkn_cost = 0.0004
            completion_1k_tkn_cost = 0.0016
            c = "c"
        if model == "babbage":
            fine_tune_1k_tkn_cost = 0.0006
            completion_1k_tkn_cost = 0.0024
            c = "b"
        if model == "curie":
            fine_tune_1k_tkn_cost = 0.003
            completion_1k_tkn_cost = 0.012
            c = "m"
        elif model == "davinci":
            fine_tune_1k_tkn_cost = 0.03
            completion_1k_tkn_cost = 0.12
            c = "r"

        cost = (tokens / 1000) 

        if dataset == "train":
            cost *= fine_tune_1k_tkn_cost
            msg = f"{city} {model} training will cost ~${round(cost, 2)} per epoch (~${round(cost * 4, 2)} for default 4 epochs)"
        else:
            cost *= completion_1k_tkn_cost
            msg = f"{city} {model} {dataset} completion will cost ~${round(cost, 2)} (for all items)"

        cprint(msg, c=c)
        
    print()


if __name__ == "__main__":
    # get_cost("chicago", ["ada", "babbage", "curie", "davinci"])
    get_cost("seattle", ["ada", "babbage", "curie", "davinci"])
    get_cost("seattle", ["ada", "babbage", "curie"], "dev")
    get_cost("seattle", ["ada", "babbage", "curie"], "test")
