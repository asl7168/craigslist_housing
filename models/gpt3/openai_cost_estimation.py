import jsonlines
import tiktoken
from cprint import cprint


def get_cost(city: str, models: str or list = "ada"):
    models_list = [models] if type(models) == str else models
    
    encoding = tiktoken.get_encoding("r50k_base")  # used for all gpt3 models
    prompts = []
    completions = []

    with jsonlines.open(f"./rent/{city}/json_files/{city}_rent_train.jsonl") as reader:
        for d in reader:
            prompts.append(d["prompt"])
            completions.append(d["completion"])

    prompts_tokens = sum([len(encoding.encode(p)) for p in prompts])
    completions_tokens = sum([len(encoding.encode(c)) for c in completions])
    tokens = prompts_tokens + completions_tokens
    
    for model in models_list:
        cost_per_1k_token = -1
        c = "w"

        if model == "ada":
            cost_per_1k_token = 0.0004
            c = "c"
        elif model == "davinci":
            cost_per_1k_token = 0.03
            c = "r"

        cost = (tokens / 1000) * cost_per_1k_token

        cprint(f"{city} {model} training will cost ~${round(cost, 2)} per epoch " +
               f"(~${round(cost * 4, 2)} for default 4 epochs)", c=c)
        
    print()


if __name__ == "__main__":
    # get_cost("chicago", ["ada", "davinci"])
    get_cost("seattle", ["ada", "davinci"])
