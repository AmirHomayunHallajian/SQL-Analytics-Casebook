-- Q1 totals by study
SELECT s.study_name,SUM(r.screened_count) total_screened,SUM(r.randomized_count) total_randomized,SUM(r.withdrawn_count) total_withdrawn FROM recruitment_events r JOIN studies s USING(study_id) GROUP BY 1;
-- Q2 screen failure rate
SELECT study_id,ROUND(100.0*SUM(screen_failed_count)/NULLIF(SUM(screened_count),0),2) AS screen_failure_rate_pct FROM recruitment_events GROUP BY 1;
-- Q3 enrollment attainment
SELECT s.study_name,ROUND(100.0*SUM(r.randomized_count)/s.target_enrollment,2) attainment_pct FROM recruitment_events r JOIN studies s USING(study_id) GROUP BY s.study_id;
-- Q4 monthly trend
SELECT strftime('%Y-%m',event_date) year_month,SUM(randomized_count) randomized FROM recruitment_events GROUP BY 1 ORDER BY 1;
-- Q5 recruitment by country
SELECT si.country,SUM(r.randomized_count) randomized FROM recruitment_events r JOIN sites si USING(site_id) GROUP BY 1 ORDER BY 2 DESC;
-- Q6 sites below target
SELECT site_id,SUM(randomized_count) randomized,SUM(monthly_target) target FROM recruitment_events GROUP BY site_id HAVING randomized<target;
-- Q7 active sites by study
SELECT study_id,COUNT(DISTINCT site_id) active_sites FROM sites WHERE site_status='Active' GROUP BY 1;
-- Q8 site activation rate
SELECT study_id,ROUND(100.0*SUM(CASE WHEN activation_status='Activated' THEN 1 ELSE 0 END)/COUNT(*),2) activation_rate FROM site_activation_events GROUP BY 1;
-- Q9 avg activation delay
SELECT study_id,AVG(julianday(activated_date)-julianday(planned_activation_date)) avg_delay_days FROM site_activation_events GROUP BY 1;
-- Q10 missing doc rate
SELECT ROUND(100.0*SUM(CASE WHEN required_flag=1 AND received_flag=0 THEN 1 ELSE 0 END)/COUNT(*),2) missing_document_rate_pct FROM site_documents;
-- Q11 critical missing docs
SELECT COUNT(*) critical_missing_documents FROM site_documents sd JOIN document_types dt USING(document_type_id) WHERE dt.is_critical=1 AND sd.received_flag=0;
-- Q12 open/overdue/SLA/avg resolution
SELECT COUNT(*) open_queries FROM clinical_queries WHERE query_status='Open';
SELECT COUNT(*) overdue_queries FROM clinical_queries WHERE query_status='Open' AND julianday('now')-julianday(query_open_date)>sla_days;
SELECT ROUND(100.0*AVG(CASE WHEN query_status='Resolved' AND julianday(query_resolved_date)-julianday(query_open_date)<=sla_days THEN 1.0 ELSE 0 END),2) sla_compliance_pct FROM clinical_queries;
SELECT AVG(julianday(query_resolved_date)-julianday(query_open_date)) avg_resolution_days FROM clinical_queries WHERE query_status='Resolved';
