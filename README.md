# Arabic Music Lyrics Corpus

A reproducible pipeline that collects public Arabic song-lyrics datasets and
filters them down to **Arabic-only lyrics**.

**Result: 12,463 tracks · 2,771 artists · 18.5M characters · 1921–2023**

Published dataset: [akbargherbal/arabic-music-lyrics](https://huggingface.co/datasets/akbargherbal/arabic-music-lyrics)

## Statistics

Full summary and top-50 artist table: **[STATS.md](STATS.md)**

Machine-readable per-artist counts:

- [`data/processed/artist_stats.csv`](data/processed/artist_stats.csv) — as stored (2,771 artist strings)
- [`data/processed/artist_stats_merged.csv`](data/processed/artist_stats_merged.csv) — `Name - Arabic alias` merged (2,736 artists)

Top of the distribution: Amr Diab (375 tracks), Abyusif (219), The Synaptik (146),
Wegz (119), Marwan Pablo (108). The corpus is long-tailed: 57% of artists have
exactly one track, and the top 10 artists account for 10.4% of tracks.

## Sources

| Source | Tracks | Origin | Notes |
|---|---:|---|---|
| `genius` | 10,396 | [Genius Song Lyrics](https://www.kaggle.com/datasets/carlosgdcj/genius-song-lyrics-with-language-information) (Kaggle) | ~12M-row multilingual dump with 3 language detectors |
| `spotify_960k` | 1,021 | [960K Spotify Songs With Lyrics](https://www.kaggle.com/datasets/bwandowando/spotify-songs-with-attributes-and-lyrics) (Kaggle) | no language column → script filter + `langdetect` |
| `arabic_hiphop` | 589 | [Arabic hip-hop lyrics](https://www.kaggle.com/datasets/dadalyndell/arabic-hip-hop) (Kaggle) | Egyptian / Palestinian / Syrian / Lebanese rap |
| `egyptian_songs` | 280 | [fr3on/egyptian-songs](https://huggingface.co/datasets/fr3on/egyptian-songs) (HF) | line-level excerpts + English translations |
| `moroccan_lyrics` | 177 | [atlasia/moroccan_lyrics](https://huggingface.co/datasets/atlasia/moroccan_lyrics) (HF) | Darija, largely written in Arabizi |

Interesting finding: the 12M-song Genius dump contains only ~11k Arabic tracks
(~0.09%), and the 550K Spotify dump contains **zero** predominantly-Arabic
tracks (only English songs with Arabic hooks), so it was excluded.

## Filtering

- **Genius**: keep a row if `language_cld3`, `language_ft` or `language` says
  `ar`, or if >30% of non-space characters are Arabic script and no detector
  says Persian/Urdu/Pashto/Kurdish. The 9 GB CSV is scanned directly out of the
  zip with DuckDB (no extraction needed).
- **Spotify**: >50% Arabic script, then `langdetect`; only `ar` kept (Persian
  and Urdu share the script and were removed).
- Cleanup: dropped non-music Genius entries (Quran recitations, Ibn Khaldoun's
  *Muqaddima*, list articles) and literal "Genius Arabic Translations" pages;
  dropped tracks <100 characters; removed Persian/Urdu/Kurdish rows that used
  Arabic script.
- Deduplicated on normalized `title + artist`, keeping the longest lyric.

## Layout

```
scripts/
  filter_genius_duckdb.py    # 9 GB Genius CSV -> Arabic parquet (DuckDB)
  filter_spotify_arabic.py   # Spotify dumps -> Arabic-script parquet
  merge_corpus.py            # normalize + clean + dedupe all sources
  artist_stats.py            # per-artist track/character counts
  upload_hf.py               # publish to the Hugging Face Hub
data/processed/
  arabic_lyrics.parquet      # final corpus (21 columns)
  arabic_lyrics_stats.json
  arabic_lyrics_sample.csv   # first 200 rows
  artist_stats.csv           # per-artist counts, as stored
  artist_stats_merged.csv    # per-artist counts, alias-merged
STATS.md                     # human-readable statistics
```

## Reproduce

```bash
pip install pandas pyarrow duckdb langdetect huggingface_hub kaggle

kaggle datasets download -d carlosgdcj/genius-song-lyrics-with-language-information -p data/raw
unzip data/raw/genius-song-lyrics-with-language-information.zip -d data/raw
python scripts/filter_genius_duckdb.py

kaggle datasets download -d bwandowando/spotify-songs-with-attributes-and-lyrics -p data/raw --unzip
kaggle datasets download -d dadalyndell/arabic-hip-hop -p data/raw --unzip
python scripts/filter_spotify_arabic.py

python scripts/merge_corpus.py
```

## Columns

`source`, `source_id`, `source_url`, `title`, `artist`, `artist_origin`,
`album`, `year`, `genre`, `dialect`, `language_variant`, `lyrics`,
`translation`, `views`, `matched_by`, `lyrics_completeness`, `arabic_ratio`,
`script`, `n_chars`, `n_lines`, `has_translation`.

## Caveats

- **Copyright**: lyrics belong to their authors and publishers. This is a
  research compilation of already-public scraped data, not a license to
  redistribute lyrics commercially.
- `egyptian_songs` has no artist field upstream and contains verse/chorus
  excerpts, not complete songs.
- Dialect labels come from the sources and are not independently verified.
- 111 tracks are Latin-script Arabizi (`script = latin/arabizi`).

## License

Code: MIT. Data: see caveats above.
