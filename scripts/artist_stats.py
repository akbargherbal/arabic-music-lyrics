"""Per-artist statistics for the merged Arabic lyrics corpus.

Writes:
    data/processed/artist_stats.csv       # one row per artist string as stored
    data/processed/artist_stats_merged.csv  # "Name - Arabic alias" merged into "Name"

Counts cover only rows that have an artist; 381 tracks (3.1%) have none
(280 Egyptian excerpts + 101 Moroccan rows missing an artist upstream).
"""
import re
from pathlib import Path

import pandas as pd

CORPUS = Path("data/processed/arabic_lyrics.parquet")
OUT_RAW = Path("data/processed/artist_stats.csv")
OUT_MERGED = Path("data/processed/artist_stats_merged.csv")


def merge_alias(name: str) -> str:
    """'Wegz - ويجز' -> 'Wegz' (the Arabic part is an alias, not a collab)."""
    base = re.sub(r"\s+[-\u2013\u2014]\s*.*$", "", name)
    return re.sub(r"\s+", " ", base).strip()


def stats(df: pd.DataFrame, artist_col: str) -> pd.DataFrame:
    g = df.groupby(artist_col).agg(
        tracks=("title", "size"),
        chars=("n_chars", "sum"),
        median_chars=("n_chars", "median"),
        sources=("source", lambda s: ",".join(sorted(set(s)))),
        first_year=("year", "min"),
        last_year=("year", "max"),
        dialect=("dialect", lambda s: ",".join(sorted({x for x in s.dropna()}))or None),
    ).reset_index()
    g["median_chars"] = g["median_chars"].round(0).astype("Int64")
    return g.sort_values(["tracks", "chars"], ascending=False).reset_index(drop=True)


def main() -> None:
    df = pd.read_parquet(CORPUS)
    df = df[df["artist"].fillna("") != ""].copy()

    raw = stats(df, "artist").rename(columns={"artist": "artist"})
    raw.to_csv(OUT_RAW, index=False)

    df["artist_merged"] = df["artist"].map(merge_alias)
    merged = stats(df, "artist_merged").rename(columns={"artist_merged": "artist"})
    merged.to_csv(OUT_MERGED, index=False)

    print(f"raw artist strings : {len(raw):,}")
    print(f"merged artists     : {len(merged):,}")
    print(f"tracks with artist : {len(df):,} / 12,463")
    print(f"median tracks/artist: {raw.tracks.median():.0f}")
    print(f"artists with 1 track: {(raw.tracks == 1).sum():,} "
          f"({(raw.tracks == 1).mean()*100:.0f}%)")
    print(f"artists with >=10   : {(raw.tracks >= 10).sum():,}")
    print(f"top 10 share        : {raw.tracks.head(10).sum()/raw.tracks.sum()*100:.1f}%")
    print("\ntop 25 merged artists:")
    print(merged.head(25).to_string(index=False))


if __name__ == "__main__":
    main()
