from django.shortcuts import render
from datetime import datetime
from joefish_site.database.query import get_flow_rate_graph,get_wind_speed_graph,get_temp_graph,get_wind_direction_table,get_all_data


def home(request):
    current_date = datetime.now().date()
    payload = get_all_data()
    payload["date"] = current_date
    return render(request, "home.html", payload)

def about(request):
    return render(request, 'about.html')

def wind(request):
    payload = {
        "wind_speed_div": get_wind_speed_graph(),
        "wind_direction_table": get_wind_direction_table(),
    }
    return render(request, 'wind.html', payload)

def flow_rate(request):
    payload = {
        "flow_rate_div": get_flow_rate_graph(),
    }
    return render(request, 'flow_rate.html', payload)

def temperature(request):
    payload = {
        "temp_div": get_temp_graph(),
    }
    return render(request, 'temperature.html', payload)