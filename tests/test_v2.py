import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from algorithm import decision_engine
KB=json.loads((Path(__file__).parents[1]/"competition_kb.json").read_text())
def test_12(): assert len(KB)==12
def test_each_has_3_stages(): assert all(len(v["stages"])==3 for v in KB.values())
def test_no_mit_solve(): assert "MIT Solve" not in KB
def test_rsi_not_research_fair(): assert KB["RSI at MIT"]["family"]=="student_selection"
def test_blue_official(): assert KB["Blue Ocean Competition"]["official"] is True
