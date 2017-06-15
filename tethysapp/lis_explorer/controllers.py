from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tethys_sdk.gizmos import *
from django.http import JsonResponse, HttpResponse
import json,shapely.geometry
from lis import *
from utilities import *

LIS_DIRECTORY = "/lis/"

@login_required()
def home(request):
    """
    Controller for the app home page.
    """

    display_vars = {'Qs': 'Runoff', 'rainfall': 'Rainfall', 'total_precip': 'Total Precip'}

    var_metadata, cbar = get_range(LIS_DIRECTORY, display_vars, 20)

    var_metadata = json.dumps(var_metadata)
    cbar = json.dumps(cbar)

    var_list = get_lis_variables(LIS_DIRECTORY)

    dates_list = get_lis_dates(LIS_DIRECTORY)

    slider_max = len(dates_list)

    first_day = dates_list[0][0]
    variable_select = SelectInput(display_text='Select a Variable',
                                  name='variable-select',
                                  options=var_list, )

    date_select = SelectInput(display_text='Select a Date',
                              name='date-select',
                              options=dates_list, )

    context = {
        'host': 'http://%s' % request.get_host(),
        'variable_select': variable_select,
        'date_select': date_select,
        'first_day': first_day,
        'slider_max': slider_max,
        'display_vars': display_vars,
        'var_metadata': var_metadata,
        'cbar': cbar
    }

    return render(request, 'lis_explorer/home.html', context)

@login_required()
def get_ts(request):

    return_obj = {}

    if request.is_ajax() and request.method == 'POST':
        variable = request.POST["variable-select"]
        variable_info = get_variable_info(LIS_DIRECTORY,variable)


        pt_coords = request.POST["point-lat-lon"]
        poly_coords = request.POST['poly-lat-lon']
        shp_bounds = request.POST['shp-lat-lon']


        if pt_coords:
            graph = get_pt_timeseries(LIS_DIRECTORY,variable,pt_coords)
            graph = json.loads(graph)
            if graph["success"] == "success":
                return_obj["values"] = graph["values"]
                return_obj["location"] = graph["point"]
                return_obj["display_name"] = variable_info["display_name"]
                return_obj["units"] = variable_info["units"]
                return_obj["variable"] = variable

                return_obj["success"] = "success"

            if graph["success"] != "success":
                return_obj["success"] = graph["success"]


        if poly_coords:
            poly_geojson = json.loads(poly_coords)
            shape_obj = shapely.geometry.asShape(poly_geojson)
            poly_bounds = shape_obj.bounds
            graph = get_poly_timeseries(LIS_DIRECTORY,variable,poly_bounds)
            graph = json.loads(graph)
            if graph["success"] == "success":
                return_obj["values"] = graph["values"]
                return_obj["location"] = graph["bounds"]
                return_obj["display_name"] = variable_info["display_name"]
                return_obj["units"] = variable_info["units"]
                return_obj["variable"] = variable

                return_obj["success"] = "success"

            if graph["success"] != "success":
                return_obj["success"] = graph["success"]

        if shp_bounds:
            shp_bounds = tuple(shp_bounds.split(','))
            graph = get_poly_timeseries(LIS_DIRECTORY,variable,shp_bounds)
            graph = json.loads(graph)
            if graph["success"] == "success":
                return_obj["values"] = graph["values"]
                return_obj["location"] = graph["bounds"]
                return_obj["display_name"] = variable_info["display_name"]
                return_obj["units"] = variable_info["units"]
                return_obj["variable"] = variable

                return_obj["success"] = "success"

            if graph["success"] != "success":
                return_obj["success"] = graph["success"]



    return JsonResponse(return_obj)