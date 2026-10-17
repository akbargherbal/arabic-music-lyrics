"""Merge every shortlisted Arabic-lyrics source into one normalized corpus.

Sources
-------
genius           data/processed/genius_arabic.parquet    (Kaggle 12M-song dump filtered to Arabic)
arabic_hiphop    data/raw/arabic_rap2.csv                (Kaggle, Arabic rap)
moroccan_lyrics  data/raw/moroccan_lyrics/lyrics.csv     (HF, Darija)
egyptian_songs   data/raw/egyptian-songs/data/*.parquet  (HF, line-level, aggregated per song)
spotify_960k     data/processed/spotify960k_arabic.parquet (Kaggle, script-filtered + langdetect)

Output
------
data/processed/arabic_lyrics.parquet
data/processed/arabic_lyrics_stats.json
data/processed/arabic_lyrics_sample.csv
"""
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd
from langdetect import DetectorFactory, detect

DetectorFactory.seed = 0

ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")
PERSIAN_RE = re.compile(r"[\u067E\u0686\u0698\u06AF]")
URDU_RE = re.compile(r"[\u0679\u0688\u0691\u06BA\u06D2\u06BE]")
KURDISH_RE = re.compile(r"[\u06A4\u06CE\u06C6\u0695\u06B5]")

OUT = Path("data/processed/arabic_lyrics.parquet")


def clean(text) -> str:
    if not isinstance(text, str):
        return ""
    text = text.replace("\\n", "\n").replace("\\r", "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def ar_ratio(text: str) -> float:
    chars = [c for c in text if not c.isspace()]
    if not chars:
        return 0.0
    return len(ARABIC_RE.findall("".join(chars))) / len(chars)


def marker_ratio(text: str, pattern: re.Pattern) -> float:
    if not text:
        return 0.0
    return len(pattern.findall(text)) / len(text)


def script_class(ratio: float) -> str:
    if ratio >= 0.55:
        return "arabic"
    if ratio >= 0.10:
        return "mixed"
    return "latin/arabizi"


def norm_key(title: str, artist: str) -> str:
    s = f"{title} {artist}".lower()
    s = unicodedata.normalize("NFKD", s)
    s = re.sub(r"[^\w\u0600-\u06FF]+", " ", s)
    s = re.sub(r"\b(feat|ft|featuring)\b.*$", "", s)
    return re.sub(r"\s+", " ", s).strip()


def safe_detect(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "err"


def strip_spotify_artists(value: str) -> str:
    s = str(value or "")
    s = re.sub(r'^\[|\]$', "", s.strip())
    s = s.replace('"', "").replace("'", "")
    return s.strip()


def load_genius() -> tuple[pd.DataFrame, dict]:
    df = pd.read_parquet("data/processed/genius_arabic.parquet")
    dropped = {}

    artist = df["artist"].fillna("")
    title = df["title"].fillna("")
    # Non-music entries sit in the 'misc' tag: Quran recitations, Ibn Khaldoun's
    # Muqaddima, Genius Arabia list articles.
    non_music = artist.str.contains(
        r"Al-Quran|Ibn Khaldoun|Genius Arabia|Arabic Translations", case=False
    ) | title.str.match(r"^(Al Muqaddima|AL-|AS-|AN-)")
    dropped["non_music"] = int(non_music.sum())
    df = df[~non_music].copy()

    # Persian/Urdu/Kurdish songs that script detection mistook for Arabic.
    script_rows = df["matched_by"] == "script"
    persian = df["lyrics"].map(lambda t: marker_ratio(t, PERSIAN_RE)) > 0.005
    urdu = df["lyrics"].map(lambda t: marker_ratio(t, URDU_RE)) > 0.005
    kurdish = df["lyrics"].map(lambda t: marker_ratio(t, KURDISH_RE)) > 0.010
    other = script_rows & (persian | urdu | kurdish)
    dropped["other_language"] = int(other.sum())
    df = df[~other].copy()

    year = pd.to_numeric(df["year"], errors="coerce")
    year = year.where(year >= 1900)

    out = pd.DataFrame({
        "source": "genius",
        "source_id": df["id"].astype(str),
        "source_url": None,
        "title": df["title"].map(clean),
        "artist": df["artist"].map(clean),
        "artist_origin": None,
        "album": None,
        "year": year.astype("Int64"),
        "genre": df["tag"],
        "dialect": None,
        "language_variant": "ar",
        "lyrics": df["lyrics"].map(clean),
        "translation": None,
        "views": pd.to_numeric(df["views"], errors="coerce").astype("Int64"),
        "matched_by": df["matched_by"],
        "lyrics_completeness": "full",
    })
    return out, dropped


def load_hiphop() -> pd.DataFrame:
    df = pd.read_csv("data/raw/arabic_rap2.csv")
    return pd.DataFrame({
        "source": "arabic_hiphop",
        "source_id": df["url"],
        "source_url": df["url"],
        "title": df["song_name"].map(clean),
        "artist": df["author"].map(clean),
        "artist_origin": df["author_origin"],
        "album": None,
        "year": pd.Series([pd.NA] * len(df), dtype="Int64"),
        "genre": "rap",
        "dialect": None,
        "language_variant": "ar",
        "lyrics": df["lyrics"].map(clean),
        "translation": None,
        "views": pd.Series([pd.NA] * len(df), dtype="Int64"),
        "matched_by": "curated",
        "lyrics_completeness": "full",
    })


def load_moroccan() -> pd.DataFrame:
    df = pd.read_csv("data/raw/moroccan_lyrics/lyrics.csv")
    return pd.DataFrame({
        "source": "moroccan_lyrics",
        "source_id": df["url"],
        "source_url": df["url"],
        "title": df["title"].map(clean),
        "artist": df["artist_name"].map(clean),
        "artist_origin": "Morocco",
        "album": None,
        "year": pd.Series([pd.NA] * len(df), dtype="Int64"),
        "genre": None,
        "dialect": "moroccan_darija",
        "language_variant": "ar_MA",
        "lyrics": df["lyrics"].map(clean),
        "translation": None,
        "views": pd.Series([pd.NA] * len(df), dtype="Int64"),
        "matched_by": "curated",
        "lyrics_completeness": "full",
    })


def load_egyptian() -> pd.DataFrame:
    files = sorted(Path("data/raw/egyptian-songs/data").glob("*.parquet"))
    df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    df["line_no"] = df.groupby("song_id").cumcount()
    df = df.sort_values(["song_id", "line_no"])

    def join_lines(s: pd.Series) -> str:
        return clean("\n".join(x for x in s if isinstance(x, str) and x.strip()))

    g = df.groupby("song_id", sort=False)
    return pd.DataFrame({
        "source": "egyptian_songs",
        "source_id": g["id"].first(),
        "source_url": None,
        "title": g["song_name"].first().map(clean),
        "artist": None,  # dataset has no artist column
        "artist_origin": "Egypt",
        "album": g["album_name"].first(),
        "year": pd.to_numeric(g["year"].first(), errors="coerce").astype("Int64"),
        "genre": g["genre"].first(),
        "dialect": g["dialect"].first(),
        "language_variant": g["language_variant"].first(),
        "lyrics": g["arabic"].apply(join_lines),
        "translation": g["english"].apply(join_lines),
        "views": pd.Series([pd.NA] * g.ngroups, dtype="Int64"),
        "matched_by": "curated",
        "lyrics_completeness": "excerpt (verse/chorus lines only)",
    }).reset_index(drop=True)


def load_spotify960k() -> tuple[pd.DataFrame, dict]:
    df = pd.read_parquet("data/processed/spotify960k_arabic.parquet")
    # The dump mixes Persian and Urdu (same script). Keep Arabic only.
    langs = df["lyrics"].map(lambda t: safe_detect(t) if len(t) >= 20 else "err")
    keep = langs == "ar"
    dropped = {
        "language": {k: int(v) for k, v in langs.value_counts().items()},
        "dropped_non_arabic": int((~keep).sum()),
    }
    df = df[keep].copy()
    return pd.DataFrame({
        "source": "spotify_960k",
        "source_id": df["id"].astype(str),
        "source_url": None,
        "title": df["name"].map(clean),
        "artist": df["artists"].map(strip_spotify_artists).map(clean),
        "artist_origin": None,
        "album": df["album_name"].map(clean),
        "year": pd.Series([pd.NA] * len(df), dtype="Int64"),
        "genre": None,
        "dialect": None,
        "language_variant": "ar",
        "lyrics": df["lyrics"].map(clean),
        "translation": None,
        "views": pd.Series([pd.NA] * len(df), dtype="Int64"),
        "matched_by": "script+langdetect",
        "lyrics_completeness": "full",
    }), dropped


def main() -> None:
    genius, genius_dropped = load_genius()
    spotify, spotify_dropped = load_spotify960k()
    frames = [genius, load_hiphop(), load_moroccan(), load_egyptian(), spotify]
    df = pd.concat(frames, ignore_index=True)

    df["lyrics"] = df["lyrics"].map(clean)
    df["title"] = df["title"].fillna("").str.strip()
    df["artist"] = df["artist"].fillna("").str.strip()
    df["arabic_ratio"] = df["lyrics"].map(ar_ratio).round(3)
    df["script"] = df["arabic_ratio"].map(script_class)
    df["n_chars"] = df["lyrics"].str.len()
    df["n_lines"] = df["lyrics"].str.count("\n") + 1
    df["has_translation"] = df["translation"].fillna("").str.len() > 0
    df["key"] = [norm_key(t, a) for t, a in zip(df["title"], df["artist"])]
    # Rows without an artist (Egyptian excerpts) or metadata must not collapse.
    blank = (df["key"] == "") | (df["artist"] == "")
    df.loc[blank, "key"] = [f"__row{i}" for i in df.index[blank]]

    df = df[df["n_chars"] >= 100].copy()

    # Same song across sources -> keep the longest lyric.
    df["_prio"] = df["source"].map(
        {"genius": 0, "arabic_hiphop": 1, "moroccan_lyrics": 2,
         "egyptian_songs": 3, "spotify_960k": 4}
    )
    before = len(df)
    df = df.sort_values(["key", "n_chars", "_prio"], ascending=[True, False, True])
    df = df.drop_duplicates("key", keep="first").drop(columns=["_prio", "key"])
    deduped = before - len(df)

    df = df.sort_values(["source", "artist", "title"]).reset_index(drop=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT, index=False)
    df.head(200).to_csv("data/processed/arabic_lyrics_sample.csv", index=False)

    stats = {
        "tracks": len(df),
        "by_source": df["source"].value_counts().to_dict(),
        "by_script": df["script"].value_counts().to_dict(),
        "by_dialect": df["dialect"].value_counts(dropna=False).head(15).to_dict(),
        "artists": int(df.loc[df.artist != "", "artist"].nunique()),
        "with_translation": int(df["has_translation"].sum()),
        "chars": {
            "total": int(df["n_chars"].sum()),
            "median": int(df["n_chars"].median()),
            "p90": int(df["n_chars"].quantile(0.9)),
        },
        "year_range": [
            int(df["year"].min()) if df["year"].notna().any() else None,
            int(df["year"].max()) if df["year"].notna().any() else None,
        ],
        "top_genres": df["genre"].value_counts().head(10).to_dict(),
        "top_artists": df.loc[df.artist != "", "artist"].value_counts().head(20).to_dict(),
        "deduped_rows": int(deduped),
        "genius_cleaning": genius_dropped,
        "spotify_language_detection": spotify_dropped,
    }
    Path("data/processed/arabic_lyrics_stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
