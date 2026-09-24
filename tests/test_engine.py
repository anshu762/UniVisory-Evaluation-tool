import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import RUBRICS,validate,finalize
class TestURIE(unittest.TestCase):
 def setUp(self): self.p={'competition':'IRIS National Fair','stage':'idea','content':'A student proposes testing a novel low-cost filtration membrane against a commercial baseline under controlled conditions.'}
 def test_rubrics_sum(self):
  for k,r in RUBRICS.items(): self.assertEqual(sum(r['criteria'].values()),100,k)
 def test_validation(self): self.assertEqual(validate(self.p),self.p)
 def test_short_rejected(self):
  with self.assertRaises(ValueError): validate({**self.p,'content':'short'})
 def test_missing_scores_not_zero(self):
  x=finalize({'criteria':{'novelty':{'score':4,'reason':'test'}}},self.p,{'status':'unavailable','works':[]})
  self.assertEqual(x['assessed_weight_percent'],25);self.assertEqual(x['provisional_score_out_of_100'],80);self.assertIsNone(x['criteria']['methodology']['score']);self.assertEqual(x['novelty_status'],'unverified')
 def test_bad_scores_ignored(self):
  x=finalize({'criteria':{'novelty':{'score':100}}},self.p,{'status':'unavailable','works':[]})
  self.assertIsNone(x['provisional_score_out_of_100'])
if __name__=='__main__': unittest.main()
