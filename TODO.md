# 📝 Project Roadmap & TODOs

This document tracks the planned features, known bugs, and technical debt for the MX Gas Prices Tracker pipeline.

### Phase 1: MVP & Pipeline Reliability (Current Focus)
- [x] Create repository and define project architecture.
- [x] Write Python extraction script to parse CRE XML feeds (`prices` and `places`).
- [x] Set up GitHub Actions for daily automated runs via cron job.
- [ ] **Test the Pipeline:** Monitor the GitHub Action for the first 3 days to ensure it runs without memory or timeout errors.
- [ ] **Add Error Handling:** Update `extract_and_save.py` with `try/except` blocks in case the CRE Azure servers go down or return a 404 error.
- [ ] **Data Validation:** Write a quick check to ensure coordinates (lat/long) fall within Mexico's geographical bounding box (filter out ocean/invalid coordinates).

### Phase 2: Geospatial Analytics & EDA
- [ ] **Create EDA Notebook:** Set up `notebooks/geospatial_eda.ipynb` to explore the cleaned historical data.
- [ ] **Implement Haversine Logic:** Write a Python function using `SciPy`/`NumPy` to calculate the distance between a given coordinate and all active gas stations.
- [ ] **Price Variance Analysis:** Calculate the average price variance (Magna vs. Premium) within a 5km radius in major cities (e.g., CDMX, Monterrey, Guadalajara).

### Phase 3: Visualization & Business Intelligence
- [ ] **Connect BI Tool:** Link Power BI / Tableau to the `historical_gas_prices.csv` data source.
- [ ] **Build Map Visual:** Create an interactive heat map showing gas price density.
- [ ] **Build Time-Series Visual:** Create a line chart tracking the 30-day moving average of gas prices to visualize inflation/fluctuations.
- [ ] **Export Dashboard:** Take high-quality screenshots or a GIF of the final dashboard and add them to the main `README.md`.

### Phase 4: Scaling & Tech Debt (Future State)
- [ ] **Migrate to Cloud Storage:** Move away from GitHub commit storage and integrate Google BigQuery (or AWS S3 / Supabase) to handle larger historical data volumes.
- [ ] **Update GitHub Action:** Modify `.yml` to push credentials securely via GitHub Secrets to the new cloud database.
- [ ] **Modularize Code:** Split `extract_and_save.py` into separate modules (e.g., `extractor.py`, `transformer.py`, `loader.py`) for cleaner software architecture.

---
*Note to self: Cross off items using `[x]` as they are completed.*