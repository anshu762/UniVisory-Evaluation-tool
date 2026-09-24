"""URIE Competition Intelligence Engine v2.0
Deterministic policy layer. AI produces observations; this module owns stage gates,
score calculation, evidence sufficiency, confidence, and abstention.
"""
from dataclasses import dataclass
import hashlib

GATE_VALUES=('pass','fail','unknown')

# Evidence sufficiency requirements by stage family. These are URIE policy, not official weights.
EVIDENCE_MINIMUMS={
 'idea':0.30,'profile':0.35,'impact':0.45,
 'methodology':0.50,'validation':0.50,'strategy':0.50,'build':0.55,'application':0.50,'evidence':0.60,
 'submission':0.70
}

def evidence_registry(payload,discovery):
 reg={'SUBMISSION':{'type':'student_submission','verified':False,'label':'Student-supplied content'}}
 for i,w in enumerate(discovery.get('works',[])[:10],1):
  reg[f'LEAD-{i}']={'type':'literature_discovery','verified':False,'title':w.get('title'),'doi':w.get('doi'),'url':w.get('url')}
 for i,line in enumerate(payload.get('evidence','').splitlines()[:40],1):
  if line.strip(): reg[f'USER-{i}']={'type':'user_evidence','verified':False,'label':line.strip()[:400]}
 return reg

def normalize(raw,payload,config,registry):
 source=raw.get('criteria',{}) if isinstance(raw.get('criteria'),dict) else {}
 clean={}; warnings=[]
 for name,weight in config['criteria'].items():
  item=source.get(name,{}) if isinstance(source.get(name,{}),dict) else {}
  score=item.get('score'); score=score if type(score) is int and 0<=score<=5 else None
  reason=str(item.get('reason','')).strip()[:1600]
  refs=[x for x in item.get('evidence_ids',[]) if isinstance(x,str) and x in registry] if isinstance(item.get('evidence_ids',[]),list) else []
  uncertainty=str(item.get('uncertainty','')).strip()[:1000]
  # A score requires explicit reasoning and provenance; unsupported AI numbers are discarded.
  if score is not None and (len(reason)<20 or not refs):
   warnings.append(f'{name}: score withheld — insufficient rationale/provenance')
   score=None
  clean[name]={'weight':weight,'score':score,'reason':reason,'evidence_ids':refs,'uncertainty':uncertainty}
 return clean,warnings

def normalize_gates(raw,config):
 supplied=raw.get('gates',{}) if isinstance(raw.get('gates'),dict) else {}
 out={}
 for gate in config['gates']:
  v=supplied.get(gate,'unknown')
  out[gate]=v if v in GATE_VALUES else 'unknown'
 return out

def decision_engine(raw,payload,discovery,config):
 registry=evidence_registry(payload,discovery)
 criteria,warnings=normalize(raw,payload,config,registry)
 gates=normalize_gates(raw,config)
 assessed=sum(x['weight'] for x in criteria.values() if x['score'] is not None)
 weighted=sum(x['weight']*x['score']/5 for x in criteria.values() if x['score'] is not None)
 score=round(weighted/assessed*100,1) if assessed else None
 evidence_density=round(min(1.0,(len(registry)-1)/max(3,len(config['criteria']))),2)
 stage=payload['stage']; min_ev=EVIDENCE_MINIMUMS.get(stage,0.5)
 if discovery.get('status') in ('discovery_only','reviewable_discovery'):
  warnings.append('Prior-art retrieval is evidence triage, not proof of novelty. Patent/product/code coverage may still be required.')
 else: warnings.append('Independent prior-art discovery unavailable; originality cannot be verified.')
 if any(v=='fail' for v in gates.values()): decision='STOP_CRITICAL_GATE'
 elif any(v=='unknown' for v in gates.values()): decision='CONDITIONAL_UNVERIFIED_GATES'
 elif assessed<70: decision='INSUFFICIENT_ASSESSABLE_EVIDENCE'
 elif evidence_density<min_ev: decision='MORE_EVIDENCE_REQUIRED'
 elif score is not None and score<55: decision='MAJOR_REDESIGN'
 elif score is not None and score<70: decision='PROMISING_BUT_MATERIAL_GAPS'
 else: decision='STRONG_FOR_EXPERT_REVIEW'
 # Never auto-label a winner or predict outcome.
 return {
  'engine_version':'3.0.0','knowledge_base_version':'2026-09-23-v3',
  'submission_hash':hashlib.sha256(payload['content'].encode()).hexdigest(),
  'competition':payload['competition'],'family':config['family'],'stage':stage,
  'criteria':criteria,'gates':gates,'evidence_registry':registry,
  'assessed_weight_percent':assessed,'provisional_score_out_of_100':score,
  'evidence_density':evidence_density,'decision':decision,'warnings':warnings,
  'human_review_required':True,'novelty_verdict':'UNVERIFIED' if discovery.get('status')!='reviewable_discovery' else 'REQUIRES_COMPARATIVE_REVIEW',
  'official_weights':config['official'],'source_basis':config['source'],'competition_rules_note':config['rules'],
  'score_disclaimer':'URIE readiness score, not an official competition score or win probability. Official weights are used only where the organiser publishes them; otherwise URIE internal weights are explicitly marked.',
  'literature_discovery':discovery,
  'strengths':raw.get('strengths',[]),'critical_weaknesses':raw.get('critical_weaknesses',[]),
  'next_actions':raw.get('next_actions',[]),'questions_for_student':raw.get('questions_for_student',[]),
  'competition_fit':raw.get('competition_fit',{}),'submission_specific_feedback':raw.get('submission_specific_feedback',[])
 }
