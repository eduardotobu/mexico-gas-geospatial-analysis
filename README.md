# ⛽ México Gas Geospatial Analysis: End-to-End ETL & Geospatial Analysis

### 📊 Project Overview
In Mexico, the Comisión Nacional de Energía (CRE) publishes daily updates on gasoline prices and station locations via XML feeds. The objective of this project is to build an automated, cloud-based data pipeline that extracts this daily data, cleans it, and maps it geospatially to identify the cheapest fuel options within any given radius.

This tool is designed to help logistics companies, delivery fleets, and everyday drivers optimize their fuel expenditures by identifying micro-regional price variances.

---

### 🏗️ Architecture & Workflow

1. **Automated Ingestion:** A Python script runs daily via **GitHub Actions** at 6:00 AM CST to fetch the latest XML feeds for prices (`/prices`) and locations (`/places`).
2. **Transformation & Cleaning:** Data is parsed, merged on `place_id`, and cleaned to remove erroneous geospatial coordinates using **Pandas**.
3. **Cloud Storage:** Historical daily snapshots are pushed to an **AWS S3** bucket to build a time-series database of inflation and regional price trends.
4. **Geospatial Recommendation Logic:** A custom Python function utilizes the Haversine formula (via `SciPy`/`NumPy`) to calculate the distance between a user's coordinates and nearby stations, ranking them by price.
5. **Visualization:** A **Power BI / Tableau** dashboard connects to the cleaned dataset to visualize price density and regional averages over time.

---

### 🛠️ Tech Stack
* **Languages:** Python (Pandas, NumPy, SciPy, Requests, BeautifulSoup)
* **Cloud & Automation:** AWS S3, GitHub Actions (CI/CD)
* **Visualization:** Power BI / Tableau
* **Concepts:** ETL Pipelines, Geospatial Analysis, Time-Series Tracking

---

### 📂 Repository Structure

```text
mexico-gas-geospatial-analysis/
│
├── .github/workflows/       
│   └── daily_scraper.yml      # GitHub Action automating the daily run
│
├── src/                     
│   ├── extract_xml.py         # Fetches CRE data from Azure endpoints
│   ├── process_data.py        # Cleans and joins prices with coordinates
│   └── push_to_s3.py          # Uploads daily historical data to AWS S3
│
├── notebooks/             
│   └── spatial_analysis.ipynb # EDA and Haversine distance logic
│
├── visuals/               
│   └── dashboard_map.png      # Power BI Dashboard preview
│
├── requirements.txt         
└── README.md                
```

---

### 💡 Key Findings & Business Impact
* **Micro-Regional Variance:** Discovered up to a X% price variance for Magna/Premium gasoline within a 5km radius in major metropolitan areas.
* **Fleet Cost Optimization:** By utilizing the recommendation engine to always select the cheapest station within a logistical route, a mid-sized delivery fleet (50 vehicles) could potentially reduce monthly fuel costs by $X,XXX MXN.
* **Data Resilience:** Built a fault-tolerant historical dataset in AWS S3, bypassing the CRE's limitation of only displaying the current day's prices.

---

### 🚀 How to Run Locally

1. Clone the repository:
   ```bash
   git clone [https://github.com/eduardotobu/mexico-gas-geospatial-analysis.git](https://github.com/eduardotobu/mexico-gas-geospatial-analysis.git)
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the extraction and processing scripts:
   ```bash
   python src/extract_xml.py
   python src/process_data.py
   ```
*(Note: To test the AWS S3 upload, you will need to configure your own `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in your environment variables.)*
