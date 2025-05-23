# Microplastics Data Analysis on GitHub (for collaboration)
# By Scott Baroni and Landon Escorcio 
# at Cal State Polytechnic University - Pomona

# ===========================
# SETUP
# ===========================

# The imports are pretty standard for data analysis. 
# We also included time so we could have some runtime complexity
# data and make sure nothing strange was happening with
# the calculations.

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import time
import pycountry_convert as pc

ms = time.time()

# This line fixes an error with pycountry_convert which
# would mark these countries as Unknown
country_fixes = {           
    "UK": "United Kingdom",
    "Scotland": "United Kingdom",
    "England": "United Kingdom",
    "Korea": "South Korea",
}

# Grouping countries by continent for an 
# additional, broader column.

# Our code also includes error handling as is good practice
# for professional programming
def get_continent(country_name):
    try:
        # Make any fixes
        country_name = country_fixes.get(country_name, country_name)
        # Convert country to corresponding continent
        country_code = pc.country_name_to_country_alpha2(country_name, cn_name_format="default")
        continent_code = pc.country_alpha2_to_continent_code(country_code)
        # Map continent codes to full continent names
        continent_name = {
            "AF": "Africa",
            "AS": "Asia",
            "EU": "Europe",
            "NA": "North America",
            "SA": "South America",
            "OC": "Oceania"
        }
        return continent_name.get(continent_code, "Unknown")
    except:
        print("Unknown: ",country_name)
        return "Unknown"

# Reading in only columns we need from the orgiginal dataset.
# Important columns include Location, Concentration, and Units.
df = pd.read_csv("samples_geocoded.csv", usecols=["Sample_ID","Location","Countries","Source","Concentration","Concentration_Units"])

# Remove rows with NaN values
df.dropna(axis=0, subset=["Countries", "Concentration", "Source", "Concentration_Units"], how="any", inplace=True)

# Group United Kingdom regions into UK category for 
# sake of consistency and clearer analysis
df["Countries"] = df["Countries"].replace({
    "England": "UK",
    "Scotland": "UK",
    "Wales": "UK",
    "Northern Ireland": "UK"
})

# ===========================
# DATA IMPUTATION
# ===========================
# Impute more MP concentration data for Africa.

# Africa did not have enough datapoints originally,
# Which we solved by adding from another dataset.
# This turned out to be worthwhile. Some visualizations changed
# and became more accurate as a result of this change.
df_to_impute = pd.read_csv("SouthAfricaWaterMP.csv", usecols=["Concentration (particles/L)"])
df_to_impute.rename(columns={"Concentration (particles/L)": "Concentration"}, inplace=True)

# In order to add the data, we added required columns.
df_to_impute["Sample_ID"] = None
df_to_impute["Location"] = "Gauteng, South Africa"
df_to_impute["Countries"] = "South Africa"
df_to_impute["Source"] = "tap water"
df_to_impute["Concentration_Units"] = "particles/L"

df.to_csv("output2.csv",index=False)
# Then, concatenated to original dataframe.
df = pd.concat([df, df_to_impute], ignore_index=True)

# Create continents column.
df["Continents"] = df["Countries"].apply(get_continent)

# ===========================
# STRUCTURING UNITS
# ===========================
# Converted 'Concentration' column to numeric 
# (in order to remove those values that are not a number)
df["Concentration"] = pd.to_numeric(df["Concentration"], errors="coerce")

# Drop rows where Concentration_Units is not in particles/volume
# For example, it seems that ug refers to "micrograms".
# It was not clear how this measurement compares to our definition
# of a single "particle", so these rows were removed.
df = df[~df["Concentration_Units"].isin(["ug/m3", "ug/g"])]

i = 0
concentrations = df["Concentration"].to_list()
sources=df["Source"].to_list()
bottled_avg=0
tap_avg=0
# Manual Unit Conversions
# We used standard lists to convert between units so that
# verification of the numbers was easier, as opposed to 
# pandas functions that may have unexpected behavior.
for x in df["Concentration_Units"].to_list():
    if x == "particles/0.33L":
        concentrations[i] = concentrations[i]*3
    elif x == "particles/m3":
        concentrations[i] = concentrations[i]/1000
    elif x == "particles/50 L":
        concentrations[i] = concentrations[i]/50
    elif x == "particles/50 L":
        concentrations[i] = concentrations[i]/50
    elif x == "particles/bottle":
        # Assuming an average bottle holds around .5 liter
        concentrations[i] = concentrations[i]*2

# Replaced columns with new converted units, all now in particles/L.
df["Concentration"] = concentrations
df["Concentration_Units"] = "particles/L"

# ===========================
# HANDLING OUTLIERS
# ===========================
# Drop major outliers in concentration using the standard IQR method.
# Lower bound should not be reached in practice.
Q1 = df["Concentration"].quantile(0.25)
Q3 = df["Concentration"].quantile(0.75)
IQR = Q3 - Q1

# Bounds for outliers.
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
initial_rows = len(df)

df = df[(df["Concentration"] >= lower_bound) & (df["Concentration"] <= upper_bound)]

# Print how many rows were removed.
print(f"Outlier rows removed: {initial_rows - len(df)}")
print(f"Remaining rows: {len(df)}")
df.info()
print()

# ===========================
# CLEANED DATA & SKEWNESS
# ===========================
# Create/update csv for cleaned up data.
df.to_csv("output.csv",index=False)

# Find skewness of tap and bottled water.
tap_skew = df[df["Source"] == "tap water"]["Concentration"].skew()
bottled_skew = df[df["Source"] == "bottled water"]["Concentration"].skew()
print(f"Tap water skew: {tap_skew:.4f}")
print(f"Bottled water skew: {bottled_skew:.4f}")

# ===========================
# VISUALIZATIONS
# ===========================
# These visualizations use good practice methods, such as colorblind
# friendly colors, legible font sizes, and barcharts that start from 0.
# We are now ready to run the code.

# Averages for bottled and tap concentrations
# Filter only water data
df_tap = df[df["Source"] == "tap water"]
df_bottled = df[df["Source"] == "bottled water"]

# Calculate averages
bottled_avg = np.mean(df_bottled["Concentration"])
tap_avg = np.mean(df_tap["Concentration"])

print("Bottled Average: ",bottled_avg)
print("Tap Average: ",tap_avg)
print()

# Time
n = (time.time() - ms)
print("In seconds:",n)

# Bar chart comparing bottled vs tap water
x = ['Tap Water', 'Bottled Water']
y = [tap_avg, bottled_avg]

plt.rcParams.update({'font.size': 20})

plt.figure(figsize=(12, 7))
plt.bar(x, y, color=['skyblue', 'cornflowerblue'])
plt.title('Average Microplastic Concentration in Drinking Water')
plt.xlabel('Water Source')
plt.ylabel('Concentration (particles/L)')
plt.show()

# Bar chart with error bars (based on standard deviation) to represent uncertainty
std_concentration = df.groupby("Source")["Concentration"].std()
plt.figure(figsize=(12, 7))
plt.bar(x, y, yerr=std_concentration, capsize=5, color=['skyblue', 'cornflowerblue'])
plt.title('Average Microplastic Concentration (with Standard Deviation)')
plt.xlabel('Water Source')
plt.ylabel('Concentration (particles/L)')
plt.show()

# Bar chart comparing countries and average concentration
# Group data by country and calculate average concentration
avg_concen_by_country = df.groupby("Countries")["Concentration"].mean()
x = avg_concen_by_country.index     # Countries
y = avg_concen_by_country.values    # Average concentrations

plt.figure(figsize=(12, 7))
plt.bar(x, y, color='cornflowerblue')
plt.title('Countries and Concentration')
plt.xlabel('Country')
plt.ylabel('Concentration (particles/Liter)')
plt.xticks(rotation=45, ha="right", fontsize=12) # Make country names readable by rotating 45 degrees and setting horizontal alignment to right
plt.subplots_adjust(bottom=0.23)
plt.show()

# Bar chart comparing average concentration by continent
avg_concen_by_cont = df.groupby("Continents")["Concentration"].mean()
x = avg_concen_by_cont.index    # Continents
y = avg_concen_by_cont.values   # Average concentrations

plt.figure(figsize=(12, 7))
plt.bar(x, y, color='cornflowerblue')
plt.title('Average Microplastic Concentration by Continent')
plt.xlabel('Continent')
plt.ylabel('Average Concentration (particles/L)')
plt.xticks(rotation=45, fontsize=12)
plt.subplots_adjust(bottom=0.23)
plt.show()

# Kernel Density Estimate (KDE) plot/density curve comparing density of concentration in tap vs bottled
plt.figure(figsize=(12, 7))
sns.kdeplot(df[df["Source"] == "tap water"]["Concentration"], label="Tap Water", fill=True)
sns.kdeplot(df[df["Source"] == "bottled water"]["Concentration"], label="Bottled Water", fill=True)
plt.title("Density Curve of Microplastic Concentration")
plt.xlabel("Concentration (particles/L)")
plt.ylabel("Density")
plt.legend()
plt.show()