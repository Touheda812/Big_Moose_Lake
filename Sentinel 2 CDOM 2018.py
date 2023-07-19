#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# pip install earthengine-api


# In[1]:


import ee
import geemap
import pandas as pd
import numpy as np 
from matplotlib import pyplot
from io import StringIO


#ee.Authenticate()  # Only needed for the first time
ee.Initialize()
Map= geemap.Map()


# In[ ]:





# In[2]:


# import ee

# # Initialize the Earth Engine API
# ee.Initialize()

# # Define the image collection
# s2 = ee.ImageCollection('COPERNICUS/S2_SR')

# # Function to extract the date from the system:time_start property
# def get_date(image):
#     return ee.Date(image.get('system:time_start'))

# # Map the function over the ImageCollection to get a list of dates
# dates = s2.aggregate_array('system:time_start')

# # Get the list of dates
# date_list = dates.getInfo()

# # Print the list of dates
# print('List of dates:', date_list)


# In[3]:


sentinel2_bands =['B1','B2','B3','B4','B5','B6','B8','B8A','B11']
STD_NAMES = ['Aerosols', 'Blue', 'Green', 'Red', 'RedEdge1','RedEdge2','RedEdge4','NIR','SWIR1']


# In[4]:


lake = ee.FeatureCollection('projects/ee-touheda-khanom/assets/samplinglakes') \
    .filter(ee.Filter.eq('GNIS_Name', 'Big Moose Lake'))


# In[5]:


def cdom(img):
    cdo = img.expression("(20.3 - 10. * (b2 / b3) - 2.4 * (b3 / b4))", {
        'b1': img.select('Aerosols'),
        'b2': img.select('Blue'),
        'b3': img.select('Green'),
        'b4': img.select('Red')
    }).rename("CO")
    
    bad2 = cdo.where(cdo.gte(0), 1).rename("bad2")
    co = cdo.multiply(bad2).rename("CO")
    mask = co.neq(0)

    return img.addBands(co).clip(lake).updateMask(mask)


# In[8]:


# Define the image collection
s2 = ee.ImageCollection('COPERNICUS/S2_SR')\
       .select(sentinel2_bands, STD_NAMES) \
       .map(cdom)\
       .filterBounds(lake)


# In[9]:


def station_mean(img):  
    mean = img.reduceRegion(reducer=ee.Reducer.mean(), geometry=lake, scale=30).get('CO')
    return img.set('date', img.date().format()).set('CDOM',mean)

station_reduced_imgs = s2.map(station_mean)
nested_list = station_reduced_imgs.reduceColumns(ee.Reducer.toList(2), ['date','CDOM']).values().get(0)
df = pd.DataFrame(nested_list.getInfo(), columns=['date','CDOM'])

df = pd.DataFrame(nested_list.getInfo(), columns=['date','CDOM'])
pd.set_option('display.max_rows', None)

df


# In[ ]:





# In[ ]:




