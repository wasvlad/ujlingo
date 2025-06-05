import pandas as pd
from difflib import SequenceMatcher

df = pd.read_csv("/ujlingo/translator/data/production/ua_to_en_sentence_normalized2.csv")


df = df[(df.Ukrainian.str.split().str.len() > 1) & (df.English.str.split().str.len() > 1)]


df = df[(df.Ukrainian.str.split().str.len() < 100) & (df.English.str.split().str.len() < 100)]


df = df.drop_duplicates(subset=["Ukrainian","English"]).reset_index(drop=True)

#  near-duplicate filter (O(n²)
to_drop = set()
for i in range(len(df)):
    if i in to_drop: continue
    for j in range(i+1, len(df)):
        if j in to_drop: continue
        sim = SequenceMatcher(None, df.loc[i,"Ukrainian"], df.loc[j,"Ukrainian"]).ratio()
        if sim > 0.9:
            to_drop.add(j)
df = df.drop(index=list(to_drop)).reset_index(drop=True)
