# V6 real-data source audit — 2026-09-08

## Confirmed public/authoritative candidates

### NASA COOLR
- Events: NASA ArcGIS `COOLR_Events_Points/FeatureServer/0`.
- Reports: NASA ArcGIS `COOLR_Reports_Points/FeatureServer/0`.
- Contains event/report information from the Global Landslide Catalog, Landslide Reporter Catalog, NASA manual/automatic inventories and contributed inventories.
- Event attributes include event date/title and citations; the service supports JSON queries and has a 2,000-record maximum per query, so the acquisition script paginates.
- Use: historical labels, event validation, citizen/field evidence.

### ISRO/NRSC Bhuvan Landslide Inventory
- Bhuvan exposes seasonal inventories for 2014, 2017 and 2023 and state-specific layers including Arunachal Pradesh, Assam, Manipur, Meghalaya, Mizoram, Nagaland, Sikkim and Tripura.
- Bhuvan also exposes event-based inventories and the Landslide Atlas document.
- Use: Indian regional inventory and cross-source validation.
- Status: public web-service/document access; exact downloadable feature endpoints must be resolved from the Bhuvan webservice/metadata links before automated extraction. Do not substitute another inventory without recording that change.

### OpenStreetMap / Geofabrik
- North-Eastern Zone extract exists as OSM PBF and GIS formats.
- The current public extract is roughly 103 MB PBF and covers the North-Eastern Zone; daily/dated snapshots are available.
- Use: actual road graph, intersections, road classes and routing geometry.
- The acquisition runner downloads the latest PBF rather than using a hand-built demo road network.

### HydroSHEDS
- HydroSHEDS provides core DEM/flow products and derived HydroRIVERS/HydroBASINS products.
- Asia HydroRIVERS and HydroBASINS downloads are available publicly.
- Use: drainage, river distance, flow accumulation, basin context and hydrological network.

### SoilGrids
- ISRIC SoilGrids provides 250 m global soil property predictions with depth layers and uncertainty.
- WebDAV and WCS access are available.
- Use: soil texture, organic carbon, bulk density, pH and other soil properties; dynamic soil moisture must come from a separate time-varying source.

### ESA WorldCover
- WorldCover 2020 v100 and 2021 v200 are available at 10 m.
- Public AWS access is available without an AWS account; tiles can be selected by bounding box.
- Use: land cover and surface context.

### Copernicus Sentinel-1/2
- Copernicus Data Space provides Sentinel data access.
- Sentinel-1 provides all-weather/day-night C-band SAR; Sentinel-2 provides optical observations.
- Use: deformation/change monitoring and post-event assessment. Processing must be designed carefully to prevent post-event leakage into pre-event prediction.

### USGS earthquakes
- USGS FDSN API provides queryable earthquake event data.
- Use: seismic context and triggering events.
- The acquisition runner downloads a Northeast India bounding-box catalogue from 2000 to present at a configurable minimum magnitude.

### NASA GPM IMERG / ERA5-Land / Open-Meteo
- IMERG supplies high-frequency precipitation products with different latency/reprocessing characteristics.
- ERA5-Land provides long consistent land reanalysis but programmatic CDS access may require credentials.
- Open-Meteo provides practical historical/operational weather API access and can be used as a real-data source where appropriate.
- Use: rainfall, temperature, humidity, soil moisture and related dynamic variables.

## Sources requiring additional access/engineering work

- ERA5-Land bulk CDS acquisition: requires an execution environment and appropriate CDS access credentials.
- Copernicus Data Space high-volume Sentinel processing: requires account/API setup for large automated extraction.
- Some Copernicus DEM access tiers have current access restrictions; use an accessible authoritative DEM instance and record exact product/version.
- Official Indian government/telecom warning and road-closure integrations require configured operational endpoints.

## No synthetic-data policy

If a source is inaccessible, the pipeline must record `UNAVAILABLE` or use an explicitly documented real alternative. It must never manufacture observations merely to make a training table complete.
