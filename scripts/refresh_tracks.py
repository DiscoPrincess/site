"""Validate and embed the curated catalog. Playlist ingestion will be added later."""
import json
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    config=json.loads((ROOT/'catalog-source.json').read_text())
    if config['mode'] != 'manual':
        raise RuntimeError('Playlist ingestion is not configured. Existing catalog preserved.')
    tracks=json.loads((ROOT/'tracks.json').read_text())
    if not isinstance(tracks,list): raise ValueError('Catalog must be an array')
    seen=set()
    for t in tracks:
        if not all(t.get(k) for k in ('id','title','audio','artwork','url')): raise ValueError('Incomplete track')
        if t['id'] in seen: raise ValueError('Duplicate track')
        seen.add(t['id'])
        if not all(t[k].startswith('https://') for k in ('audio','artwork','url')): raise ValueError('HTTPS required')
        if not isinstance(t.get('tags'),list): raise ValueError('Tags must be an array')
    index=ROOT/'index.html'
    replacement='<script id="track-data" type="application/json">'+json.dumps(tracks,ensure_ascii=False).replace('</','<\\/')+'</script>'
    updated,n=re.subn(r'<script id="track-data" type="application/json">.*?</script>',lambda _:replacement,index.read_text(),flags=re.S)
    if n!=1:raise RuntimeError('Catalog marker missing')
    index.write_text(updated)
    print(f'Validated {len(tracks)} tracks. Playlist integration deferred.')
if __name__=='__main__': main()
