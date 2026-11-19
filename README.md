
# WastageX - Food Loss Intelligence System

WastageX is a Python-based data processing and analysis project that explores food-loss observations from FAO Food Balance Sheets.

The application reads a large CSV dataset, filters food-loss records, cleans missing and invalid measurements, performs statistical analysis using NumPy, and generates a structured analysis report.

## Project Objectives

- Process real-world agricultural food balance data.
- Identify reported food-loss observations.
- Clean and transform CSV data.
- Calculate meaningful statistical measurements.
- Explore country-wise, commodity-wise, and yearly patterns.
- Generate an automated analysis report.

## Features

### 1. Dataset Inspection
- Identifies CSV columns and available years.
- Reads records using Python's CSV module.
- Examines food balance elements.

### 2. Data Cleaning
- Filters records with the Element value "Losses".
- Converts wide-format yearly data into long format.
- Handles missing and invalid measurements.
- Preserves source flags and negative values for review.

### 3. Statistical Analysis
Uses NumPy to calculate:

- Mean
- Median
- Standard deviation
- Maximum
- Minimum
- 25th percentile
- 75th percentile

### 4. Data Insights
- Country-wise average observations.
- Commodity-wise average observations.
- Year-wise average observations.

### 5. Automated Reporting
Generates a text report containing the statistical results and grouped analysis.

## Technology Stack

- Python
- NumPy
- CSV module
- pathlib
- collections
- Git and GitHub

## Project Structure

```text
WastageX/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── src/
│   └── wastagex.py
│
├── reports/
│   └── analysis_report.txt
│
├── README.md
├── requirements.txt
├── .gitignore
└── LICENSE
```

## Dataset

Dataset: FAO - Food Balance Sheets

Kaggle source:
https://www.kaggle.com/datasets/tcashion/fao-food-balance-sheets

Download the following file:

FoodBalanceSheets_E_All_Data.csv

Place it inside:

`data/raw/`

The dataset contains food production, supply, utilization, and loss-related measurements across geographical areas, commodities, and years.

The dataset is not included in this repository. Users must obtain it from the original source and follow its licensing and attribution requirements.

Dataset license displayed on Kaggle: CC BY-SA 3.0.

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Tharunnagabramhagna/wastagex.git
cd wastagex
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Add the dataset

Place the downloaded CSV file inside:

`data/raw/FoodBalanceSheets_E_All_Data.csv`

### 6. Run the application

```bash
python src/wastagex.py
```

## Generated Outputs

### Cleaned Dataset

`data/processed/food_losses_cleaned.csv`

Contains filtered food-loss observations in long format, including the country, commodity, year, measurement unit, and source flag.

### Analysis Report

`reports/analysis_report.txt`

Contains descriptive statistical calculations and country-wise, commodity-wise, and yearly average observations.

## Statistical Methodology

NumPy is used for numerical calculations.

The analysis is performed separately for each measurement unit.

Missing observations are not treated as zero. Negative measurements are retained in the cleaned dataset for review but excluded from descriptive statistics.

Grouped averages describe the available observations. They should not be interpreted as national or global total food losses.

Aggregate commodity categories may overlap with their component commodities, so their observations should not be blindly added together.

## Important Notes

The FAO Food Balance Sheets "Losses" element represents reported losses within the food balance methodology. It does not measure all food waste at retail or household level.

Source flags are retained for traceability and should be interpreted using the dataset's documentation.

## Future Improvements

- Interactive data visualizations.
- More detailed food-loss trend analysis.
- Improved source-flag interpretation.
- Commodity-level comparisons with non-overlapping categories.
- Exportable analytical summaries.

## Author

Developed as a Python data processing mini-project.

GitHub: https://github.com/Tharunnagabramhagna
