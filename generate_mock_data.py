import json
import random
import numpy as np
from datetime import datetime, timedelta
import rasterio
from rasterio.transform import from_origin

def generate_mock_sensor_data(num_sensors=20, days=1):
    # Delhi's approximate boundaries
    min_lat, max_lat = 28.4, 28.7
    min_lon, max_lon = 77.1, 77.4
    
    # Known monitoring stations in Delhi
    stations = [
        {"name": "US Embassy", "lat": 28.6, "lon": 77.2},
        {"name": "Anand Vihar", "lat": 28.65, "lon": 77.3},
        {"name": "Punjabi Bagh", "lat": 28.66, "lon": 77.12},
        {"name": "R K Puram", "lat": 28.56, "lon": 77.18},
        {"name": "Mandir Marg", "lat": 28.63, "lon": 77.2}
    ]
    
    # Generate data for each station
    results = []
    base_date = datetime(2023, 10, 1)
    
    for station in stations:
        for day in range(days):
            for hour in range(24):
                # Base PM2.5 value with some randomness
                base_value = random.uniform(100, 200)
                # Add daily pattern (higher during morning/evening)
                if hour in [8, 9, 17, 18]:  # Rush hours
                    value = base_value * 1.3
                else:
                    value = base_value
                
                # Add some noise
                value += random.uniform(-10, 10)
                
                # Ensure value is within realistic range
                value = max(50, min(300, value))
                
                current_date = base_date + timedelta(days=day, hours=hour)
                
                results.append({
                    "location": station["name"],
                    "parameter": "pm25",
                    "value": round(value, 1),
                    "date": {
                        "utc": current_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "local": (current_date + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%dT%H:%M:%S+05:30")
                    },
                    "coordinates": {
                        "latitude": station["lat"],
                        "longitude": station["lon"]
                    }
                })
    
    return {
        "meta": {
            "name": "Delhi_PM25_Mock_Data",
            "date_generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "num_sensors": len(stations),
            "days": days
        },
        "results": results
    }

def generate_mock_satellite_data():
    # Create a 34x34 grid (matching your earlier output)
    height, width = 34, 34
    
    # Create a base NO2 concentration map
    # Higher values near city center (around 28.6N, 77.2E)
    base_no2 = np.zeros((height, width))
    
    # Add some spatial patterns
    for i in range(height):
        for j in range(width):
            # Create a gradient from center
            dist_from_center = np.sqrt((i - height/2)**2 + (j - width/2)**2)
            base_value = 0.0002 * np.exp(-dist_from_center/10)  # Exponential decay
            
            # Add some noise
            noise = np.random.normal(0, 0.00001)
            base_no2[i,j] = max(0, base_value + noise)
    
    # Create a GeoTIFF file
    transform = from_origin(77.1, 28.7, 0.01, 0.01)  # 0.01 degree resolution
    
    with rasterio.open(
        'data/satellite/delhi_no2.tif',
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=1,
        dtype=rasterio.float64,
        crs='EPSG:4326',
        transform=transform
    ) as dst:
        dst.write(base_no2, 1)
    
    return base_no2

# Generate and save the ground sensor data
mock_data = generate_mock_sensor_data(num_sensors=5, days=1)
with open("data/ground/delhi_pm25.json", "w") as f:
    json.dump(mock_data, f, indent=2)

# Generate and save the satellite data
no2_data = generate_mock_satellite_data()

print("Mock data generated and saved:")
print("- Ground sensor data: data/ground/delhi_pm25.json")
print("- Satellite data: data/satellite/delhi_no2.tif") 