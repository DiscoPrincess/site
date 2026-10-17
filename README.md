# DiscoPrincess
Music site adapted from Natalie4933/site, with a new identity based on the DiscoPrincess manifesto.

## Brand
Midnight #100D1B, velvet #1C1429, cream #F3EBDD, gold #EAC584, pink #F163BD. Cormorant Garamond for expressive display typography; Manrope for navigation, body and player. Gold crown with DP monogram in a concentric seal, supplied as scalable SVG.

## Playlists and music
Add public Treblo playlist IDs to `catalog-source.json` in the desired homepage order. Run `python scripts/refresh_tracks.py`, or trigger the Publish workflow. GitHub Actions fetches all configured playlists daily at 06:17 UTC and on each push, then publishes the generated homepage, dedicated `playlists/<id>.html` pages, catalog and metadata.

The importer scopes membership to each playlist's `songs` array, preserves ordering, includes all artists, deduplicates tracks, and enriches records from public song metadata. Removed tracks disappear on the next successful refresh. A missing/private/malformed source fails the build before any catalog writes or deployment, preserving the last published version. The importer requires complete server-rendered playlist membership and checks count fields when exposed; it does not invent counts or silently truncate known paginated sources.

Cards show track count, total duration, playlist likes, combined track likes, track plays (only when available for every track), and artist count. Dedicated pages credit each track artist. Counts are source snapshots, not local voting controls. Public source links are included.

`tracks.json` holds the unique shared catalog; `playlists.json` holds metadata and per-playlist tracks. Embedded catalogs allow immediate playback without a data fetch. The player supports play/pause, seeking, volume, shuffle, repeat and Media Session controls.

Validation: `python -m unittest discover -s tests` and `node --check app.js`.

## Hosting
The GitHub Actions workflow validates and publishes the static site. In repository Settings > Pages, select GitHub Actions as source if not already enabled. There are no build dependencies. Serve the project directory with any static server for local preview.

## Opening videos
Upload MP4 or WebM videos under `assets/` (subdirectories supported). Each deployment discovers them with `scripts/build_videos.py`. The homepage shuffles the full collection per visit and each cycle, avoiding consecutive repeats when possible. Video audio is always muted; only the music player produces sound. Unsupported or broken videos are skipped. With no videos, a dark gradient remains. MP4 H.264 is recommended for browser compatibility.
