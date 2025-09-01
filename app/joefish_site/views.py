from django.shortcuts import render
import plotly.graph_objects as go
from plotly.io import to_html
import numpy as np
import polars as pl
from datetime import datetime, timedelta
from joefish_site.database.database import FishDatabase
from joefish_site.database.query import get_flow_rate_graph, get_wind_speed_graph, get_temp_graph,get_wind_direction_table
from django.views.decorators.cache import cache_page
# from database.query import get_flow_rate_data


@cache_page(60 * 15)
def about(request):
    return render(request, 'about.html')

@cache_page(60 * 15)
def home(request):
    from django.core.cache import cache

    # Set cache
    cache.set("my_key", "Hello, world!", timeout=120)  # expires in 60s

    # Get cache
    value = cache.get("my_key")
    print(value)  # "Hello, world!"

    # Delete cache
    cache.delete("my_key")
    current_date = datetime.now().date()
    flow_rate_div = get_flow_rate_graph()
    wind_speed_div = get_wind_speed_graph()  
    temp_div = get_temp_graph()
    wind_direction_table = get_wind_direction_table()
    payload = {
        'flow_rate_div': flow_rate_div,
        'wind_speed_div': wind_speed_div,
        'temp_div': temp_div,
        'wind_direction_table': wind_direction_table,
        'date': current_date
    }
    # Render the template with the plot
    return render(request, 'home.html', payload)


@cache_page(60 * 15)
def wind(request):
    wind_speed_div = get_wind_speed_graph()
    wind_direction_table = get_wind_direction_table()
    return render(request, 'wind.html',{'wind_direction_table':wind_direction_table,'wind_speed_div':wind_speed_div})

@cache_page(60 * 15)
def flow_rate(request):
    flow_rate_div = get_flow_rate_graph()
    return render(request, 'flow_rate.html',{'flow_rate_div':flow_rate_div})
