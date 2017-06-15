from netCDF4 import Dataset
import os
import gdal,gdalconst
import osr
import requests
from datetime import datetime, timedelta


def create_lis_geotiff(filename,var_name,output_dir):
    nc_fid = Dataset(filename)
    nc_var = nc_fid.variables
    lats = nc_var['lat'][:]
    lon = nc_var['lon'][:]
    field = nc_var[var_name][:]
    xsize, ysize, GeoT, NDV, Projection = get_netcdf_info(filename, var_name)
    dir = os.path.join(output_dir,'')
    time = nc_var['time'][:]

    for timestep,v in enumerate(time):

        current_time_step = nc_var[var_name][timestep,:,:]
        filename = datetime.fromtimestamp(int(v)).strftime('%Y_%m_%d')

        data = nc_var[var_name][timestep,:,:]
        data = data[::-1,:]
        driver = gdal.GetDriverByName('GTiff')
        DataSet = driver.Create(dir + filename + '_'+var_name+'.tif', xsize, ysize, 1,
                                gdal.GDT_Float32)

        DataSet.SetGeoTransform(GeoT)
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        DataSet.SetProjection(srs.ExportToWkt())

        DataSet.GetRasterBand(1).WriteArray(data)
        DataSet.GetRasterBand(1).SetNoDataValue(NDV)
        DataSet.FlushCache()

        DataSet = None

def get_netcdf_info(filename,var_name):
    nc_file = gdal.Open(filename)

    # There are more than two variables, so specifying the lwe_thickness variable

    if nc_file.GetSubDatasets() > 1:
        subdataset = 'NETCDF:"' + filename + '":' + var_name  # Specifying the subset name
        src_ds_sd = gdal.Open(subdataset)  # Reading the subset
        NDV = src_ds_sd.GetRasterBand(1).GetNoDataValue()  # Get the nodatavalues
        xsize = src_ds_sd.RasterXSize  # Get the X size
        ysize = src_ds_sd.RasterYSize  # Get the Y size
        GeoT = src_ds_sd.GetGeoTransform()  # Get the GeoTransform
        Projection = osr.SpatialReference()  # Get the SpatialReference
        Projection.ImportFromWkt(src_ds_sd.GetProjectionRef())  # Setting the Spatial Reference

        src_ds_sd = None  # Closing the file
        nc_file = None  # Closing the file

        return xsize, ysize, GeoT, NDV, Projection

#Upload GeoTiffs to geoserver
def upload_tiff(dir,geoserver_rest_url,workspace):


    headers = {
        'Content-type': 'image/tiff',
    }

    for file in os.listdir(dir):
        store_name = file.split('.')[0]
        data = open(dir+file,'rb').read()
        request_url = '{0}/workspaces/{1}/coveragestores/{2}/file.geotiff'.format(geoserver_rest_url, workspace,
                                                                                  store_name)  # Creating the rest url
        requests.put(request_url, headers=headers, data=data,
                     auth=('admin', 'geoserver'))