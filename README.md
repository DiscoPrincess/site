# DiscoPrincess
Music site adapted from Natalie4933/site, with a new identity based on the DiscoPrincess manifesto.

## Brand
Midnight #100D1B, velvet #1C1429, cream #F3EBDD, gold #EAC584, pink #F163BD. Cormorant Garamond for expressive display typography; Manrope for navigation, body and player. Gold crown with DP monogram in a concentric seal, supplied as scalable SVG.

## Music
The persistent player retains playback, seek, volume, shuffle, repeat and media-session controls. The catalog is deliberately empty until her selected music is supplied. No Natalie recordings or portraits are included.

`tracks.json` is canonical. Run `python scripts/refresh_tracks.py` to validate and embed it. `catalog-source.json` reserves a playlist source; no artist scraping or automatic ingestion is enabled. Later playlist integration must reflect playlist removals and ordering, validate public playable streams, preserve the prior catalog on source errors, and update both catalog representations together.

## Hosting
The GitHub Actions workflow validates and publishes the static site. In repository Settings > Pages, select GitHub Actions as source if not already enabled. There are no build dependencies. Serve the project directory with any static server for local preview.
