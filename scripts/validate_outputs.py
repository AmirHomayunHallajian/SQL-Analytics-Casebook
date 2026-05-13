from pathlib import Path
import sqlite3
ROOT=Path(__file__).resolve().parents[1]
expected=['monthly_active_users.csv','cohort_retention.csv','recruitment_funnel.csv','site_performance_ranking.csv','query_aging.csv','missing_documents_by_site.csv','cycle_time_summary.csv','intervention_priority_sites.csv']
for f in expected:
    assert (ROOT/'data'/'outputs'/f).exists(), f'missing {f}'
con=sqlite3.connect(ROOT/'db'/'analytics_casebook.sqlite')
for t in ['studies','sites','clinical_queries','product_events']:
    assert con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]>0
assert con.execute('SELECT COUNT(*) FROM recruitment_events WHERE randomized_count>screened_count').fetchone()[0]==0
print('Validation summary: all checks passed')
