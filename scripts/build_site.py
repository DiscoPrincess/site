"""Build pages from the committed catalog without network or audio analysis."""
import json
from refresh_tracks import ROOT, build
from estimate_lyrics import build_estimates

def main():
    playlists = json.loads((ROOT / 'playlists.json').read_text())
    for name, content in build(playlists).items():
        target = ROOT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    estimated = build_estimates(ROOT / 'lyrics')
    print(f'Added {estimated} estimated word timings without audio analysis.')
    print(f'Built pages from {len(playlists)} saved playlists; reused existing lyrics.')

if __name__ == '__main__':
    main()
