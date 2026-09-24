"""URIE v3 prior-art intelligence.
Discovery != verification. Multi-source retrieval, similarity triage, and a novelty defence matrix.
No source is treated as proof until it carries enough metadata/abstract evidence for review.
"""
import json, re, urllib.parse, urllib.request, math
from collections import Counter

STOP=set('the a an and or of to in for on with by from is are was were be been this that these those as at it its into using use based via we our their'.split())

def toks(s): return [x for x in re.findall(r'[a-z0-9]+',(s or '').lower()) if len(x)>2 and x not in STOP]
def cosine(a,b):
 ca,cb=Counter(toks(a)),Counter(toks(b));
 if not ca or not cb:return 0.0
 dot=sum(v*cb.get(k,0) for k,v in ca.items()); den=math.sqrt(sum(v*v for v in ca.values())*sum(v*v for v in cb.values()))
 return round(dot/den,3) if den else 0.0

def inv(idx):
 if not idx:return ''
 pos=[]
 for word,locs in idx.items():
  for p in locs: pos.append((p,word))
 return ' '.join(w for _,w in sorted(pos))

def get_json(url,headers=None,timeout=10):
 req=urllib.request.Request(url,headers=headers or {'User-Agent':'URIE/3.0 prior-art research'})
 with urllib.request.urlopen(req,timeout=timeout) as r:return json.load(r)

def openalex(q,limit=12):
 try:
  url='https://api.openalex.org/works?'+urllib.parse.urlencode({'search':q[:300],'per-page':limit,'select':'id,title,publication_year,doi,abstract_inverted_index,primary_location'})
  d=get_json(url); out=[]
  for x in d.get('results',[]):
   out.append({'provider':'OpenAlex','type':'paper','title':x.get('title'),'year':x.get('publication_year'),'doi':x.get('doi'),'url':x.get('id'),'abstract':inv(x.get('abstract_inverted_index'))[:6000]})
  return out
 except Exception:return []

def crossref(q,limit=8):
 try:
  url='https://api.crossref.org/works?'+urllib.parse.urlencode({'query.bibliographic':q[:300],'rows':limit,'select':'DOI,title,abstract,published'})
  d=get_json(url); out=[]
  for x in d.get('message',{}).get('items',[]):
   title=(x.get('title') or [''])[0]; abstract=re.sub('<[^>]+>',' ',x.get('abstract',''))
   parts=(x.get('published',{}).get('date-parts') or [[None]])[0]
   doi=x.get('DOI'); out.append({'provider':'Crossref','type':'paper','title':title,'year':parts[0],'doi':doi,'url':('https://doi.org/'+doi if doi else None),'abstract':abstract[:6000]})
  return out
 except Exception:return []

def dedupe(items):
 seen=set();out=[]
 for x in items:
  key=(x.get('doi') or re.sub(r'\W+',' ',(x.get('title') or '').lower()).strip())
  if not key or key in seen:continue
  seen.add(key);out.append(x)
 return out

def build_matrix(submission,items,top=10):
 ranked=[]
 for x in items:
  hay=(x.get('title') or '')+' '+(x.get('abstract') or '')
  x=dict(x);x['similarity']=cosine(submission,hay);x['review_status']='metadata_plus_abstract' if x.get('abstract') else 'metadata_only'
  x['risk_flag']='HIGH_SIMILARITY_REVIEW' if x['similarity']>=.35 else ('REVIEW' if x['similarity']>=.18 else 'LOW_TEXTUAL_SIMILARITY')
  ranked.append(x)
 ranked.sort(key=lambda z:z['similarity'],reverse=True)
 return ranked[:top]

def discover(submission,query=None):
 q=(query or submission)[:300]
 items=dedupe(openalex(q)+crossref(q))
 matrix=build_matrix(submission,items)
 abstract_n=sum(1 for x in matrix if x['review_status']=='metadata_plus_abstract')
 status='reviewable_discovery' if abstract_n>=3 else ('discovery_only' if matrix else 'unavailable')
 return {'status':status,'query':q,'sources':['OpenAlex','Crossref'],'matrix':matrix,'works':matrix,
  'coverage':{'retrieved':len(items),'top_reviewed':len(matrix),'abstract_available':abstract_n,'patent_search':'NOT_CONFIGURED'},
  'novelty_policy':'Text similarity is triage, not a novelty verdict. A human/expert or evidence-grounded AI must compare problem, method, result and claimed contribution. Patent/product/code search is required where relevant.',
  'required_novelty_defence':['closest prior work','what it already solves','method used','result/limitation','student claimed difference','experiment/benchmark that could falsify the claimed improvement']}
