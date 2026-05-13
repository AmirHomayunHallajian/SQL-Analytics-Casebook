"""Generate deterministic synthetic analytics data for the casebook."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed"
SEED = 42


def _date_dim(start: str = "2024-01-01", periods: int = 730) -> pd.DataFrame:
    d = pd.date_range(start=start, periods=periods, freq="D")
    return pd.DataFrame({
        "date_key": d.date.astype(str), "year": d.year, "quarter": d.quarter,
        "month": d.month, "month_name": d.strftime("%B"), "year_month": d.strftime("%Y-%m"),
        "week": d.isocalendar().week.astype(int), "day_of_week": d.strftime("%A"),
        "is_weekend": d.weekday.isin([5, 6]).astype(int),
    })


def generate() -> None:
    rng = np.random.default_rng(SEED)
    OUT.mkdir(parents=True, exist_ok=True)
    studies = pd.DataFrame([
        [1, "ONC-201", "Oncology", "Phase II", "NovaThera", "2024-01-01", "2026-12-31", 600, "Active"],
        [2, "CVD-302", "Cardiology", "Phase III", "HelixBio", "2024-03-01", "2026-12-31", 700, "Active"],
        [3, "IMM-145", "Immunology", "Phase II", "Arcadia Pharma", "2024-02-15", "2026-10-31", 450, "Active"],
        [4, "CNS-220", "Neurology", "Phase III", "VitaGen", "2024-04-01", "2027-03-31", 800, "Active"],
        [5, "MET-118", "Endocrinology", "Phase II", "Aster Labs", "2024-01-20", "2026-11-30", 520, "Startup"],
    ], columns=["study_id","study_name","therapeutic_area","study_phase","sponsor","planned_start_date","planned_end_date","target_enrollment","study_status"])
    n_sites = 80
    countries = ["United States","Canada","Germany","India","Brazil","Spain"]
    country_weight = {"United States":1.2,"India":1.1,"Germany":1.0,"Canada":0.9,"Brazil":0.8,"Spain":0.7}
    site_rows=[]
    for i in range(1,n_sites+1):
        sid = int(rng.integers(1,6)); c = rng.choice(countries)
        planned = pd.Timestamp("2024-02-01") + pd.Timedelta(days=int(rng.integers(0,365)))
        delay = int(rng.choice([0,5,10,20,35,60], p=[0.2,0.2,0.2,0.2,0.15,0.05]))
        actual = planned + pd.Timedelta(days=delay)
        site_rows.append([i,sid,f"Site-{i:03d}",c,"NA" if c in ["United States","Canada"] else "ROW",rng.choice(["Tier 1","Tier 2","Tier 3"],p=[0.3,0.5,0.2]),f"PI {i}",planned.date(),actual.date(),"Active",int(rng.integers(20,80))])
    sites=pd.DataFrame(site_rows,columns=["site_id","study_id","site_name","country","region","site_tier","principal_investigator","planned_activation_date","actual_activation_date","site_status","enrollment_target"])
    users=[]
    for u in range(1,451):
        srow = sites.sample(1, random_state=int(SEED+u)).iloc[0]
        role = rng.choice(["CRA","Coordinator","Data Manager","Investigator","Study Lead"], p=[0.2,0.35,0.2,0.15,0.1])
        users.append([u,int(srow.site_id),int(srow.study_id),role,srow.country,(pd.Timestamp("2024-01-01")+pd.Timedelta(days=int(rng.integers(0,500)))).date(),rng.choice(["Active","Inactive"],p=[0.82,0.18])])
    users=pd.DataFrame(users,columns=["user_id","site_id","study_id","user_role","country","signup_date","user_status"])
    doc_types=pd.DataFrame([[i,t,c,int(i%3==0)] for i,(t,c) in enumerate([
        ("CV","Regulatory"),("Medical License","Regulatory"),("GCP Certificate","Training"),("Delegation Log","Operations"),("Lab Certification","Regulatory"),("IRB Approval","Regulatory"),("Insurance","Finance"),("Training Log","Training"),("Temperature Log","Operations"),("Pharmacy License","Regulatory")],1)],columns=["document_type_id","document_type","document_category","is_critical"])
    months = pd.period_range("2024-01", "2025-12", freq="M")
    rec=[]; rid=1
    for _,s in sites.iterrows():
        for m in months:
            screened=max(0,int(rng.normal(12*country_weight[s.country],4)))
            fail=int(min(screened,rng.integers(1,max(2,screened//2+1)))) if screened>0 else 0
            rand=max(0,screened-fail-int(rng.integers(0,3)))
            wd=int(min(rand,rng.integers(0,3))) if rand>0 else 0
            rec.append([rid,s.study_id,s.site_id,m.to_timestamp("M").date(),screened,fail,rand,wd,int(s.enrollment_target/24)])
            rid+=1
    recruitment=pd.DataFrame(rec,columns=["recruitment_event_id","study_id","site_id","event_date","screened_count","screen_failed_count","randomized_count","withdrawn_count","monthly_target"])
    # activation
    sae=[]
    for i,s in sites.iterrows():
        sel=pd.Timestamp(s.planned_activation_date)-pd.Timedelta(days=int(rng.integers(30,90)))
        cs=sel+pd.Timedelta(days=int(rng.integers(5,20))); csg=cs+pd.Timedelta(days=int(rng.integers(3,25)))
        rs=csg+pd.Timedelta(days=int(rng.integers(5,20))); ra=rs+pd.Timedelta(days=int(rng.integers(7,35))); siv=ra+pd.Timedelta(days=int(rng.integers(3,15)))
        act=max(pd.Timestamp(s.actual_activation_date),siv+pd.Timedelta(days=int(rng.integers(1,10))))
        sae.append([i+1,s.study_id,s.site_id,sel.date(),cs.date(),csg.date(),rs.date(),ra.date(),siv.date(),act.date(),s.planned_activation_date,"Activated"])
    activation=pd.DataFrame(sae,columns=["activation_event_id","study_id","site_id","site_selected_date","contract_sent_date","contract_signed_date","regulatory_submitted_date","regulatory_approved_date","site_initiation_visit_date","activated_date","planned_activation_date","activation_status"])
    q=[]
    for i in range(1,3501):
        s=sites.sample(1,random_state=SEED+i).iloc[0]
        o=pd.Timestamp("2024-01-01")+pd.Timedelta(days=int(rng.integers(0,700)))
        is_open=rng.random()<0.25
        rdate=None if is_open else (o+pd.Timedelta(days=int(rng.integers(1,35)))).date()
        q.append([i,s.study_id,s.site_id,f"SUBJ-{rng.integers(1000,9999)}",o.date(),rdate,"Open" if is_open else "Resolved",rng.choice(["Data Entry","Protocol","Safety","Eligibility"]),rng.choice(["Low","Medium","High"],p=[0.4,0.4,0.2]),int(rng.integers(5,16))])
    queries=pd.DataFrame(q,columns=["query_id","study_id","site_id","subject_id","query_open_date","query_resolved_date","query_status","query_category","query_priority","sla_days"])
    sd=[]; did=1
    for _,s in sites.iterrows():
        for _,d in doc_types.iterrows():
            received=int(rng.random()> (0.25 if s.site_tier=="Tier 3" else 0.12))
            approved=int(received and rng.random()>0.1)
            due=pd.Timestamp("2025-01-01")+pd.Timedelta(days=int(rng.integers(0,180)))
            recd=(due-pd.Timedelta(days=int(rng.integers(-10,20)))).date() if received else None
            sd.append([did,s.study_id,s.site_id,d.document_type_id,1,received,approved,due.date(),recd,"Approved" if approved else ("Received" if received else "Missing")]);did+=1
    docs=pd.DataFrame(sd,columns=["document_record_id","study_id","site_id","document_type_id","required_flag","received_flag","approved_flag","due_date","received_date","document_status"])
    pe=[]
    roles_freq={"Study Lead":0.8,"Data Manager":0.7,"CRA":0.55,"Coordinator":0.5,"Investigator":0.35}
    evt=["login","view_dashboard","complete_training","complete_form","export_report"]
    eid=1
    for _,u in users.iterrows():
        n=int(rng.integers(8,95)*roles_freq[u.user_role])
        for _ in range(n):
            ts=pd.Timestamp("2024-01-01")+pd.Timedelta(days=int(rng.integers(0,730)),hours=int(rng.integers(0,24)))
            pe.append([eid,u.user_id,u.site_id,u.study_id,ts,ts.date(),rng.choice(evt,p=[0.35,0.25,0.1,0.2,0.1]),rng.choice(["Onboarding","Data Capture","Monitoring","Reporting"]),f"sess-{u.user_id}-{rng.integers(1,999)}"]);eid+=1
    events=pd.DataFrame(pe,columns=["event_id","user_id","site_id","study_id","event_timestamp","event_date","event_type","product_area","session_id"])
    wt=[]
    for i in range(1,2201):
        s=sites.sample(1,random_state=i+99).iloc[0]
        created=pd.Timestamp("2024-01-01")+pd.Timedelta(days=int(rng.integers(0,700)))
        ttype=rng.choice(["Contract Review","Regulatory Package","Data Review","Monitoring Follow-up"])
        lag={"Contract Review":18,"Regulatory Package":22,"Data Review":10,"Monitoring Follow-up":14}[ttype]
        done = rng.random()>0.18
        completed=(created+pd.Timedelta(days=int(rng.integers(1,lag+8)))).date() if done else None
        wt.append([i,s.study_id,s.site_id,ttype,created.date(),completed,"Completed" if done else "Open",rng.choice(["Low","Medium","High"]),rng.choice(["CRA","Coordinator","Data Manager"]),int(rng.integers(7,21))])
    tasks=pd.DataFrame(wt,columns=["task_id","study_id","site_id","task_type","task_created_date","task_completed_date","task_status","task_priority","owner_role","sla_days"])

    for name,df in {"studies":studies,"sites":sites,"users":users,"document_types":doc_types,"date_dim":_date_dim(),"recruitment_events":recruitment,"site_activation_events":activation,"clinical_queries":queries,"site_documents":docs,"product_events":events,"workflow_tasks":tasks}.items():
        df.to_csv(OUT/f"{name}.csv",index=False)
    print("Synthetic data generated in data/processed")

if __name__ == "__main__":
    generate()
