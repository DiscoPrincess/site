'use strict';
const tracks=JSON.parse(document.getElementById('track-data').textContent);
const $=id=>document.getElementById(id), audio=$('audio');
let current=-1,shuffle=false,filter='all',lastVolume=.7,playRequest=0;
audio.volume=lastVolume;
const format=seconds=>{seconds=Number.isFinite(seconds)?Math.max(0,Math.floor(seconds)):0;return `${Math.floor(seconds/60)}:${String(seconds%60).padStart(2,'0')}`;};
const isCategory=(track,category)=>category==='all'||(category==='chant'?track.tags.some(t=>/chant|tibetan|devotional/i.test(t)):category==='rhythm'?track.tags.some(t=>/percussion|bass|liquid/i.test(t)):track.tags.some(t=>/ambient|piano|ethereal|soft/i.test(t)));
function render(){
 if(!tracks.length){ $('tracks').innerHTML='<div class="catalog-empty"><img src="assets/mark.svg" alt="" width="88" height="88"><p class="eyebrow">THE NEXT CHAPTER</p><h3>Good things take a little rhythm.</h3><p>A new collection is on its way.<br>Until then, make yourself at home.</p></div>'; ['play','shuffle','shuffle-all','next','prev','repeat','quiet-track','seek'].forEach(id=>$(id).disabled=true); return; }
 $('tracks').replaceChildren();
 tracks.forEach((track,index)=>{
  if(!isCategory(track,filter))return;
  const card=document.createElement('article');card.className='track-card';card.dataset.index=index;
  const art=document.createElement('div');art.className='track-art';const img=document.createElement('img');img.src=track.artwork;img.alt=`${track.title} cover artwork`;img.loading='lazy';img.width=400;img.height=400;
  const play=document.createElement('button');play.className='track-play';play.dataset.play=index;play.addEventListener('click',()=>select(index));art.append(img,play);
  const row=document.createElement('div');row.className='track-title-row';const title=document.createElement('h3');title.textContent=track.title;const time=document.createElement('span');time.textContent=format(track.duration);row.append(title,time);
  const meta=document.createElement('div');meta.className='track-meta';const tags=document.createElement('span');tags.textContent=`${track.artist || 'DiscoPrincess'} · ${track.likes ?? '—'} likes${track.plays != null ? ` · ${track.plays} plays` : ''}`;const link=document.createElement('a');link.href=track.url;link.className='track-treblo-link';link.textContent='Treblo ↗';link.target='_blank';link.rel='noopener';link.setAttribute('aria-label',`Open ${track.title} on Treblo`);meta.append(tags);const links=document.createElement('div');links.className='track-links';links.append(link);card.append(art,row,links,meta);$('tracks').append(card);
 });sync();
}
function sync(){
 const playing=!audio.paused&&!audio.ended;
 $('play').textContent=playing?'Ⅱ':'▶';$('play').setAttribute('aria-label',playing?'Pause':'Play');
 document.querySelectorAll('.track-card').forEach(card=>card.classList.toggle('playing',Number(card.dataset.index)===current));
 document.querySelectorAll('[data-play]').forEach(button=>{const i=Number(button.dataset.play),active=i===current&&playing;button.textContent=active?'Ⅱ':'▶';button.setAttribute('aria-label',`${active?'Pause':'Play'} ${tracks[i].title}`);button.setAttribute('aria-pressed',String(active));});
 $('shuffle').setAttribute('aria-pressed',String(shuffle));$('shuffle').setAttribute('aria-label',shuffle?'Disable shuffle':'Enable shuffle');
 $('shuffle-all').textContent=shuffle?'⇄  Shuffle on':'⇄  Shuffle the collection';
 if('mediaSession' in navigator)navigator.mediaSession.playbackState=playing?'playing':'paused';
}
async function select(index,force=false){
 if(!tracks.length)return;
 if(index===current&&!force){if(audio.paused)await resume();else audio.pause();return;}
 current=(index+tracks.length)%tracks.length;const track=tracks[current];audio.src=track.audio;$('player-title').textContent=track.title;$('player-subtitle').textContent=`${track.artist || 'DiscoPrincess'} · Treblo`;$('player-art').src=track.artwork;$('song-link').href=track.url;$('song-link').setAttribute('aria-label',`Open ${track.title} on Treblo`);$('duration').textContent=format(track.duration);$('elapsed').textContent='0:00';$('seek').value=0;
 if('mediaSession' in navigator&&'MediaMetadata' in window){navigator.mediaSession.metadata=new MediaMetadata({title:track.title,artist:track.artist || 'DiscoPrincess',album:'The unapologetic glow',artwork:[{src:track.artwork}]});}
 sync();await resume();
}
async function resume(){const request=++playRequest;$('player-status').textContent='Loading your sound…';try{await audio.play();if(request===playRequest)$('player-status').textContent='';}catch(error){if(request===playRequest&&error.name!=='AbortError')$('player-status').textContent='Playback couldn’t start. Try Play again, or use ↗ to listen on Treblo.';}sync();}
function step(direction){let index;if(shuffle&&tracks.length>1){index=Math.floor(Math.random()*(tracks.length-1));if(index>=current)index++;}else index=current<0?0:current+direction;select(index,true);}
$('play').addEventListener('click',()=>current<0?select(0):select(current));$('begin').addEventListener('click',()=>tracks.length?(current<0?select(0):select(current)):document.getElementById('music').scrollIntoView({behavior:'smooth'}));$('quiet-track')?.addEventListener('click',()=>select(Math.max(0,tracks.findIndex(t=>t.artist==='discoprincess')),true));$('next').addEventListener('click',()=>step(1));$('prev').addEventListener('click',()=>audio.currentTime>3?(audio.currentTime=0):step(-1));
$('shuffle').addEventListener('click',()=>{shuffle=!shuffle;sync();});$('shuffle-all').addEventListener('click',()=>{shuffle=true;step(1);sync();});$('repeat').addEventListener('click',()=>{audio.loop=!audio.loop;$('repeat').setAttribute('aria-pressed',String(audio.loop));});
$('seek').addEventListener('input',event=>{if(Number.isFinite(audio.duration)&&audio.duration>0)audio.currentTime=Number(event.target.value)/100*audio.duration;});
function syncVolume(){$('volume').value=audio.muted?0:audio.volume;$('mute').textContent=audio.muted||audio.volume===0?'♪':'♫';$('mute').setAttribute('aria-label',audio.muted||audio.volume===0?'Unmute':'Mute');}
$('volume').addEventListener('input',event=>{audio.volume=Number(event.target.value);audio.muted=false;if(audio.volume>0)lastVolume=audio.volume;syncVolume();});$('mute').addEventListener('click',()=>{if(audio.volume===0){audio.volume=lastVolume;audio.muted=false;}else audio.muted=!audio.muted;syncVolume();});
audio.addEventListener('timeupdate',()=>{$('elapsed').textContent=format(audio.currentTime);$('seek').value=audio.duration?audio.currentTime/audio.duration*100:0;});audio.addEventListener('loadedmetadata',()=>{$('duration').textContent=format(audio.duration);});audio.addEventListener('play',sync);audio.addEventListener('pause',sync);audio.addEventListener('ended',()=>{if(!audio.loop)step(1);});audio.addEventListener('waiting',()=>{$('player-status').textContent='Loading your sound…';});audio.addEventListener('playing',()=>{$('player-status').textContent='';sync();});audio.addEventListener('error',()=>{$('player-status').textContent='This stream is unavailable. Try another track or open the song on Treblo ↗.';sync();});
document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{filter=button.dataset.filter;document.querySelectorAll('[data-filter]').forEach(b=>{b.classList.toggle('active',b===button);b.setAttribute('aria-pressed',String(b===button));});render();}));
if('mediaSession' in navigator){[['play',()=>current<0?select(0):resume()],['pause',()=>audio.pause()],['previoustrack',()=>step(-1)],['nexttrack',()=>step(1)],['seekto',details=>{if(Number.isFinite(details.seekTime))audio.currentTime=details.seekTime;}]].forEach(([action,handler])=>{try{navigator.mediaSession.setActionHandler(action,handler);}catch{}});}
$('year').textContent=new Date().getFullYear();render();

