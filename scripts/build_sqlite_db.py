from pathlib import Path
import sqlite3, pandas as pd

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'db'/'analytics_casebook.sqlite'
CSV=ROOT/'data'/'processed'

TABLES=['studies','sites','users','document_types','date_dim','recruitment_events','site_activation_events','clinical_queries','site_documents','product_events','workflow_tasks']

con=sqlite3.connect(DB)
con.executescript((ROOT/'sql'/'01_schema.sql').read_text())
for t in TABLES:
    pd.read_csv(CSV/f'{t}.csv').to_sql(t,con,if_exists='append',index=False)
print('Build summary:')
for t in TABLES:
    c=con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
    print(t,c)
con.close()
