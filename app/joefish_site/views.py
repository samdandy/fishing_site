from django.shortcuts import render
from datetime import datetime
from joefish_site.database.query import get_flow_rate_graph, get_wind_speed_graph, get_temp_graph,get_wind_direction_table
from django.core.cache import cache
from joefish_site.utils.misc import execute_threaded_queries

def home(request):
    current_date = datetime.now().date()
    refresh = request.GET.get("refresh")
    if refresh:
        cache.delete_many([
            "flow_rate_graph",
            "wind_speed_graph",
            "temp_graph",
            "wind_direction_table"
        ])
    query_map = {
    "flow_rate_div": ("flow_rate_graph", get_flow_rate_graph),
    "wind_speed_div": ("wind_speed_graph", get_wind_speed_graph),
    "temp_div": ("temp_graph", get_temp_graph),
    "wind_direction_table": ("wind_direction_table", get_wind_direction_table),
    }
    payload = execute_threaded_queries(query_map, max_workers=4, cache_timeout=60 * 5)
    payload["date"] = current_date
    return render(request, "home.html", payload)

def about(request):
    return render(request, 'about.html')

def wind(request):
    query_map = {
        "wind_speed_div": ("wind_speed_graph", get_wind_speed_graph),
        "wind_direction_table": ("wind_direction_table", get_wind_direction_table),
    }
    payload = execute_threaded_queries(query_map, max_workers=4, cache_timeout=60 * 5)
    return render(request, 'wind.html', payload)

def flow_rate(request):
    query_map = {
        "flow_rate_div": ("flow_rate_graph", get_flow_rate_graph),
    }
    payload = execute_threaded_queries(query_map, max_workers=4, cache_timeout=60 * 5)
    return render(request, 'flow_rate.html', payload)