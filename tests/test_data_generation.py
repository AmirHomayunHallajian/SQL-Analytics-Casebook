from pathlib import Path
import pandas as pd

def test_generated_csvs_exist():
    base=Path('data/processed')
    for f in ["studies.csv","sites.csv","users.csv","clinical_queries.csv"]:
        assert (base/f).exists()

def test_constraints():
    r=pd.read_csv('data/processed/recruitment_events.csv')
    assert (r.randomized_count<=r.screened_count).all()
