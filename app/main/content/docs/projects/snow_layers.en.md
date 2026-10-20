---
title: Snow Layers · Winters in the French mountains
summary: Explore snow depth, season by season
---

**Snow Layers**, coded with Codex, explores snow depth through a non-exhaustive catalogue of 46 French mountain resorts.

### How to use
Choose a resort on the map or from the list, then select a season in the dark panel. The red line shows snow depth in centimetres; the blue band and line show the range and mean of the other available seasons. Hover over or keyboard-focus a point to read its date and value.

The comparison shows December–April means for two resorts alongside altitude-group statistics: low (below 1,200 m), middle (1,200–1,800 m), and high (above 1,800 m). Toggle each series independently. Partial seasons do not represent complete winters, and resort coverage depends on imported data.

### Understanding the data
Without imported observations, Méribel displays an explicitly labelled **simulated demonstration**. Other resorts remain empty. Imported data comes from [Open-Meteo’s ERA5-Land reanalysis](https://open-meteo.com/en/docs/historical-weather-api): these are **modelled** depths, not measurements from resort sensors. Hourly depths in metres are converted to centimetres and averaged by day. Catalogue coordinates and elevations are approximate.

### Availability
Imported series are stored in dedicated tables in the portfolio’s PostgreSQL database. Provenance is shared to reduce storage while retaining daily December–April data. Production imports require an administrator token; viewing remains public. Visiting the page never triggers weather collection. The map uses Leaflet and OpenStreetMap tiles; the list remains available if the map fails. The exploratory interface is in French; this information sheet is also available in English.

### Credits
Illustrative alpine photograph: [Romain Malaunay, Unsplash](https://unsplash.com/photos/cXrhDuOZBiI), La Plagne-Tarentaise. It does not necessarily depict the selected resort. Data: Open-Meteo / ERA5-Land. Map: © OpenStreetMap contributors.
