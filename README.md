# DiscoPrincess

Artist content and assets for https://discoprincess.github.io/site/, powered by the pinned [shared artist core](https://github.com/Maxwell-Pierce/artist-site-core).

- `artist.json`: runtime identity, colors, entry portrait/effect, caption default and settings storage namespace.
- `index.html`, `manifesto.html`, `offline.html`: DiscoPrincess-owned copy and layout.
- `assets/`: her own portrait, crown, PWA icons and muted videos.
- `catalog-source.json`, `playlists.json`, `tracks.json`: playlist configuration and saved public metadata.
- `lyrics/`, `lyric-config.json`, `lyric-overrides.json`: retained recognition results, review records and reviewed corrections.
- `.artist-core`: shared player, responsive layout, build, import and lyric-analysis code, pinned to an exact commit.

## Build

```sh
git clone --recurse-submodules https://github.com/DiscoPrincess/site.git
cd site
python .artist-core/scripts/build.py --site . --output _site
```

The build discovers videos, renders saved playlists, applies inexpensive estimated word timings to the output copy and hashes runtime assets. It never analyzes audio or changes the saved recognition source. Generated `app.js`, `style.css`, the PWA manifest and service worker are in `_site/`.

## Publishing and analysis

`Publish artist site` validates each push/PR and deploys main through GitHub Pages. `Analyze artist lyrics` runs daily, manually or when its source inputs change. The latter reuses this repository's existing caches and results, processes at most the configured new-track budget, and commits only refreshed catalog/lyric data. Successful analysis triggers a quick publication.

Dependabot checks the shared submodule daily and proposes an update PR. Shared changes do not reach this site until its core update is merged. Core fixes belong in `Maxwell-Pierce/artist-site-core`; artist-only adjustments belong in `custom.css` / `custom.js` or the local pages. Reverting `.artist-core` rolls back the shared behavior.

See [LYRICS.md](LYRICS.md) for recognition/estimate provenance and reviewed correction details. Artist content, playlists and binaries were retained in the core migration.
