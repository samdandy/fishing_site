from django.shortcuts import render
import plotly.graph_objects as go
from plotly.io import to_html
import numpy as np
import polars as pl
from datetime import datetime, timedelta
from joefish_site.database.database import FishDatabase
from joefish_site.database.query import get_flow_rate_graph, get_wind_speed_graph, get_temp_graph,get_wind_direction_table
# from database.query import get_flow_rate_data

def about(request):
    return render(request, 'about.html')

def home(request):
    db = FishDatabase()
    current_date = datetime.now().date()
    flow_rate_div = get_flow_rate_graph(db)
    wind_speed_div = get_wind_speed_graph(db)  
    temp_div = get_temp_graph(db)
    wind_direction_table = get_wind_direction_table(db)
    payload = {
        'flow_rate_div': flow_rate_div,
        'wind_speed_div': wind_speed_div,
        'temp_div': temp_div,
        'wind_direction_table': wind_direction_table,
        'date': current_date
    }
    # Render the template with the plot
    return render(request, 'home.html', payload)

def wind(request):
    return render(request, 'wind.html')

def flow_rate(request):
    return render(request, 'flow_rate.html')