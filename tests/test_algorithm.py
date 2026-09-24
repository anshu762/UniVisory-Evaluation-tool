import unittest
from algorithm import decision_engine
from engine import RUBRICS
P={'competition':'IRIS National Fair','stage':'idea','content':'A student proposes a novel experiment to compare different filtration membranes and test particle retention under matched flow conditions.'}
D={'status':'unavailable','works':[]}
class AlgorithmTests(unittest.TestCase):
 def test_no_auto_approval(self):
  raw={'criteria':{'novelty':{'score':5,'reason':'Student claims novel filter','evidence_ids':['SUBMISSION']}},'gates':{'student_ownership':'pass','ethics_safety':'pass','feasibility':'pass'},'eligibility':{'status':'eligible'}}
  out=decision_engine(raw,P,D,RUBRICS[P['competition']]);self.assertEqual(out['decision'],'HOLD_UNVERIFIED_GATES');self.assertEqual(out['novelty_verdict'],'UNVERIFIED')
 def test_no_idea_validation(self):
  raw={'criteria':{'validation':{'score':5,'reason':'promises excellent results','evidence_ids':['SUBMISSION']}}}
  out=decision_engine(raw,P,D,RUBRICS[P['competition']]);self.assertIsNone(out['criteria']['validation']['score'])
 def test_no_unproven_score(self):
  raw={'criteria':{'novelty':{'score':5,'reason':'novel'}}}
  out=decision_engine(raw,P,D,RUBRICS[P['competition']]);self.assertIsNone(out['criteria']['novelty']['score'])
 def test_ai_cannot_inject_decision(self):
  raw={'decision':'APPROVED','provisional_score_out_of_100':100,'criteria':{}}
  out=decision_engine(raw,P,D,RUBRICS[P['competition']]);self.assertNotEqual(out['decision'],'APPROVED');self.assertIsNone(out['provisional_score_out_of_100'])
 def test_wrong_score_type(self):
  raw={'criteria':{'novelty':{'score':True,'reason':'x','evidence_ids':['SUBMISSION']}}}
  out=decision_engine(raw,P,D,RUBRICS[P['competition']]);self.assertIsNone(out['criteria']['novelty']['score'])
if __name__=='__main__':unittest.main()
