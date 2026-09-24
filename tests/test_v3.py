import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from prior_art import build_matrix
from calibration import profile,pattern_checks
from algorithm import decision_engine

def test_prior_art_similarity_and_status():
 m=build_matrix('underwater holographic camera microplastics AI',[{'title':'AI holographic imaging of microplastics','abstract':'underwater holographic camera detects microplastics with machine learning'}])
 assert m[0]['similarity']>0
 assert m[0]['review_status']=='metadata_plus_abstract'

def test_calibration_is_nonpredictive():
 p=profile('Regeneron ISEF'); assert p['n_verified_exemplars']>=2
 assert 'cannot' in p['warning'].lower()
 assert pattern_checks('Regeneron ISEF')

def test_no_exemplar_false_precision():
 p=profile('IRIS National Fair'); assert p['calibration_strength']=='NONE'
