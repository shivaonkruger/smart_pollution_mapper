import rasterio
import numpy as np

with rasterio.open("C:\geotif\data\satellite\delhi_no2.tif") as src:
    data = src.read(1)
    print("NO2 values:", data[~np.isnan(data)][:10])  # First 10 valid pixels