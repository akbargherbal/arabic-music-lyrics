# Corpus statistics

Generated from `data/processed/arabic_lyrics.parquet` — **12,463 tracks**, 18,540,195 characters, 2,771 artists, 1921–2023.

## Tracks by source

| Source | Tracks |
|---|---:|
| `genius` | 10,396 |
| `spotify_960k` | 1,021 |
| `arabic_hiphop` | 589 |
| `egyptian_songs` | 280 |
| `moroccan_lyrics` | 177 |

## Artist coverage

- Tracks with an artist string: **12,082 / 12,463** (96.9%)
- Missing artist: 381 tracks (280 Egyptian excerpts + 101 Moroccan rows, upstream limitation)
- Distinct artist strings: **2,771**
- After merging `Name - Arabic alias` variants: **2,736**
- Median tracks per artist: **1**
- Artists with exactly one track: **1,582** (57%)
- Artists with 10+ tracks: **286**
- Share of tracks from the top 10 artists: **10.4%**

## Top 50 artists (alias-merged)

| # | Artist | Tracks | Characters | Median chars | Years | Sources |
|---:|---|---:|---:|---:|---|---|
| 1 | Amr Diab | 375 | 401,098 | 1,047 | 1983–2022 | genius,spotify_960k |
| 2 | Abyusif | 219 | 362,593 | 1,613 | 2009–2022 | arabic_hiphop,genius |
| 3 | The Synaptik | 146 | 206,272 | 1,348 | 2017–2021 | arabic_hiphop,genius,spotify_960k |
| 4 | Wegz | 119 | 171,103 | 1,348 | 2017–2022 | arabic_hiphop,genius |
| 5 | Marwan Pablo | 108 | 123,056 | 1,097 | 2016–2022 | arabic_hiphop,genius |
| 6 | FADA VEX | 104 | 143,995 | 1,418 | 2004–2021 | genius |
| 7 | Lotfi Double Kanon | 99 | 242,732 | 2,235 | 1999–2017 | genius |
| 8 | Vli Weezy | 84 | 94,141 | 1,079 | 2017–2022 | arabic_hiphop,genius |
| 9 | Marwan Moussa | 82 | 162,906 | 1,888 | 2016–2022 | genius |
| 10 | Cairokee | 79 | 76,176 | 922 | 2009–2021 | arabic_hiphop,genius,spotify_960k |
| 11 | Balti | 78 | 171,952 | 2,206 | 2002–2021 | genius,spotify_960k |
| 12 | El Joker | 74 | 158,273 | 1,934 | 2012–2022 | genius |
| 13 | Nancy Ajram | 70 | 74,221 | 988 | 1998–2021 | genius,spotify_960k |
| 14 | Elissa | 70 | 62,088 | 871 | 2002–2020 | genius,spotify_960k |
| 15 | DAM | 69 | 192,712 | 2,427 | 2006–2019 | genius,spotify_960k |
| 16 | Muslim | 66 | 135,154 | 2,019 | 2005–2021 | genius,spotify_960k |
| 17 | Redstar Radi | 60 | 130,375 | 2,157 | 2012–2021 | genius |
| 18 | Tamer Hosny | 59 | 60,455 | 951 | 2006–2021 | genius,spotify_960k |
| 19 | Bu Kolthoum | 55 | 66,048 | 1,263 | 2014–2021 | arabic_hiphop,genius,spotify_960k |
| 20 | Mousv | 54 | 88,576 | 1,628 | 2016–2022 | genius |
| 21 | El Rass | 54 | 88,233 | 1,569 | 2011–2020 | arabic_hiphop,genius,spotify_960k |
| 22 | Souad Massi | 54 | 49,615 | 870 | 2001–2019 | genius,spotify_960k |
| 23 | Shabjdeed | 53 | 88,938 | 1,766 | 2017–2021 | arabic_hiphop,genius |
| 24 | Dahmane El Harrachi | 47 | 71,420 | 1,525 | 1970–2018 | genius |
| 25 | Nassif Zeytoun | 47 | 41,194 | 886 | 2014–2021 | genius,spotify_960k |
| 26 | Flenn | 46 | 87,189 | 1,944 | 2013–2021 | genius |
| 27 | Ghani Mahdi | 46 | 44,414 | 823 | 2014–2014 | genius |
| 28 | Phobia Isaac | 45 | 99,934 | 2,230 | 2015–2021 | genius |
| 29 | MC Amin | 45 | 77,047 | 1,613 | 2013–2021 | arabic_hiphop,genius |
| 30 | Kadim Al Sahir | 44 | 46,960 | 1,042 | — | spotify_960k |
| 31 | Klay BBJ | 43 | 91,438 | 2,098 | 2013–2021 | genius |
| 32 | Alhassan Ortega | 43 | 88,691 | 2,060 | 2014–2020 | genius |
| 33 | Arsenik | 43 | 71,822 | 1,506 | — | arabic_hiphop |
| 34 | Psyco M | 42 | 171,942 | 3,072 | 2011–2021 | genius |
| 35 | El Castro | 42 | 98,960 | 2,167 | 2014–2020 | genius |
| 36 | Blvxb | 41 | 64,547 | 1,371 | 2016–2021 | genius,spotify_960k |
| 37 | Abo El Anwar | 40 | 85,744 | 1,825 | 2019–2022 | arabic_hiphop,genius,spotify_960k |
| 38 | Afroto | 40 | 68,969 | 1,674 | 2018–2022 | genius |
| 39 | Zed-K | 39 | 81,793 | 2,014 | 2013–2021 | genius |
| 40 | Molotof | 39 | 43,075 | 1,062 | 2019–2021 | arabic_hiphop,genius |
| 41 | Wust El Balad | 39 | 39,620 | 990 | 2007–2019 | genius |
| 42 | Mashrou' Leila | 39 | 26,845 | 420 | 2009–2019 | genius |
| 43 | Arsee | 38 | 42,701 | 1,084 | 2019–2022 | genius,spotify_960k |
| 44 | Jadal | | 38 | 26,850 | 666 | 2009–2021 | genius |
| 45 | El Hass | 37 | 68,169 | 1,856 | 2012–2021 | genius |
| 46 | Mohamed Hamaki | 37 | 33,396 | 887 | 2007–2021 | genius,spotify_960k |
| 47 | C H E B . | 36 | 44,523 | 1,224 | 2018–2021 | genius |
| 48 | Fikka Ganja | 35 | 67,770 | 1,629 | 1999–2015 | genius |
| 49 | Icowesh | 35 | 66,077 | 1,793 | 2013–2021 | genius |
| 50 | Haifa Wehbe | 35 | 31,438 | 839 | 2002–2021 | genius,spotify_960k |

## Notes

- Full data: [`data/processed/artist_stats_merged.csv`](data/processed/artist_stats_merged.csv) (alias-merged) and [`data/processed/artist_stats.csv`](data/processed/artist_stats.csv) (as stored).
- Collaborations such as `Molotof & Shabjdeed` are kept as a single artist string, so individual feature credits are not split out.
- The `Name - Arabic alias` merge only applies when the Arabic part is an alias (e.g. `Wegz - ويجز`), not a collaboration.
