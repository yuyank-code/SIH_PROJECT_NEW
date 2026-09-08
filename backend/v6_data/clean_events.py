#!/usr/bin/env python3
"""Clean NASA COOLR event/report GeoJSON without inventing labels."""
from __future__ import annotations
import json, pathlib, re
import pandas as pd

RAW = pathlib.Path("data/v6/raw")
OUT = pathlib.Path("data/v6/interim")
OUT.mkdir(parents=True, exist_ok=True)

NER = {"Arunachal Pradesh","Assam","Manipur","Meghalaya","Mizoram","Nagaland","Sikkim","Tripura"}

def load_geojson(path):
    obj=json.loads(path.read_text(encoding="utf-8"))
    rows=[]
    for f in obj.get("features",[]):
        p=f.get("properties") or {}
        g=f.get("geometry") or {}
        coords=g.get("coordinates") or [None,None]
        if g.get("type") != "Point" or len(coords)<2:
            continue
        row=dict(p)
        row["longitude"]=coords[0]
        row["latitude"]=coords[1]
        rows.append(row)
    return pd.DataFrame(rows)

def clean(path, outname):
    df=load_geojson(path)
    if df.empty:
        raise SystemExit(f"No features in {path}")
    for c in ["latitude","longitude"]:
        df[c]=pd.to_numeric(df[c], errors="coerce")
    df=df.dropna(subset=["latitude","longitude"])
    df=df[df.latitude.between(21,30) & df.longitude.between(88,98.5)]
    # Try common date field names without assuming one exact schema.
    date_col=next((c for c in ["event_date","date","event_time","event_datetime","reported_date"] if c in df.columns), None)
    if date_col:
        df["event_time_utc"]=pd.to_datetime(df[date_col], errors="coerce", utc=True)
    else:
        df["event_time_utc"]=pd.NaT
    # Preserve all source columns; only add controlled QA fields.
    df["qa_valid_coordinate"]=True
    df["qa_has_event_time"]=df["event_time_utc"].notna()
    # Exact duplicates are removed; near-duplicates remain for later source-aware reconciliation.
    subset=[c for c in ["latitude","longitude","event_time_utc","event_id","title","event_title"] if c in df.columns]
    if subset:
        df=df.drop_duplicates(subset=subset, keep="first")
    df.to_parquet(OUT/outname, index=False)
    return df

for src, out in [(RAW/"nasa_coolr_events.geojson","coolr_events_clean.parquet"),(RAW/"nasa_coolr_reports.geojson","coolr_reports_clean.parquet")]:
    if src.exists():
        d=clean(src,out)
        print(src.name, len(d), "rows")
    else:
        print("SKIP",src)
