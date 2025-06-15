import csv, random
from pathlib import Path
from collections import Counter
import pandas as pd, matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans

root = Path.cwd()
src  = root / "data" / "production" / "merged_ukr_dataset.tsv"
out  = root / "data" / f"cluster_stats_{src.stem}"
out.mkdir(parents=True, exist_ok=True)

df = (
    pd.read_csv(src, sep="\t", header=0, quoting=csv.QUOTE_NONE,
                on_bad_lines="skip", engine="python")[["English","Ukrainian"]]
    .dropna()
)

vec = TfidfVectorizer(max_features=40000, lowercase=True).fit_transform(df["English"])
svd = TruncatedSVD(n_components=50, random_state=42).fit_transform(vec)
k   = 10
km  = KMeans(n_clusters=k, random_state=42, n_init="auto").fit(svd)
df["cluster"] = km.labels_

df_len = df.assign(
    en_len=df.English.str.split().str.len(),
    ua_len=df.Ukrainian.str.split().str.len(),
    ratio=lambda d: d.en_len / d.ua_len.replace(0, pd.NA)
)

sizes = df_len["cluster"].value_counts().sort_index()
sizes.to_csv(out / "cluster_sizes.csv", header=["size"])

stats = (
    df_len.groupby("cluster")
          .agg(en_mean=("en_len","mean"),
               ua_mean=("ua_len","mean"),
               ratio_mean=("ratio","mean"),
               en_median=("en_len","median"),
               ua_median=("ua_len","median"),
               en_std=("en_len","std"),
               ua_std=("ua_len","std"),
               count=("en_len","size"))
)
stats.to_csv(out / "cluster_sentence_len.csv")

for cl in range(k):
    sub = df_len[df_len.cluster==cl]
    en_top = Counter(" ".join(sub.English).lower().split()).most_common(30)
    ua_top = Counter(" ".join(sub.Ukrainian).lower().split()).most_common(30)
    pd.DataFrame(en_top, columns=["token","freq"]).to_csv(out / f"en_top30_c{cl}.csv", index=False)
    pd.DataFrame(ua_top, columns=["token","freq"]).to_csv(out / f"ua_top30_c{cl}.csv", index=False)
    sub.sample(min(2000, len(sub))).to_csv(out / f"sample_c{cl}.tsv", sep="\t", index=False)

p2  = svd[:,:2]
idx = random.sample(range(len(p2)), k=min(15000, len(p2)))
plt.figure(figsize=(7,7))
plt.scatter(p2[idx,0], p2[idx,1], c=km.labels_[idx], s=5, alpha=0.6)
plt.xticks([]); plt.yticks([])
plt.tight_layout()
plt.savefig(out / "clusters_2d.png", dpi=300)
plt.close()
