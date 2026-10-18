"""Publish timestamp sidecars; align entry tracks once per audio/lyric fingerprint."""
import json,hashlib,subprocess,sys,os
from pathlib import Path
from lyrics_common import clean_lines
ROOT=Path(__file__).resolve().parents[1]
def main():
    playlists=json.loads((ROOT/'playlists.json').read_text());tracks={t['id']:t for p in playlists for t in p['tracks']}
    entry={t['id'] for t in playlists[0]['tracks']} if playlists else set()
    cache=ROOT/'.cache/lyrics';cache.mkdir(parents=True,exist_ok=True)
    out=ROOT/'lyrics';out.mkdir(exist_ok=True);report=[]
    for track in tracks.values():
        lines=clean_lines(track.get('alignedLyrics'),track['duration'])
        data={'id':track['id'],'audio':track['audio'],'language':'en','source':'treblo','alignment':'line','lines':lines}
        fingerprint=hashlib.sha256(json.dumps({'version':1,'audio':track['audio'],'lines':lines},sort_keys=True).encode()).hexdigest()
        stored=cache/(fingerprint+'.json')
        if stored.exists():data=json.loads(stored.read_text())
        elif lines and track['id'] in entry:
            source=cache/(fingerprint+'.input.json');result=cache/(fingerprint+'.result.json');source.write_text(json.dumps(data))
            try:
                subprocess.run([sys.executable,str(ROOT/'scripts/align_words.py'),str(source),str(result)],check=True,timeout=600)
                data=json.loads(result.read_text());data['alignment']='word' if any(l['words'] for l in data['lines']) else 'line'
                stored.write_text(json.dumps(data))
            except (subprocess.SubprocessError,OSError,ValueError) as e:print(f'Line fallback for {track["id"]}: {e}',flush=True)
            finally:source.unlink(missing_ok=True);result.unlink(missing_ok=True)
        (out/(track['id']+'.json')).write_text(json.dumps({k:v for k,v in data.items() if k!='audio'},ensure_ascii=False))
        words=sum(len(l['words']) for l in data['lines']);report.append({'id':track['id'],'title':track['title'],'lines':len(data['lines']),'alignedWords':words,'mode':data['alignment']})
        print(f'{track["title"]}: {len(data["lines"])} lines / {words} aligned words',flush=True)
    (out/'report.json').write_text(json.dumps(report,indent=2))
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as f:f.write('## Experimental lyric alignment\n\n'+ '\n'.join(f'- {r["title"]}: {r["lines"]} lines, {r["alignedWords"]} aligned words' for r in report))
if __name__=='__main__':main()
