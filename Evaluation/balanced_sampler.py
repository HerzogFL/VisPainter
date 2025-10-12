#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
One-shot difficulty-balanced sampler (auto element_count, dataset-wise params)
"""

import json, random, argparse
from pathlib import Path
from typing import List

import pandas as pd
import numpy as np


# =========================================================
def balanced_sample(
    folder: Path,
    n: int,
    key: str = "element_count",
    default_bins: int = 5,
    seed: int = 42,
) -> List[str]:
    """
    Parameters
    ----------
    folder : Path          dataset directory containing 60 json files
    n      : int           how many samples to draw  (5–20, divides 60)
    key    : str           column name for difficulty score
    default_bins : int     default quantile bins for stratification
    seed   : int           random seed for reproducibility
    """
    rng = random.Random(seed)

    records = []
    for fp in folder.glob("*.json"):
        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            elem_cnt = len(data)
            meta = {key: elem_cnt}
        elif isinstance(data, dict):
            meta = data
            if key not in meta:
                meta[key] = len(meta.get("elements", []))
        else:
            raise ValueError(f"Unsupported JSON structure in {fp}")

        meta["__file"] = fp.name
        records.append(meta)

    df = pd.DataFrame(records)
    assert len(df) >= n, "n larger than dataset!"


    name_lower = str(folder).lower()
    is_ti2i = "ti2i" in name_lower          
    kappa   = 1.8  if is_ti2i else 1.0      # λ 
    eps_k   = 0.05 if is_ti2i else 0.10     # ε
    bins0   = 7    if is_ti2i else default_bins


    mu_pop    = df[key].mean()
    sigma_pop = df[key].std(ddof=0)
    lam = kappa * sigma_pop / (mu_pop + 1e-6)          
    eps = eps_k * sigma_pop * (20 / n)                

 
    df["bin"] = pd.qcut(df[key], q=bins0,
                        labels=False, duplicates="drop")
    actual_bins = len(df["bin"].unique())
    n_bins = min(bins0, n, actual_bins)               
    if n_bins != bins0:
        df["bin"] = pd.qcut(df[key], q=n_bins,
                            labels=False, duplicates="drop")

    per_bin = max(1, n // n_bins)                     
    rem     = n % n_bins
    chosen  = []

    for b in range(n_bins):
        idx = df.index[df["bin"] == b].tolist()
        rng.shuffle(idx)
        take = per_bin + (1 if b < rem else 0)
        chosen.extend(idx[:take])

    sub = df.loc[chosen]
    not_chosen = list(set(df.index) - set(chosen))

    def J(sdf: pd.DataFrame) -> float:
        return abs(sdf[key].mean() - mu_pop) + \
               lam * abs(sdf[key].std(ddof=0) - sigma_pop)

    for _ in range(3):                               
        improved = False
        while J(sub) > eps and not_chosen:
            out_idx = rng.choice(sub.index.tolist())
            in_idx  = rng.choice(not_chosen)
            new_sub = pd.concat([sub.drop(out_idx), df.loc[[in_idx]]])

            if J(new_sub) < J(sub):
                sub = new_sub
                not_chosen.remove(in_idx)
                not_chosen.append(out_idx)
                improved = True
            else:
                break
        if not improved:
            break

    return sub["__file"].tolist()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", type=str,
                        default="/T2I_GT",
                        help="dataset directory")
    parser.add_argument("-n", type=int, default=15,
                        help="samples per draw (5–20)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=str, default="picked_list.json")
    args = parser.parse_args()

    picks = balanced_sample(Path(args.folder), n=args.n, seed=args.seed)
    print(f"Picked {len(picks)} files:\n" + "\n".join(picks))

    json.dump(picks,
              open(args.out, "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    print("Saved list to", args.out)




# python balanced_sampler.py --folder GT/prompt-gt-t2i -n 15
# python balanced_sampler.py --folder GT/prompt-gt-ti2i -n 15