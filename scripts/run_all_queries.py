from pathlib import Path
import sqlite3, pandas as pd
ROOT=Path(__file__).resolve().parents[1]
con=sqlite3.connect(ROOT/'db'/'analytics_casebook.sqlite')
out=ROOT/'data'/'outputs'; out.mkdir(parents=True,exist_ok=True)
q={
' monthly_active_users.csv':"SELECT strftime('%Y-%m',event_date) year_month,COUNT(DISTINCT user_id) monthly_active_users FROM product_events GROUP BY 1 ORDER BY 1",
' cohort_retention.csv':"WITH c AS (SELECT user_id,strftime('%Y-%m',MIN(event_date)) cohort_month FROM product_events GROUP BY 1),a AS (SELECT p.user_id,c.cohort_month,strftime('%Y-%m',p.event_date) active_month,((CAST(strftime('%Y',p.event_date) AS INT)-CAST(substr(c.cohort_month,1,4) AS INT))*12 + (CAST(strftime('%m',p.event_date) AS INT)-CAST(substr(c.cohort_month,6,2) AS INT))) cohort_age FROM product_events p JOIN c USING(user_id) GROUP BY 1,2,3) SELECT cohort_month,cohort_age,COUNT(DISTINCT user_id) retained_users FROM a GROUP BY 1,2",
' recruitment_funnel.csv':"SELECT SUM(screened_count) screened,SUM(randomized_count) randomized,SUM(randomized_count-withdrawn_count) retained FROM recruitment_events",
' site_performance_ranking.csv':"SELECT site_id,SUM(randomized_count) randomized,RANK() OVER (ORDER BY SUM(randomized_count) DESC) rk FROM recruitment_events GROUP BY 1",
' query_aging.csv':"SELECT CASE WHEN julianday('now')-julianday(query_open_date)<=5 THEN '0-5' WHEN julianday('now')-julianday(query_open_date)<=10 THEN '6-10' WHEN julianday('now')-julianday(query_open_date)<=20 THEN '11-20' ELSE '21+' END aging_bucket,COUNT(*) cnt FROM clinical_queries WHERE query_status='Open' GROUP BY 1",
' missing_documents_by_site.csv':"SELECT site_id,SUM(CASE WHEN required_flag=1 AND received_flag=0 THEN 1 ELSE 0 END) missing_docs FROM site_documents GROUP BY 1",
' cycle_time_summary.csv':"SELECT 'query_resolution' metric,AVG(julianday(query_resolved_date)-julianday(query_open_date)) avg_days FROM clinical_queries WHERE query_status='Resolved' UNION ALL SELECT 'workflow_completion',AVG(julianday(task_completed_date)-julianday(task_created_date)) FROM workflow_tasks WHERE task_status='Completed'",
' intervention_priority_sites.csv':"SELECT r.site_id,SUM(r.randomized_count) rand,COALESCE(q.open_q,0) open_queries,COALESCE(d.missing_docs,0) missing_docs FROM recruitment_events r LEFT JOIN (SELECT site_id,COUNT(*) open_q FROM clinical_queries WHERE query_status='Open' GROUP BY 1) q USING(site_id) LEFT JOIN (SELECT site_id,SUM(CASE WHEN received_flag=0 THEN 1 ELSE 0 END) missing_docs FROM site_documents GROUP BY 1) d USING(site_id) GROUP BY 1 ORDER BY open_queries DESC, missing_docs DESC, rand ASC LIMIT 10"
}
for k,v in q.items(): pd.read_sql_query(v,con).to_csv(out/k.strip(),index=False)
(Path(ROOT/'reports'/'query_results_summary.md')).write_text('# Query Results Summary\n\nGenerated outputs in data/outputs.\n')
con.close(); print('Query outputs created')
