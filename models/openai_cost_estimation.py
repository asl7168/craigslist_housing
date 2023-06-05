import jsonlines
from math import ceil 

prefix = "./json_files"

def round_up_1000s(n: int):
    return int(ceil(n / 1000.0)) * 1000

def ada_cost(n: int):
    return round((round_up_1000s(n) / 1000) * 0.0004, 2)

if __name__ == "__main__":
    s_tkn_ct = 0
    alt_s_tkn_ct = 0
    c_tkn_ct = 0
    alt_c_tkn_ct = 0

    for f in [f"{prefix}/seattle_train.jsonl", f"{prefix}/chicago_train.jsonl"]:
        seattle = "s" == f[0]
        with jsonlines.open(f) as reader:
            prompts = [d['prompt'] for d in [di for di in reader]]
            tokens = len([t for p in prompts for t in p.split()])
            alt_tokens = len([t for p in prompts for t in p.split(" ")])
            if seattle: s_tkn_ct = tokens; alt_s_tkn_ct = alt_tokens
            else: c_tkn_ct = tokens; alt_c_tkn_ct = alt_tokens

        print(f"{'Seattle' if seattle else 'Chicago'} Ada training will cost somewhere around " +
              f"between ${ada_cost(s_tkn_ct if seattle else c_tkn_ct)} and " + 
              f"${ada_cost(alt_s_tkn_ct if seattle else alt_c_tkn_ct)}")
