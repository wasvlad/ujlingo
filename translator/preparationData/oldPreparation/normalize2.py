import pandas as pd
import re
import string


df = pd.read_csv("/ujlingo/translator/data/production/ua_to_en_sentence.csv")

#    Prepare a regex that matches any punctuation character
#    We include the standard ASCII punctuation plus common Ukrainian/English quotes and dashes.
punctuation_chars = string.punctuation + "«»“”—–…"
punct_re = re.compile(f"[{re.escape(punctuation_chars)}]")

def normalize_text(text: str) -> str:
    # Convert to string (in case of NaNs) and lowercase
    txt = str(text).lower()
    # Remove punctuation
    txt = punct_re.sub("", txt)
    # Collapse multiple whitespace into single space, and strip ends
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt

df["Ukrainian"] = df["Ukrainian"].apply(normalize_text)
df["English"]   = df["English"].apply(normalize_text)

# Save the normalized data back out
df.to_csv(
    "/Users/sn_mrk/PycharmProjects/ujlingo/ujlingo/translator/data/production/ua_to_en_sentence_normalized2.csv",
    index=False
)

print("Done! Your Ukrainian and English columns are now lowercase and punctuation-free.")
