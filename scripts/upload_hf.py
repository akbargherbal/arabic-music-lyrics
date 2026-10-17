"""Publish the merged Arabic lyrics corpus to the Hugging Face Hub.

Creates/updates a *private* dataset repo (lyrics are copyrighted; flip to
public yourself if you have the rights) and uploads:

    arabic_lyrics.parquet
    arabic_lyrics_stats.json
    arabic_lyrics_sample.csv
    README.md   (dataset card)
"""
import json
import shutil
from pathlib import Path

import pandas as pd
from huggingface_hub import HfApi

REPO_ID = "akbargherbal/arabic-music-lyrics"
PROC = Path("data/processed")
STAGE = PROC / "upload"

CARD = """---
pretty_name: Arabic Music Lyrics
language:
  - ar
  - arz
  - ary
task_categories:
  - text-generation
tags:
  - music
  - lyrics
  - arabic
  - egyptian-arabic
  - moroccan-darija
  - rap
  - hip-hop
size_categories:
  - {size_cat}
license: other
---

# Arabic Music Lyrics

Arabic-language song lyrics collected from public datasets: **{tracks:,} tracks**
from **{artists:,} artists**, {chars:,} characters of lyrics.

## Sources

| source | tracks | origin | notes |
|---|---:|---|---|
| `genius` | {genius:,} | [Genius Song Lyrics](https://www.kaggle.com/datasets/carlosgdcj/genius-song-lyrics-with-language-information) (Kaggle API, Jan 2023) | ~12M-song multilingual dump with 3 language detectors; filtered to Arabic |
| `arabic_hiphop` | {hiphop:,} | [Arabic hip-hop lyrics](https://www.kaggle.com/datasets/dadalyndell/arabic-hip-hop) (Kaggle) | Egyptian/Palestinian/Syrian/Lebanese rap |
| `moroccan_lyrics` | {moroccan:,} | [atlasia/moroccan_lyrics](https://huggingface.co/datasets/atlasia/moroccan_lyrics) | Moroccan Darija, often written in Arabizi (Latin script) |
| `egyptian_songs` | {egyptian:,} | [fr3on/egyptian-songs](https://huggingface.co/datasets/fr3on/egyptian-songs) | Egyptian Arabic; **excerpts** (verse/chorus lines only) + English translations |
| `spotify_960k` | {spotify:,} | [960K Spotify Songs With Lyrics](https://www.kaggle.com/datasets/bwandowando/spotify-songs-with-attributes-and-lyrics) (Kaggle) | Arabic-script lyrics; Persian/Urdu removed with `langdetect` |

## Filtering

From the ~12M-row Genius dump, a track is kept when **any** of the three
provided language detectors (`language_cld3`, `language_ft`, `language`) labels
it `ar`, **or** when >30% of the non-space characters are Arabic script and no
detector labels it Persian/Urdu/Pashto/Kurdish. Tracks shorter than 100
characters were dropped, and duplicates were removed on normalized
title+artist (keeping the longest lyric).

The Spotify set has no language column, so it was filtered to >50% Arabic
script and then passed through `langdetect`; only `ar` rows were kept
(Persian and Urdu share the script and were removed).

Genius `misc` entries were cleaned of non-music content (Quran recitations,
Ibn Khaldoun's *Muqaddima*, Genius Arabia list articles) and of
"Genius Arabic Translations" pages (literal translations of foreign songs).

## Columns

| column | meaning |
|---|---|
| `source` | one of the four sources above |
| `source_id`, `source_url` | original identifier/link when available |
| `title`, `artist`, `album`, `year` | metadata (artist is null for `egyptian_songs`, which has no artist field) |
| `artist_origin`, `dialect`, `language_variant` | country / dialect labels when the source provides them |
| `genre` | Genius tag (e.g. rap, pop, rock) |
| `lyrics` | cleaned lyric text |
| `translation` | English translation (`egyptian_songs` only) |
| `views`, `matched_by`, `lyrics_completeness` | provenance / completeness flags |
| `arabic_ratio`, `script` | share of Arabic-script characters; `arabic`, `mixed`, or `latin/arabizi` |
| `n_chars`, `n_lines`, `has_translation` | convenience statistics |

## Script distribution

{distribution}

## Caveats

- **Copyright**: lyrics belong to their authors/publishers. This dataset is a
  research compilation of already-public scraped data, not a license to
  redistribute the lyrics commercially.
- Genius lyrics include structural tags such as `[Chorus]` and may contain
  romanized Arabic; `script` flags the ones that are mostly Latin script.
- `egyptian_songs` rows are line-level excerpts, not complete songs.
- `spotify_960k` and `genius` lyrics use literal `\n` in some rows; the
  `lyrics` column has already been normalized to real newlines.
- Dialect labels are inherited from the sources and are not independently
  verified.
"""


def main() -> None:
    stats = json.loads((PROC / "arabic_lyrics_stats.json").read_text())
    df = pd.read_parquet(PROC / "arabic_lyrics.parquet")

    n = len(df)
    size_cat = (
        "n<1K" if n < 1_000 else
        "1K<n<10K" if n < 10_000 else
        "10K<n<100K" if n < 100_000 else
        "100K<n<1M" if n < 1_000_000 else "1M<n<10M"
    )
    by_source = stats["by_source"]
    dist = "\n".join(
        f"- `{k}`: {v:,} tracks" for k, v in stats["by_script"].items()
    )

    STAGE.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PROC / "arabic_lyrics.parquet", STAGE / "arabic_lyrics.parquet")
    shutil.copy2(PROC / "arabic_lyrics_stats.json", STAGE / "arabic_lyrics_stats.json")
    shutil.copy2(PROC / "arabic_lyrics_sample.csv", STAGE / "arabic_lyrics_sample.csv")
    (STAGE / "README.md").write_text(
        CARD.format(
            tracks=n,
            artists=stats["artists"],
            chars=stats["chars"]["total"],
            genius=by_source.get("genius", 0),
            hiphop=by_source.get("arabic_hiphop", 0),
            moroccan=by_source.get("moroccan_lyrics", 0),
            egyptian=by_source.get("egyptian_songs", 0),
            spotify=by_source.get("spotify_960k", 0),
            size_cat=size_cat,
            distribution=dist,
        ),
        encoding="utf-8",
    )

    api = HfApi()
    url = api.create_repo(
        repo_id=REPO_ID, repo_type="dataset", private=True, exist_ok=True
    )
    print("repo:", url)
    api.upload_folder(
        folder_path=str(STAGE),
        repo_id=REPO_ID,
        repo_type="dataset",
        commit_message=f"Arabic music lyrics corpus ({n:,} tracks)",
    )
    print("uploaded:", f"https://huggingface.co/datasets/{REPO_ID}")


if __name__ == "__main__":
    main()
