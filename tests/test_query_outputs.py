from pathlib import Path
import pandas as pd

def test_outputs_created():
    p=Path('data/outputs/monthly_active_users.csv')
    assert p.exists()
    df=pd.read_csv(p)
    assert not df.empty
