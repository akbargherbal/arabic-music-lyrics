"""Filter the two Spotify lyric dumps to Arabic-script tracks with DuckDB."""
import json
import sys
import time
from pathlib import Path

import duckdb

ARABIC_RE = r"[\p{Arabic}]"

SOURCES = {
    "spotify_960k": {
        "csv": "data/raw/songs_with_attributes_and_lyrics.csv",
        "out": "data/processed/spotify960k_arabic.parquet",
        "cols": "id, name, album_name, artists, lyrics",
    },
    "spotify_550k": {
        "csv": "data/raw/spotify550k/songs.csv",
        "out": "data/processed/spotify550k_arabic.parquet",
        "cols": "id, name, album_name, artists, lyrics, year, genre, popularity",
    },
}


def run(name: str, cfg: dict) -> dict:
    con = duckdb.connect()
    con.execute("PRAGMA threads=2")
    con.execute("PRAGMA memory_limit='6GB'")
    q = f"""
    COPY (
      WITH src AS (
        SELECT {cfg['cols']}
        FROM read_csv('{cfg['csv']}', header=true, quote='"', escape='"',
                      ignore_errors=true)
        WHERE lyrics IS NOT NULL
          AND length(lyrics) >= 100
          AND regexp_matches(lyrics, '{ARABIC_RE}')
      ), scored AS (
        SELECT *,
          (length(regexp_replace(lyrics, '\\s', '', 'g'))
           - length(regexp_replace(lyrics, '{ARABIC_RE}', '', 'g')))::DOUBLE
          / nullif(length(regexp_replace(lyrics, '\\s', '', 'g')), 0) AS arabic_ratio
        FROM src
      )
      SELECT * FROM scored WHERE arabic_ratio > 0.50
    ) TO '{cfg['out']}' (FORMAT parquet, COMPRESSION zstd)
    """
    t0 = time.time()
    con.execute(q)
    n = con.execute(f"SELECT count(*) FROM read_parquet('{cfg['out']}')").fetchone()[0]
    print(f"{name}: {n:,} tracks in {time.time()-t0:.0f}s -> {cfg['out']}", flush=True)
    return {"source": name, "tracks": n}


if __name__ == "__main__":
    which = sys.argv[1:] or list(SOURCES)
    stats = [run(n, SOURCES[n]) for n in which]
    Path("data/processed/spotify_filter_stats.json").write_text(
        json.dumps(stats, indent=2), encoding="utf-8"
    )
