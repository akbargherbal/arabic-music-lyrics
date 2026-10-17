"""Filter the 9 GB Genius lyrics dump to Arabic songs using DuckDB (single pass).

Input : data/raw/song_lyrics.csv  (extracted from the Kaggle zip)
Output: data/processed/genius_arabic.parquet
        data/processed/genius_arabic_stats.json

A row is kept when any of the three language detectors says 'ar', or the
lyrics are >30% Arabic script and no detector says Persian/Urdu/Kurdish.
"""
import json
import time
from pathlib import Path

import duckdb

CSV = "data/raw/song_lyrics.csv"
OUT = "data/processed/genius_arabic.parquet"
STATS = "data/processed/genius_arabic_stats.json"

READ = (
    f"read_csv('{CSV}', header=true, quote='\"', escape='\"', "
    "ignore_errors=true)"
)
ARABIC_RE = r"[\p{Arabic}]"
OTHER = "('fa','ur','ps','ku')"

con = duckdb.connect()
con.execute("PRAGMA threads=2")
con.execute("PRAGMA memory_limit='6GB'")

query = f"""
COPY (
  WITH src AS (
    SELECT id, title, tag, artist, year, views, lyrics,
           language_cld3, language_ft, language,
           (coalesce(language_cld3,'') = 'ar'
            OR coalesce(language_ft,'') = 'ar'
            OR coalesce(language,'') = 'ar') AS detector_ar
    FROM {READ}
  ),
  scored AS (
    SELECT *,
      CASE
        WHEN detector_ar THEN 1.0
        -- cheap gate: only build strings when the lyric actually has Arabic
        WHEN regexp_matches(lyrics, '{ARABIC_RE}') THEN
          (length(regexp_replace(lyrics, '\\s', '', 'g'))
           - length(regexp_replace(lyrics, '{ARABIC_RE}', '', 'g')))::DOUBLE
          / nullif(length(regexp_replace(lyrics, '\\s', '', 'g')), 0)
        ELSE 0.0
      END AS arabic_ratio
    FROM src
  )
  SELECT *,
    CASE WHEN detector_ar THEN 'detector' ELSE 'script' END AS matched_by
  FROM scored
  WHERE detector_ar
     OR (arabic_ratio > 0.30
         AND coalesce(language_cld3,'') NOT IN {OTHER}
         AND coalesce(language_ft,'')  NOT IN {OTHER})
) TO '{OUT}' (FORMAT parquet, COMPRESSION zstd)
"""
t0 = time.time()
if Path(OUT).exists():
    print(f"{OUT} already exists, skipping filter", flush=True)
else:
    print("filtering (single scan of 9 GB) ...", flush=True)
    con.execute(query)
    print(f"wrote {OUT} in {time.time() - t0:.0f}s", flush=True)

rows = con.execute(
    f"""
    SELECT count(*) n_rows,
           count(DISTINCT title || '|' || artist) tracks,
           count(DISTINCT artist) artists,
           min(year) year_min, max(year) year_max,
           count(*) FILTER (WHERE coalesce(language_cld3,'')='ar') cld3_ar,
           count(*) FILTER (WHERE coalesce(language_ft,'')='ar') ft_ar,
           count(*) FILTER (WHERE coalesce(language,'')='ar') label_ar
    FROM read_parquet('{OUT}')
    """
).fetchone()
matched = dict(con.execute(
    f"SELECT matched_by, count(*) FROM read_parquet('{OUT}') GROUP BY 1"
).fetchall())
tags = dict(con.execute(
    f"SELECT tag, count(*) FROM read_parquet('{OUT}') GROUP BY 1 ORDER BY 2 DESC LIMIT 20"
).fetchall())
top_artists = dict(con.execute(
    f"SELECT artist, count(*) FROM read_parquet('{OUT}') GROUP BY 1 ORDER BY 2 DESC LIMIT 30"
).fetchall())
langs = dict(con.execute(
    f"SELECT language, count(*) FROM read_parquet('{OUT}') GROUP BY 1 ORDER BY 2 DESC"
).fetchall())
years = dict(con.execute(
    f"SELECT year, count(*) FROM read_parquet('{OUT}') GROUP BY 1 ORDER BY 1"
).fetchall())

out = {
    "rows": rows[0],
    "tracks": rows[1],
    "artists": rows[2],
    "year_min": rows[3],
    "year_max": rows[4],
    "detector_hits": {"cld3": rows[5], "ft": rows[6], "label": rows[7]},
    "matched_by": matched,
    "language_labels": langs,
    "top_tags": tags,
    "top_artists": top_artists,
    "rows_per_year": years,
}
with open(STATS, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(json.dumps({k: v for k, v in out.items()
                  if k not in ("top_artists", "rows_per_year")},
                 ensure_ascii=False, indent=2))
print("elapsed", round(time.time() - t0), "s")
