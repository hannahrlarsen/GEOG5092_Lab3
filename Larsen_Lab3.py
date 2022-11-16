import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import random
import numpy as np

def arrayfunc(samppoints):                
    np.array(samppoints.values())
    #This function returns a sample points layer for each watershed type as a numpy array.

path = "C:/Users/larsenh/Desktop/lab3.gpkg"

w08 = gpd.read_file(path, layer = 0)
w12 = gpd.read_file(path, layer = 1)
ssrugo = gpd.read_file(path, layer = 2)

for proj in [w08, w12]:
    projection = proj['geometry'].to_crs({'proj': 'cea'})
    proj.insert(5, 'area sq km', round((projection.area / 10**6), 0))
    totalpoints = proj['area sq km']
    proj.insert(6, 'point_total', totalpoints * 0.05)
    proj['point_total'] = proj['point_total'].astype('int64')
    
bounds_08 = w08.bounds
bounds_12 = w12.bounds
w08_new = pd.concat([w08, bounds_08], axis = 1)
w12_new = pd.concat([w12, bounds_12], axis = 1)

random.seed(0)

sample_points08 = {'point_id': [], 'geometry': [], 'watershed': []}
sample_points12 = {'point_id': [], 'geometry': [], 'watershed': []}

for i, row in w08_new.iterrows():
    ntemp = int(row['point_total'])
    for i in range(ntemp):
        intersects = False
        while intersects == False:
            x = random.uniform(row['minx'], row['maxx'])
            y = random.uniform(row['miny'], row['maxy'])
            point = Point(x, y)
            results = w08['geometry'].intersects(point)
            if True in results.unique():
                sample_points08['geometry'].append(Point((x, y)))
                sample_points08['point_id'].append(i)
                sample_points08['watershed'].append(row['HUC8'])
                intersects = True
                
for i, row in w12_new.iterrows():
    ntemp = int(row['point_total'])
    for i in range(ntemp):
        intersects = False
        while intersects == False:
            x = random.uniform(row['minx'], row['maxx'])
            y = random.uniform(row['miny'], row['maxy'])
            point = Point(x, y)
            results = w12['geometry'].intersects(point)
            if True in results.unique():
                sample_points12['geometry'].append(Point((x, y)))
                sample_points12['point_id'].append(i)
                sample_points12['watershed'].append(row['HUC12'])
                intersects = True
    
arrayfunc(sample_points08)
arrayfunc(sample_points12)   
    

df08 = pd.DataFrame(data = sample_points08)
w08_pointsgdf = gpd.GeoDataFrame(df08, geometry='geometry')

df12 = pd.DataFrame(data = sample_points12)
w12_pointsgdf = gpd.GeoDataFrame(df12, geometry='geometry')
w12_pointsgdf["string_12"] = w12_pointsgdf['watershed']
w12_pointsgdf = w12_pointsgdf.astype({'string_12':'string'})


empty_list = []
for index, row in w12_pointsgdf.iterrows():
    if '10190005' in row['string_12']:
        empty_list.append('10190005')
    elif '10190006' in row['string_12']:
        empty_list.append('10190006')
    elif '10190007' in row['string_12']:
        empty_list.append('10190007')
        
        
w12_w08 = pd.DataFrame(empty_list, columns = ['HUC08_watershed'])
w12_pointsgdf = w12_pointsgdf.join(w12_w08)
ssrugo = gpd.read_file(path, layer = 2)
ssrugo_gdf = gpd.GeoDataFrame(ssrugo, geometry='geometry')
ssrugo_proj = ssrugo_gdf.to_crs("epsg:3857")

w08_points_proj = w08_pointsgdf.set_crs('EPSG:26913')
w08_overlay = gpd.overlay(w08_points_proj, ssrugo, how='intersection')
w08_overlay = round((w08_overlay.groupby(['watershed']).mean()), 2)

w12_points_proj = w12_pointsgdf.set_crs('EPSG:26913')
w12_overlay = gpd.overlay(w12_points_proj, ssrugo, how='intersection')
w12_overlay = round((w12_overlay.groupby(['HUC08_watershed']).mean()), 2)

print("The mean aws for HUC08 watersheds 10190005, 10190006, and 10190007 using random points from HUC12 watersheds are: "
      + (str(w12_overlay.iloc[0, 1])) + ", " 
      + (str(w12_overlay.iloc[1, 1])) + ", and " 
      + (str(w12_overlay.iloc[2, 1])) + ".")

print("The mean aws for HUC08 watersheds 10190005, 10190006, and 10190007 using random points from HUC08 watersheds are: "
      + (str(w08_overlay.iloc[0, 1])) + ", " 
      + (str(w08_overlay.iloc[1, 1])) + ", and " 
      + (str(w08_overlay.iloc[2, 1])) + ".")


print("The conclusions from this random sampling is that there are differences "
      "between sampling in the HUC08 and HUC12 watershed polygons because "
      "they are different sizes. The randomly generated points could easily "
      "be located within different areas of the larger HUC08 watersheds "
      "that have different soil characteristics. Randomly generated points "
      "are helpful in providing a sample of data, but should not be relied "
      "on to provide an actual summary of the soil properties in each watershed.")



