"""Experimental English singing alignment, CPU wav2vec2 CTC, one line at a time."""
import json,re,sys,subprocess,tempfile,unicodedata
from pathlib import Path
import torch,torchaudio,imageio_ffmpeg
from lyrics_common import accepted_words

def run(source,destination):
    data=json.loads(Path(source).read_text());torch.set_num_threads(2)
    bundle=torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
    model=bundle.get_model().eval();labels={c:i for i,c in enumerate(bundle.get_labels())}
    with tempfile.TemporaryDirectory() as tmp:
        wav=Path(tmp)/'audio.wav'
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',data['audio'],'-ac','1','-ar','16000',str(wav)],check=True,timeout=90)
        audio,sr=torchaudio.load(str(wav))
        for line in data['lines']:
            original=line['text'].split();normalized=[re.sub("[^A-Z']",'',unicodedata.normalize('NFKD',word).encode('ascii','ignore').decode().upper()) for word in original]
            if not all(normalized):continue
            text='|'.join(normalized);tokens=[labels[c] for c in text]
            clip=audio[:,int(line['start']*sr):int(line['end']*sr)]
            if clip.shape[1]<400:continue
            try:
                with torch.inference_mode():emission,_=model(clip)
                emission=emission.log_softmax(-1)
                path,scores=torchaudio.functional.forced_align(emission,torch.tensor([tokens]),blank=0)
                spans=torchaudio.functional.merge_tokens(path[0],scores[0].exp())
                if len(spans)!=len(tokens):continue
                ratio=clip.shape[1]/sr/emission.shape[1];cursor=0;words=[]
                for word,norm in zip(original,normalized):
                    group=spans[cursor:cursor+len(norm)];cursor+=len(norm)+1
                    words.append({'text':word,'start':round(line['start']+group[0].start*ratio,3),'end':round(line['start']+group[-1].end*ratio,3),'score':round(sum(float(x.score) for x in group)/len(group),3)})
                line['words']=accepted_words(words,line)
            except (RuntimeError,ValueError):continue
    Path(destination).write_text(json.dumps(data,ensure_ascii=False))
if __name__=='__main__':run(*sys.argv[1:])
