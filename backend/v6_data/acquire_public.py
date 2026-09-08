#!/usr/bin/env python3
"""Acquire a first, reproducible tranche of real NER landslide/routing data.

This script intentionally downloads real public observations rather than generating fixtures.
It is designed for CI/runner execution because the ChatGPT runtime is not the data runner.
"""
from __future__ import annotations
import csv, hashlib, json, os, pathlib, time
from datetime import datetime, timezone
from urllib.parse import urlencode
import requests

ROOT = pathlib.Path(os.environ.get("V6_DATA_ROOT", "data/v6/raw"))
ROOT.mkdir(parents=True, exist_ok=True)
MANIFEST = ROOT / "acquisition_manifest.jsonl"

# NER bounding box: west, south, east, north
BBOX = (88.0, 21.0, 98.5, 30.0)
TIMEOUT = int(os.environ.get("V6_HTTP_TIMEOUT", "60"))
UA = "NER-SLIDE-V6-real-data-research/1.0"


def now():
    return datetime.now(timezone.utc).isoformat()


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def record(**kw):
    row = {"retrieval_timestamp": now(), **kw}
    with MANIFEST.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def get_json(url, params=None):
    r = requests.get(url, params=params, headers={"User-Agent": UA}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def arcgis_query(service_url: str, source_id: str, where: str = "1=1"):
    """Download an ArcGIS FeatureServer layer with pagination and spatial AOI."""
    out = ROOT / f"{source_id}.geojson"
    features = []
    offset = 0
    while True:
        params = {
            "where": where,
            "geometry": json.dumps({"xmin": BBOX[0], "ymin": BBOX[1], "xmax": BBOX[2], "ymax": BBOX[3], "spatialReference": {"wkid": 4326}}),
            "geometryType": "esriGeometryEnvelope",
            "inSR": 4326,
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "*",
            "returnGeometry": "true",
            "outSR": 4326,
            "resultOffset": offset,
            "resultRecordCount": 2000,
            "f": "geojson",
        }
        data = get_json(service_url + "/query", params)
        batch = data.get("features", [])
        features.extend(batch)
        if not data.get("exceededTransferLimit") or not batch:
            break
        offset += len(batch)
        time.sleep(0.25)
    payload = {"type": "FeatureCollection", "features": features}
    out.write_text(json.dumps(payload), encoding="utf-8")
    record(source_id=source_id, status="downloaded", format="geojson", path=str(out), feature_count=len(features), bbox=BBOX, sha256=sha256(out))
    return len(features)


def download_url(source_id: str, url: str, filename: str):
    out = ROOT / filename
    if out.exists() and out.stat().st_size > 0:
        record(source_id=source_id, status="already_present", path=str(out), sha256=sha256(out))
        return
    with requests.get(url, headers={"User-Agent": UA}, timeout=TIMEOUT, stream=True) as r:
        r.raise_for_status()
        with out.open("wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)
    record(source_id=source_id, status="downloaded", path=str(out), bytes=out.stat().st_size, sha256=sha256(out))


def usgs_earthquakes():
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson", "starttime": "2000-01-01", "endtime": datetime.now(timezone.utc).date().isoformat(),
        "minmagnitude": os.environ.get("USGS_MIN_MAG", "2.5"),
        "minlatitude": BBOX[1], "maxlatitude": BBOX[3], "minlongitude": BBOX[0], "maxlongitude": BBOX[2],
        "orderby": "time-asc", "limit": "20000"
    }
    data = get_json(url, params)
    out = ROOT / "usgs_earthquakes_2000_present.geojson"
    out.write_text(json.dumps(data), encoding="utf-8")
    record(source_id="usgs_earthquakes", status="downloaded", path=str(out), feature_count=len(data.get("features", [])), sha256=sha256(out), query=params)


def nasa_power_daily(points_csv: pathlib.Path):
    """Optional point-weather extraction for a bounded event sample.

    Set V6_POWER_POINTS to a CSV with latitude,longitude,start,end columns.
    This deliberately runs only when requested because one request is made per point.
    """
    if not points_csv.exists():
        return
    outdir = ROOT / "nasa_power_daily"
    outdir.mkdir(exist_ok=True)
    with points_csv.open(newline="", encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            lat, lon = float(row["latitude"]), float(row["longitude"])
            start = row.get("start", "20000101").replace("-", "")
            end = row.get("end", datetime.now(timezone.utc).strftime("%Y%m%d")).replace("-", "")
            params = {
                "parameters": "PRECTOTCORR,T2M,RH2M,WS10M",
                "community": "AG", "longitude": lon, "latitude": lat,
                "start": start, "end": end, "format": "JSON"
            }
            data = get_json("https://power.larc.nasa.gov/api/temporal/daily/point", params)
            out = outdir / f"point_{i:06d}.json"
            out.write_text(json.dumps(data), encoding="utf-8")
            record(source_id="nasa_power_daily", status="downloaded", path=str(out), point_index=i, sha256=sha256(out))


def main():
    # 1) NASA COOLR event inventory
    arcgis_query(
        "https://gis.earthdata.nasa.gov/gis05/rest/services/Landslides/COOLR_Events_Points/FeatureServer/0",
        "nasa_coolr_events",
    )
    # 2) NASA COOLR report/citizen inventory
    arcgis_query(
        "https://gis.earthdata.nasa.gov/gis05/rest/services/Landslides/COOLR_Reports_Points/FeatureServer/0",
        "nasa_coolr_reports",
    )
    # 3) USGS seismic context
    usgs_earthquakes()
    # 4) Current NE road graph source. Keep raw PBF for reproducible routing extraction.
    download_url(
        "osm_ne_india",
        "https://download.geofabrik.de/asia/india/north-eastern-zone-latest.osm.pbf",
        "north-eastern-zone-latest.osm.pbf",
    )
    # 5) Optional NASA POWER event-point weather extraction.
    points = os.environ.get("V6_POWER_POINTS")
    if points:
        nasa_power_daily(pathlib.Path(points))
    print(f"Acquisition complete. Manifest: {MANIFEST}")


if __name__ == "__main__":
    main()
