# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 12:11:53 2021

@author: Rithvik Shindihatti
"""
from osgeo import gdal
from PIL import Image
import os

#from qgis.PyQt.QtCore import *
#from qgis.PyQt.QtGui import *
#from qgis.PyQt.QtWidgets import *


def create_tif_clippings(filename, output_path):
    dataset = gdal.Open(filename)
	

    # get GeoTransform of the image.
    geoTransform = dataset.GetGeoTransform()
    print(geoTransform)

    # get Projection of the image.
    projection = dataset.GetProjection()
    print(projection)

    # get co-ordinates of the upper left corner
    xmin = geoTransform[0]
    ymax = geoTransform[3]
    resolution = geoTransform[1]

	# get the xlen and ylen values
    xlen = resolution * dataset.RasterXSize
    ylen = resolution * dataset.RasterYSize

	# set the clipping size
    xsize, ysize = 4000*resolution, 4000*resolution

	#get the xdiv and ydiv values
    xdiv, ydiv = int(xlen/xsize), int(ylen/ysize)

	#create a list of x and y co-ordinates
    xsteps = [xmin + xsize * i for i in range(xdiv+1)]
    ysteps = [ymax - ysize * i for i in range(ydiv+1)]

    for i in range(xdiv):
        for j in range(ydiv):
            xmin = xsteps[i]
            xmax = xsteps[i+1]
            ymax = ysteps[j]
            ymin = ysteps[j+1]
		
            print("xmin: "+str(xmin))
            print("xmax: "+str(xmax))
            print("ymin: "+str(ymin))
            print("ymax: "+str(ymax))
            print("\n")
		
            gdal.Translate(output_path + "/clipping"+str(i)+"_"+str(j)+".tif", dataset, projWin = (xmin, ymax, xmax, ymin), xRes = resolution, yRes = -resolution)
            
    dataset = None
    
    return geoTransform, projection
    
def create_jpg_clippings(filename, output_path, progressBarClip):
    
    Image.MAX_IMAGE_PIXELS = None
    
    dataset = gdal.Open(filename)
    
    # get GeoTransform of the image.
    geoTransform = dataset.GetGeoTransform()
    print(geoTransform)
    
    # get Projection of the image.
    projection = dataset.GetProjection()
    print(projection)
    
    # get co-ordinates of the upper left corner
    xmin_p = geoTransform[0]
    ymax_p = geoTransform[3]
    resolution = geoTransform[1]
    
    #xlen_in_pixels, ylen_in_pixels = dataset.RasterXSize, dataset.RasterYSize
    
    gdal.Translate(os.path.join(output_path, "jpg_conversion.jpg"), dataset, format='jpeg')
    
    # Open jpg file
    if os.name == "nt":
        img = Image.open(os.path.normpath(os.path.join(output_path, "jpg_conversion").replace("\\\\","\\")))
    else:
        img = Image.open(os.path.join(output_path, "jpg_conversion.jpg"))

    xlen_in_pixels, ylen_in_pixels = img.size
    
    # set xmin and ymin values for jpg
    xmin_conv, ymin_conv = 0, 0 
    
    # set the clipping size
    xsize, ysize = 416, 416
    
    #get the xdiv and ydiv values
    xdiv, ydiv = int(xlen_in_pixels/xsize), int(ylen_in_pixels/ysize)
    
    #create a list of x and y co-ordinates
    xsteps = [xmin_conv + xsize * i for i in range(xdiv+1)]
    ysteps = [ymin_conv + ysize * i for i in range(ydiv+1)]
    
    for i in range(xdiv):
        for j in range(ydiv):
            xmin = xsteps[i]
            xmax = xsteps[i+1]
            ymin = ysteps[j]
            ymax = ysteps[j+1]
        
            print("xmin: "+str(xmin))
            print("xmax: "+str(xmax))
            print("ymin: "+str(ymin))
            print("ymax: "+str(ymax))
            print("\n")
        
            box = (xmin, ymin, xmax, ymax)
            clipping = img.crop(box)
            
            clipping.save(os.path.join(output_path, "clipping"+str(i)+"_"+str(j)+".jpg"), format='jpeg')
            
            progress = (((i*ydiv)+(j + 1)) / (xdiv*ydiv)) * 80
            progressBarClip.setValue(progress)
            
    dataset = None
    
    return geoTransform, projection
    
    
    
    
    
    
    
    
    
    

                

