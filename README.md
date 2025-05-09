# Microplastics Data Analysis

This project uses a dataset from the California Open Data Portal about microplastic concentrations in different drinking water sources in samples across various countries. Our code produces visualizations that examine the average concentration of microplastic particles in bottled versus tap water and concentrations in varying countries and continents. 

# Getting Started

## Installing

* Clone this repository from GitHub: https://github.com/ArcaneWorm/Microplastics-Data-Analysis.git
* Ensure you have Python 3.x installed
* Install required libraries using pip:
```
pip install pandas matplotlib seaborn numpy pycountry-convert
```
* Ensure `samples_geocoded.csv` and `SouthAfricaWaterMP.csv` are in the same directory as your analysis script.

## Executing program

* Run the main analysis script: main.py
* This will:
  - Clean and preprocess the dataset
  - Remove outliers
  - Generate cleaned data (`output.csv`)
  - Produce and save figures in your working directory

# Datasets
* Main dataset: [Microplastics in Drinking Water - California Open Data Portal](https://data.ca.gov/dataset/microplastics-in-drinking-water)
* Additional dataset: [Detection and characterisation of microplastics in tap water from Gauteng, South Africa](https://www.sciencedirect.com/science/article/pii/S0045653524007963#sec2)

# Authors
* Scott Baroni  
  - GitHub: [ArcaneWorm](https://github.com/ArcaneWorm)
  - Email: [sbaroni2004@gmail.com]
* Landon Escorcio
  - GitHub: [broncodev](https://github.com/broncodev)
  - Email: [landonyaya@gmail.com]
