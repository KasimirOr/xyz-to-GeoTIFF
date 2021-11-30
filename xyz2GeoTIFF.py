
from pylab import *
from osgeo import osr, gdal
import numpy as numpy
import os
import ee
import ogr

# input setup



#working_directory = (r'D:\Projekte\EBA\Daten\Test')
input_dir = (r'D:\Projekte\EBA\Daten\input_xyz_4')
output_dir = (r'D:\Projekte\EBA\Daten\output_tif')

counter = 0
list_files = os.listdir(input_dir);

# main
for file in list_files:
    # define output file name
    print(f"working on file: {file} {counter} /{len(list_files)}")
    counter = counter + 1
    outfile = os.path.join(output_dir, file.replace(".xyz", ".tif"))

    # UTM ZONE 32, WG84 data
    data = genfromtxt(os.path.join(input_dir, file))
    #data =genfromtxt(f'D:\Projekte\EBA\Daten\Test\{file}')
    x=data[:,0]
    y=data[:,1]
    z=data[:,2]

    # find the extent and difference
    #xmin=min(x);xmax=max(x)
    #ymin=min(y);ymax=max(y)
    xmax = max(x)
    xmin = min(x)
    ymin = min(y)
    ymax = max(y)
    mdx=abs(diff(x))
    mdy=abs(diff(y))

    # determine dx and dy from the median of all the non-zero difference values
    dx=median(mdx[where(mdx>0.0)[0]])
    dy=median(mdy[where(mdy>0.0)[0]])

    #construct x,y,z of complete grid
    #xi=arange(xmin-(dx/2),xmax+(dx/2),dx)
    #yi=arange(ymin-(dy/2),ymax+(dy/2),dy)
    xi=arange(xmin,xmax+dx,dx)

    # add one additional row to grid
    yi=arange(ymin,ymax+(2*dy),dy)
    # fill grid with NaN's
    zi=ones((len(yi),len(xi)))*NaN

    # calculate indices in full grid (zi) to stick the input z values
    ix=numpy.round((x-xmin)/dx).astype(int)
    #ix_new = ix + 1
    iy=numpy.round((y-ymax)/dy).astype(int)
    # create
    # create indices for rows but start at 2nd row
    iy_new = iy - 1

    # fill in with z values, using the y indice starting at 2nd row
    zi[iy_new,ix]=z
    # copy values from last row to first row
    zi[0,] = zi[-1,]

    # subset array, delete last row
    zi = np.delete(zi, 0, 0)
    #zi = zi[1:, :]


    zi=flipud(zi)

    # write as 32-bit GeoTIFF using GDAL
    ny,nx = zi.shape
    driver = gdal.GetDriverByName("GTiff")
    ds = driver.Create(outfile, nx, ny, 1, gdal.GDT_Float32)

    # top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution
    ds.SetGeoTransform( [ xmin - (dx/2), dx, 0, ymax + (dy/2), 0, -dy ] )
    # set the reference info
    srs = osr.SpatialReference()

    # UTM zone 32, North=1
    # srs.SetUTM(32,1)
    srs.SetFromUserInput("EPSG:25832")
    ds.SetProjection( srs.ExportToWkt() )

    # write the data to a single band
    ds.GetRasterBand(1).WriteArray(zi)
    # close
    ds = None
    

