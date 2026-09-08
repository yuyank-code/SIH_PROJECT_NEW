# NER-SLIDE V6 real-data acquisition layer

This directory is the data-first foundation for V6. It is deliberately separate from the production inference path.

## Rules

1. Raw external data is never edited in place.
2. Every acquisition writes a manifest containing source, version/release, retrieval time, observation coverage, spatial/temporal resolution when known, checksum, and processing status.
3. Missing, stale, inaccessible, and unknown data are explicit states; no synthetic values are used.
4. Prediction-time datasets may only use observations available at or before the prediction timestamp.
5. Event labels, candidate negatives, and unknown samples are kept distinct.
6. Large rasters and road extracts are stored as workflow artifacts/object storage, not committed to Git.

## Initial real sources

- NASA COOLR event and report FeatureServer: landslide events/reports.
- USGS Earthquake FDSN API: earthquake context.
- OpenStreetMap / Geofabrik North-Eastern Zone: real road graph source.
- ESA WorldCover 2020/2021: 10 m land-cover candidate source.
- ISRIC SoilGrids 2.0: 250 m soil properties, WCS/WebDAV candidate source.
- HydroSHEDS/HydroRIVERS/HydroBASINS: hydrological context.
- Copernicus Sentinel-1/2: satellite change/monitoring candidate sources.
- NASA GPM IMERG, ERA5-Land and operational weather APIs: precipitation/environment time series.
- ISRO/NRSC Bhuvan Landslide Atlas/inventories: Indian landslide inventory candidate source.

The acquisition runner starts with lightweight vector/API sources and creates manifests. Large raster acquisition is handled by separate source-specific jobs so that a failed source cannot silently contaminate the dataset.
