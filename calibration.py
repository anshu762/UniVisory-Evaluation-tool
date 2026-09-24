"""URIE v3 calibration layer.
Uses organizer-published criteria plus verified exemplars. Exemplars inform pattern checks, never outcome prediction.
"""
import json
from pathlib import Path
DATA=json.loads((Path(__file__).parent/'calibration_cases.json').read_text(encoding='utf-8'))

def profile(competition):
 rows=DATA.get(competition,[])
 return {'n_verified_exemplars':len(rows),'exemplars':rows,
  'calibration_strength':'MODERATE' if len(rows)>=3 else ('LIMITED' if rows else 'NONE'),
  'warning':'Winner/finalist exemplars reveal recurring evidence patterns but cannot establish causal winning factors and must never be converted into win probabilities.'}

def pattern_checks(competition):
 rows=DATA.get(competition,[]); tags={}
 for r in rows:
  for t in r.get('evidence_patterns',[]):tags[t]=tags.get(t,0)+1
 return [{'pattern':k,'count':v,'share':round(v/len(rows),2)} for k,v in sorted(tags.items(),key=lambda x:(-x[1],x[0]))] if rows else []
