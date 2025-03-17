import pandas as pd
import time
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

ms = time.time()
df = pd.read_csv("samples_geocoded.csv")
# list of unneeded columns to remove
cols_to_remove = [
    "DOI", "Subsample_ID", "Color_Transparent", "Color_Blue", "Color_Red", "Color_Brown", "Color_Green", "Color_Orange", "Color_White",
    "Color_Yellow", "Color_Pink", "Color_Black", "Color_Other",

    "Material_PEST", "Material_PE", "Material_PP", "Material_PA", "Material_PE_PS", "Material_PS", "Material_CA",
    "Material_PVC", "Material_ER", "Material_PAM", "Material_PET", "Material_PlasticAdditive", "Material_PBT",
    "Material_PU", "Material_PET_PEST", "Material_PAN", "Material_Silicone", "Material_Acrylic", "Material_Vinyl",
    "Material_Vinyon", "Material_Other", "Material_PA_ER", "Material_PTT", "Material_PE_PP", "Material_PPS",
    "Material_Rayon", "Material_PAA", "Material_PMPS", "Material_PI", "Material_Olefin", "Material_Styrene_Butadiene",
    "Material_PBA", "Material_PMMA", "Material_Cellophane", "Material_SAN", "Material_PC", "Material_PDMS",
    "Material_PLA", "Material_PTFE", "Material_SBR", "Material_PET_Olefin", "Material_PES", "Material_ABS",
    "Material_LDPE", "Material_PEVA", "Material_AR", "Material_PVA", "Material_PPE",

    "Morphology_Fragment", "Morphology_Fiber", "Morphology_Nurdle", "Morphology_Film", "Morphology_Foam",
    "Morphology_Sphere", "Morphology_Line", "Morphology_Bead", "Morphology_Sheet", "Morphology_Film_Fragment",
    "Morphology_Rubbery_Fragment",

    "Size_3000um", "Size_2_5mm", "Size_1_5mm", "Size_1_2mm", "Size_0.5_1mm", "Size_less_than_0.5mm", "Size_500um",
    "Size_300_500um", "Size_125_300um", "Size_100_500um", "Size_greater_than_100um", "Size_50_150um",
    "Size_50_100um", "Size_50um", "Size_45_125um", "Size_greater_than_25um", "Size_20um_5mm", "Size_20_100um",
    "Size_20_50um", "Size_10_50um", "Size_10_45um", "Size_10_20um", "Size_greater_than_10um", "Size_8_316um",
    "Size_5_100um", "Size_5_10um", "Size_4_10um", "Size_1.5_5um", "Size_less_than_1.5um", "Size_1_100um",
    "Size_1_50um", "Size_1_10um", "Size_1_5um", "Size_110_124nm", "Size_0_20um",

    "Approximate_Latitude", "Approximate_Longitude" ]

df.drop(columns=cols_to_remove, axis=1, inplace=True)

# remove NA values
df.dropna(axis=0, subset=["Countries", "Concentration", "Source"], how="any", inplace=True)

df.info() # info about dataframe

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
    
    # Add to averages for bar charts
    if sources[i] == "bottled water":
        bottled_avg+=concentrations[i]
    else:
        tap_avg+=concentrations[i]
    i+=1
    
bottled_avg = bottled_avg/df["Source"].size
tap_avg = tap_avg/df["Source"].size
print("bottled avg",bottled_avg)
print("tap avg",tap_avg)
print()

# Replace with new converted units, all now in particles/L
df["Concentration"] = concentrations
df["Concentration_Units"] = "particles/L"

n = (time.time() - ms)
print("In seconds:",n)

# Bar chart comparing bottled vs tap water
plt.figure(figsize=(6, 6))
#plt.bar(df["Source"], df["Concentration"])
plt.bar(df["Countries"], df["Concentration"])
plt.title('Countries and Concentration')
plt.xlabel('Country')
plt.ylabel('Concentration (particles/Liter)')
plt.show()

df.to_csv("output.csv",index=False)

x = ['Tap', 'Bottled']
y = [tap_avg, bottled_avg]

plt.bar(x, y)
plt.title('Tap vs Bottled water contaminant amount')
plt.xlabel('Water Source')
plt.ylabel('Particles/Liter')
plt.show()