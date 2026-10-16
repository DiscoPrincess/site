"""Sync public Treblo playlists, preserving source order and failing before writes."""
import json,re,urllib.request,html,os,tempfile
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
UUID=re.compile(r'^[0-9a-f-]{36}$')
def objects(page):
    decoder=json.JSONDecoder()
    text=''.join(json.loads(x) for x in re.findall(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)',page))
    for m in re.finditer(r'\{',text):
        try: obj,_=decoder.raw_decode(text[m.start():])
        except ValueError: continue
        if isinstance(obj,dict): yield obj

def image(value):
    if not value or value=='$undefined':return 'assets/mark.svg'
    return value if value.startswith('https://') else 'https://scdn.treblo.com/images/'+value

def extract_playlist(page,pid):
    objs=list(objects(page))
    source=next((d for d in objs if d.get('id')==pid and d.get('type')=='playlist' and isinstance(d.get('songs'),list)),None)
    if source is None or source.get('visibility')!='public':raise ValueError('Public playlist payload missing: '+pid)
    details={d['id']:d for d in objs if d.get('songPath') and 'tags' in d}
    songs=[];seen=set()
    for raw in source['songs']:
        if raw.get('visibility')!='public':continue
        d={**raw,**details.get(raw['id'],{})}
        if d['id'] in seen:continue
        seen.add(d['id'])
        if not d.get('songPath','').startswith('https://cdn.treblo.com/'):raise ValueError('Missing playable stream: '+d['id'])
        songs.append(dict(id=d['id'],title=d['title'],artist=d.get('artistUsername','Unknown artist'),audio=d['songPath'],artwork=image(d.get('artwork')),duration=d.get('duration',0),tags=d.get('tags',[]),likes=d.get('likes'),plays=d.get('playCount'),comments=d.get('commentsCount'),url='https://treblo.com/song/'+d['id']))
    # Explicitly check count fields when supplied: never silently publish a partial page.
    count=source.get('songCount',source.get('songsCount'))
    if isinstance(count,int) and count!=len(source['songs']):raise ValueError('Incomplete playlist payload')
    return dict(id=pid,title=source['title'],description=source.get('description',''),artwork=image(source.get('artwork')),url='https://treblo.com/playlist/'+pid,likes=source.get('likes'),comments=source.get('commentsCount'),tracks=songs,trackCount=len(songs),duration=sum(t['duration'] for t in songs),trackLikes=sum(t['likes'] or 0 for t in songs),plays=sum(t['plays'] or 0 for t in songs) if all(t['plays'] is not None for t in songs) else None,artists=len(set(t['artist'] for t in songs)))
def esc(x):return html.escape(str(x),quote=True)
def duration(s):
    h,m=divmod(round(s/60),60)
    return f'{h} hr {m:02d} min' if h else f'{m} min'
def stats(p):
    pairs=[(p['trackCount'],'tracks'),(duration(p['duration']),'listening'),(p['likes'],'playlist likes'),(p['trackLikes'],'track likes'),(p['plays'],'track plays'),(p['artists'],'artists'),(p['comments'],'playlist comments')]
    return '<div class="playlist-stats">'+''.join(f'<div><strong>{esc(v)}</strong><span>{label}</span></div>' for v,label in pairs if v is not None)+'</div>'
def embed(h,tracks):
    data=json.dumps(tracks,ensure_ascii=False).replace('</','<\\/')
    h,n=re.subn(r'<script id="track-data" type="application/json">.*?</script>',lambda _:f'<script id="track-data" type="application/json">{data}</script>',h,flags=re.S)
    if n!=1:raise ValueError('Catalog marker missing')
    return h

def build(playlists):
    home=(ROOT/'index.html').read_text()
    cards=''
    for i,p in enumerate(playlists):
        href='playlists/'+p['id']+'.html'
        cards+=f'<article class="playlist-feature" id="collection-{esc(p["id"])}"><a class="playlist-cover" href="{href}"><img src="{esc(p["artwork"])}" alt="{esc(p["title"])} artwork" loading="lazy" width="600" height="600"><span>Explore playlist ↗</span></a><div class="playlist-feature-copy"><p class="eyebrow">COLLECTION {i+1:02d} / CURATED BY DISCOPRINCESS</p><h3><a href="{href}">{esc(p["title"])}</a></h3>'+(f'<p>{esc(p["description"])}</p>' if p['description'] else '')+stats(p)+f'<a class="button primary" href="{href}">Enter the playlist <span>↗</span></a></div></article>'
    home,n=re.subn(r'<!-- PLAYLISTS START -->.*?<!-- PLAYLISTS END -->',lambda _: '<!-- PLAYLISTS START -->'+cards+'<!-- PLAYLISTS END -->',home,flags=re.S)
    if n!=1:raise ValueError('Playlist section marker missing')
    unique={}
    for p in playlists:
        for t in p['tracks']:unique.setdefault(t['id'],t)
    home=embed(home,list(unique.values()))
    outputs={'index.html':home,'tracks.json':json.dumps(list(unique.values()),ensure_ascii=False,indent=2)+'\n','playlists.json':json.dumps(playlists,ensure_ascii=False,indent=2)+'\n'}
    for p in playlists:
        page=home.replace('<head>','<head>\n<base href="../">',1)
        page=re.sub(r'<title>.*?</title>',lambda _: '<title>'+esc(p['title'])+' | DiscoPrincess</title>',page)
        page=re.sub(r'<meta name="description"[^>]*>',lambda _:f'<meta name="description" content="{esc(p["title"])} — {p["trackCount"]} tracks, curated by DiscoPrincess.">',page)
        page=page.replace('href="#home"','href="index.html#home"').replace('href="#about"','href="index.html#about"').replace('href="#community"','href="index.html#community"')
        main=f'''<main class="playlist-page"><section class="section playlist-intro"><a class="back-link" href="index.html#music">← All collections</a><div class="playlist-feature"><div class="playlist-cover"><img src="{esc(p['artwork'])}" alt="{esc(p['title'])} artwork" width="600" height="600"></div><div class="playlist-feature-copy"><p class="eyebrow">THE DISCOPRINCESS COLLECTION</p><h1>{esc(p['title'])}</h1>{stats(p)}<button class="button primary" id="begin">▶ Play playlist</button> <a class="text-link" href="{esc(p['url'])}" target="_blank" rel="noopener">View on Treblo ↗</a></div></div></section><section class="section playlist-tracks" id="music"><div class="section-heading"><div><p class="eyebrow">THE FULL SELECTION</p><h2>Follow the <em>feeling.</em></h2></div><button class="shuffle" id="shuffle-all">⇄ Shuffle the collection</button></div><div class="track-grid" id="tracks"></div><p class="music-note">Likes and plays are public Treblo counts from the latest refresh. Track totals combine the songs in this playlist.</p></section></main>'''
        page=re.sub(r'<main>.*?</main>',lambda _:main,page,flags=re.S)
        page=embed(page,p['tracks'])
        page=page.replace('content="DiscoPrincess — The unapologetic glow"',f'content="{esc(p["title"])} | DiscoPrincess"')
        outputs['playlists/'+p['id']+'.html']=page
    return outputs

def main():
    config=json.loads((ROOT/'catalog-source.json').read_text());playlists=[]
    ids=[item['id'] for item in config['playlists']]
    if len(set(ids))!=len(ids) or any(not UUID.fullmatch(pid) for pid in ids):raise ValueError('Invalid/duplicate playlist IDs')
    for pid in ids:
        req=urllib.request.Request('https://treblo.com/playlist/'+pid,headers={'User-Agent':'DiscoPrincessSite/1.0'})
        with urllib.request.urlopen(req,timeout=60) as response:page=response.read().decode()
        playlists.append(extract_playlist(page,pid))
    outputs=build(playlists) # No outputs changed until all fetches and generation succeed.
    for name,content in outputs.items():
        target=ROOT/name;target.parent.mkdir(parents=True,exist_ok=True)
        temp=target.with_suffix(target.suffix+'.tmp');temp.write_text(content);os.replace(temp,target)
    for file in (ROOT/'playlists').glob('*.html'):
        if file.stem not in ids:file.unlink()
    print('Synced:',', '.join(f"{p['title']} ({p['trackCount']} tracks)" for p in playlists))
if __name__=='__main__':main()
