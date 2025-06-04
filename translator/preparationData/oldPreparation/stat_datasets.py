#!/usr/bin/env python3
import csv, random
from pathlib import Path
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans

root        = Path.cwd()
src_tsv     = root / "data" / "production" / "merged_ukr_dataset.tsv"
out_dir     = root / "data" / f"stats_{src_tsv.stem}"
out_dir.mkdir(parents=True, exist_ok=True)

df = (
    pd.read_csv(
        src_tsv,
        sep="\t",
        header=0,
        quoting=csv.QUOTE_NONE,
        on_bad_lines="skip",
        engine="python",
    )[["English", "Ukrainian"]]
    .dropna()
)

ua_tok  = df["Ukrainian"].astype(str).str.split()
en_tok  = df["English"].astype(str).str.split()
ua_len  = ua_tok.map(len)
en_len  = en_tok.map(len)
len_rat = en_len / ua_len.replace(0, 1)

basic = pd.DataFrame(
    {
        "count": [ua_len.count(), en_len.count()],
        "mean": [ua_len.mean(), en_len.mean()],
        "median": [ua_len.median(), en_len.median()],
        "std": [ua_len.std(), en_len.std()],
        "min": [ua_len.min(), en_len.min()],
        "p1": [ua_len.quantile(0.01), en_len.quantile(0.01)],
        "p99": [ua_len.quantile(0.99), en_len.quantile(0.99)],
        "max": [ua_len.max(), en_len.max()],
    },
    index=["UA", "EN"],
)
basic.to_csv(out_dir / "length_stats.csv")

ratio_stats = len_rat.describe(percentiles=[0.01, 0.05, 0.95, 0.99]).to_frame(name="en_to_ua_ratio")
ratio_stats.to_csv(out_dir / "length_ratio_stats.csv")

dup_pairs = df.duplicated().sum()
dup_en    = df["English"].duplicated().sum()
dup_ua    = df["Ukrainian"].duplicated().sum()
pd.DataFrame(
    {"metric": ["pair_duplicates", "en_duplicates", "ua_duplicates"], "value": [dup_pairs, dup_en, dup_ua]}
).to_csv(out_dir / "duplicate_stats.csv", index=False)

ua_vocab = Counter(t.lower() for s in ua_tok for t in s)
en_vocab = Counter(t.lower() for s in en_tok for t in s)
vocab_df = pd.DataFrame(
    {
        "vocab_size": [len(ua_vocab), len(en_vocab)],
        "total_tokens": [sum(ua_vocab.values()), sum(en_vocab.values())],
        "type_token_ratio": [
            len(ua_vocab) / sum(ua_vocab.values()),
            len(en_vocab) / sum(en_vocab.values()),
        ],
    },
    index=["UA", "EN"],
)
vocab_df.to_csv(out_dir / "vocab_stats.csv")

ua_top = pd.DataFrame(ua_vocab.most_common(50), columns=["token", "freq"])
en_top = pd.DataFrame(en_vocab.most_common(50), columns=["token", "freq"])
ua_top.to_csv(out_dir / "ua_top50.csv", index=False)
en_top.to_csv(out_dir / "en_top50.csv", index=False)

plt.figure(figsize=(8, 5))
plt.hist([ua_len, en_len], bins=60, alpha=0.7, label=["UA", "EN"])
plt.yscale("log")
plt.xlabel("sentence length (tokens)")
plt.ylabel("count (log)")
plt.legend()
plt.tight_layout()
plt.savefig(out_dir / "length_hist.png", dpi=300)
plt.close()

plt.figure(figsize=(6, 6))
plt.scatter(en_len, ua_len, s=4, alpha=0.3)
plt.xscale("log")
plt.yscale("log")
plt.xlabel("EN len")
plt.ylabel("UA len")
plt.tight_layout()
plt.savefig(out_dir / "length_scatter.png", dpi=300)
plt.close()

plt.figure(figsize=(6, 4))
plt.hist(len_rat, bins=60, color="gray")
plt.xlabel("EN / UA length ratio")
plt.ylabel("count")
plt.tight_layout()
plt.savefig(out_dir / "length_ratio_hist.png", dpi=300)
plt.close()

vec = TfidfVectorizer(max_features=40000, lowercase=True, analyzer="word").fit_transform(df["English"].astype(str))
svd = TruncatedSVD(n_components=50, random_state=42).fit_transform(vec)
k    = min(20, max(2, int(len(df) ** 0.5 // 200)))
km   = KMeans(n_clusters=k, random_state=42, n_init="auto").fit(svd)
df["cluster"] = km.labels_
cluster_sizes = df["cluster"].value_counts().sort_index()
cluster_sizes.to_csv(out_dir / "cluster_sizes.csv", header=["size"])

p = svd[:, :2]
sample_idx = random.sample(range(len(p)), k=min(10000, len(p)))
plt.figure(figsize=(7, 7))
plt.scatter(p[sample_idx, 0], p[sample_idx, 1], c=km.labels_[sample_idx], s=5, alpha=0.6)
plt.xticks([]); plt.yticks([])
plt.tight_layout()
plt.savefig(out_dir / "cluster_scatter.png", dpi=300)
plt.close()
