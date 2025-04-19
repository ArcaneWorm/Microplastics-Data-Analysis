import pandas as pd
import time
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pycountry_convert as pc

# Microplastics Data Analysis
# By Scott Baroni and Landon Escorcio at Cal State Polytechnic - Pomona

country_fixes = {               # So that pycountry_convert doesn't mark these countries as Unknown
    "UK": "United Kingdom",
    "Scotland": "United Kingdom",
    "England": "United Kingdom",
    "Korea": "South Korea",
}

# Convert countries to continent for additional column
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

ms = time.time()
# Use only columns we need
df = pd.read_csv("samples_geocoded.csv", usecols=["Sample_ID","Location","Countries","Source","Concentration","Concentration_Units"])

# Remove NA values
df.dropna(axis=0, subset=["Countries", "Concentration", "Source"], how="any", inplace=True)

# Create continent column
df["Continent"] = df["Countries"].apply(get_continent)

df.info() # Info about dataframe
print()

# Convert 'Concentration' column to numeric (in order to remove those that are not a number)
df["Concentration"] = pd.to_numeric(df["Concentration"], errors="coerce")

# Drop rows where 'Concentration' is NaN
df = df.dropna(subset=["Concentration"])

# Drop rows where Concentration_Units is not in particles/volume
# TODO Discuss whether this is the right option.
df = df[~df["Concentration_Units"].isin(["ug/m3", "ug/g"])]

i = 0
concentrations = df["Concentration"].to_list()
sources=df["Source"].to_list()
bottled_avg=0
tap_avg=0
# Unit Conversions TODO Verify
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
    
    # # Add to averages for bar charts      # Opted for method .mean() to find avg TODO Discuss if valid
    # if sources[i] == "bottled water":
    #     bottled_avg+=concentrations[i]
    # else:
    #     tap_avg+=concentrations[i]
    # i+=1

# Replace with new converted units, all now in particles/L
df["Concentration"] = concentrations
df["Concentration_Units"] = "particles/L"


# Drop major outliers in concentration using IQR
# TODO Discuss if this is reasonable
Q1 = df["Concentration"].quantile(0.25)
Q3 = df["Concentration"].quantile(0.75)
IQR = Q3 - Q1

# Bounds for outliers
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
intial_rows = len(df)

df = df[(df["Concentration"] >= lower_bound) & (df["Concentration"] <= upper_bound)]

# Check how many rows were removed
print(f"Outlier rows removed: {intial_rows - len(df)}")
print(f"Remaining rows: {len(df)}")
print()


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

# Create/update csv for cleaned up data
# df.to_csv("output.csv",index=False)

# Bar chart comparing bottled vs tap water
x = ['Tap Water', 'Bottled Water']
y = [tap_avg, bottled_avg]

plt.figure(figsize=(12, 7))
plt.bar(x, y, color=['skyblue', 'cornflowerblue'])
plt.title('Average Microplastic Concentration in Drinking Water')
plt.xlabel('Water Source')
plt.ylabel('Concentration (particles/L)')
plt.show()

# Bar chart with error bars (based on standard deviation) to represent uncertainty
# TODO Discuss if this is preferred over previous bar chart
std_concentration = df.groupby("Source")["Concentration"].std()
plt.figure(figsize=(12, 7))
plt.bar(x, y, yerr=std_concentration, capsize=5, color=['skyblue', 'cornflowerblue'])
plt.title('Average Microplastic Concentration (with Standard Deviation)')
plt.xlabel('Water Source')
plt.ylabel('Concentration (particles/L)')
plt.show()

# Bar chart comparing countries and average concentration
# Filter out entries with only 'UK' as country TODO Discuss any alternative solutions
df_filtered = df[df["Countries"] != "UK"]
# Group data by country and calculate average concentration
avg_concen_by_country = df_filtered.groupby("Countries")["Concentration"].mean()
x = avg_concen_by_country.index     # Countries
y = avg_concen_by_country.values    # Average concentrations

plt.figure(figsize=(12, 7))
plt.bar(x, y, color='cornflowerblue')   # TODO Discuss color choices :)
plt.title('Countries and Concentration')
plt.xlabel('Country')
plt.ylabel('Concentration (particles/Liter)')
plt.xticks(rotation=45, ha="right") # Make country names readable by rotating 45 degrees and setting horizontal alignment to right
plt.subplots_adjust(bottom=0.23)
plt.show()

# Bar chart comparing average concentration by continent
# TODO Discuss if this is a useful visualization
avg_concen_by_cont = df.groupby("Continent")["Concentration"].mean()
x = avg_concen_by_cont.index    # Continents
y = avg_concen_by_cont.values   # Average concentrations

plt.figure(figsize=(12, 7))
plt.bar(x, y, color='cornflowerblue')
plt.title('Average Microplastic Concentration by Continent')
plt.xlabel('Continent')
plt.ylabel('Average Concentration (particles/L)')
plt.xticks(rotation=45)
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