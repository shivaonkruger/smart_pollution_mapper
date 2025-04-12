import json
import numpy as np
import matplotlib.pyplot as plt
import rasterio
import folium
from folium import plugins
import branca.colormap as cm

def plot_satellite_data():
    # Read the NO2 data
    with rasterio.open('data/satellite/delhi_no2.tif') as src:
        no2_data = src.read(1)
        transform = src.transform
        
    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot the NO2 data
    im1 = ax1.imshow(no2_data, cmap='viridis')
    ax1.set_title('NO2 Concentration (mol/m²)')
    plt.colorbar(im1, ax=ax1)
    
    # Plot the histogram
    ax2.hist(no2_data.flatten(), bins=50)
    ax2.set_title('NO2 Value Distribution')
    ax2.set_xlabel('NO2 Concentration')
    ax2.set_ylabel('Frequency')
    
    plt.tight_layout()
    plt.savefig('data/satellite/no2_visualization.png')
    plt.close()
    
    return no2_data, transform

def plot_ground_data():
    # Read the PM2.5 data
    with open('data/ground/delhi_pm25.json') as f:
        pm25_data = json.load(f)
    
    # Extract coordinates and values
    lats = [point['coordinates']['latitude'] for point in pm25_data['results']]
    lons = [point['coordinates']['longitude'] for point in pm25_data['results']]
    values = [point['value'] for point in pm25_data['results']]
    
    # Create a map centered on Delhi
    m = folium.Map(location=[28.6, 77.2], zoom_start=11)
    
    # Create a color scale
    colormap = cm.LinearColormap(
        colors=['green', 'yellow', 'red'],
        vmin=min(values),
        vmax=max(values),
        caption='PM2.5 (µg/m³)'
    )
    
    # Add points to the map
    for lat, lon, value in zip(lats, lons, values):
        folium.CircleMarker(
            location=[lat, lon],
            radius=6,
            color=colormap(value),
            fill=True,
            fill_color=colormap(value),
            popup=f'PM2.5: {value:.1f} µg/m³'
        ).add_to(m)
    
    # Add the color scale to the map
    colormap.add_to(m)
    
    # Save the map
    m.save('data/ground/pm25_map.html')
    
    # Create a time series plot
    times = [point['date']['local'] for point in pm25_data['results']]
    plt.figure(figsize=(12, 6))
    plt.plot(times, values, 'o-')
    plt.title('PM2.5 Time Series')
    plt.xlabel('Time')
    plt.ylabel('PM2.5 (µg/m³)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('data/ground/pm25_timeseries.png')
    plt.close()
    
    return lats, lons, values

def main():
    print("Visualizing satellite data...")
    no2_data, transform = plot_satellite_data()
    print("Satellite visualization saved to data/satellite/no2_visualization.png")
    
    print("\nVisualizing ground sensor data...")
    lats, lons, values = plot_ground_data()
    print("Ground sensor visualizations saved to:")
    print("- data/ground/pm25_map.html (interactive map)")
    print("- data/ground/pm25_timeseries.png (time series)")
    
    print("\nData Statistics:")
    print(f"NO2 Data: min={np.min(no2_data):.6f}, max={np.max(no2_data):.6f}, mean={np.mean(no2_data):.6f}")
    print(f"PM2.5 Data: min={min(values):.1f}, max={max(values):.1f}, mean={np.mean(values):.1f}")

if __name__ == "__main__":
    main() 