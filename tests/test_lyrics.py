import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
from lyrics_common import clean_lines,accepted_words
class LyricsTests(unittest.TestCase):
 def test_invalid_and_section_labels_removed(self):
  lines=clean_lines([{'text':'[Verse]','start':0,'end':1},{'text':'hello world','start':1,'end':3},{'text':'bad','start':4,'end':2},{'text':'outside','start':30,'end':32}],10)
  self.assertEqual(len(lines),1);self.assertEqual(lines[0]['words'],[])
 def test_word_confidence_and_bounds(self):
  line={'text':'hello world','start':1,'end':3}
  words=[{'text':'hello','start':1,'end':1.5,'score':.8},{'text':'world','start':2,'end':2.5,'score':.8}]
  self.assertEqual(accepted_words(words,line),words)
  words[1]['score']=.01;self.assertEqual(accepted_words(words,line),[])
if __name__=='__main__':unittest.main()
