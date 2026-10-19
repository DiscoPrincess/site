"""Build pages from the committed catalog without network or audio analysis."""
import json
from refresh_tracks import ROOT, build

def main():
    playlists = json.loads((ROOT / 'playlists.json').read_text())
    for name, content in build(playlists).items():
        target = ROOT / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
    print(f'Built pages from {len(playlists)} saved playlists; reused existing lyrics.')

if __name__ == '__main__':
    main()
