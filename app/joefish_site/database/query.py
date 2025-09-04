from datetime import timedelta, date
from django.utils.timezone import now
from joefish_site.models import FlowRate, WindSpeed, Temperature, WindDirection
from joefish_site.utils.misc import query_data,queryset_to_polars,create_graph
from django.db.models import Avg
from django.utils.timezone import now
from django.db.models.functions import TruncDate
from django.db.models import Count, F, Window
from django.db.models.functions.window import Rank


today = now().date()

def get_flow_rate_data():
    seven_days_ago = now() - timedelta(days=7)
    data = query_data(
        model=FlowRate,
        filters={"reading_time_central__gte": seven_days_ago},
        order_by=["-reading_time_central"],
        values=["reading_time_central", "flow_rate"],
    )
    return queryset_to_polars(data, values=["reading_time_central", "flow_rate"])

def get_flow_rate_graph():
    df = get_flow_rate_data()
    return create_graph(
        df['reading_time_central'].to_list(),
        df['flow_rate'].to_list(),
        'River Flow Rate Over Past 7 Days', 
        'Reading Time (Central)',
        'Flow Rate (cfs)',
        'Flow Rate (cfs)'
    )


def get_wind_speed_data(today=None):
    filtered_today_onwards = (
        WindSpeed.objects
        .filter(start_time_central__date__gte=today) if today else WindSpeed.objects.all()
    )
    data = (
        filtered_today_onwards.annotate(date=TruncDate("start_time_central"))
          .values("date")
          .annotate(avg_wind_speed=Avg("wind_speed_mph"))
          .order_by("date")
    )
    return queryset_to_polars(data, values=["date", "avg_wind_speed"])

def get_wind_speed_graph():
    df = get_wind_speed_data()
    return create_graph(
        df['date'].to_list(),
        df['avg_wind_speed'].to_list(),
        'Average Wind Speed Over Next 7 Days',
        'Reading Time (Central)',
        'Wind Speed (mph)',
        'Wind Speed (mph)'
    )

# Temperature
def get_temp_data():
    today = now().date()  # timezone-safe date
    data = (
        Temperature.objects
        .filter(start_time_central__date__gte=today)
        .annotate(date=TruncDate("start_time_central"))
        .values("date")
        .annotate(avg_temperature=Avg("temperature_f"))
        .order_by("date")
    )
    return queryset_to_polars(qs=data,values=["date","avg_temperature"])

def get_temp_graph():
    df = get_temp_data()
    return create_graph(
        df['date'].to_list(),
        df['avg_temperature'].to_list(),
        'Average Air Temperature Over Next 7 Days',
        'Reading Time (Central)',
        'Air Temperature (°F)',
        'Air Temperature (°F)'
    )

# Wind Direction
def get_wind_direction_data(today=None):
    qs = WindDirection.objects.all()
    if today:
        qs = qs.filter(start_time_central__date__gte=today)

    qs = (
        qs.annotate(date=TruncDate("start_time_central"))
          .values("date", "wind_direction")
          .annotate(direction_count=Count("wind_direction"))  # count per direction per day
          .annotate(
              rank=Window(
                  expression=Rank(),
                  partition_by=[F("date")],
                  order_by=F("direction_count").desc()
              )
          )
          .filter(rank=1)  # keep only most common direction(s) per day
          .order_by("date")
    )
    return queryset_to_polars(qs=qs,values=["date","wind_direction"])

def get_wind_direction_table():
    df = get_wind_direction_data()
    html = """<div class="container mx-auto p-4">
        <h1 class="text-2xl font-bold text-center mb-8">Wind Direction Next 7 Days</h1>
        <div class="relative wrap overflow-hidden p-10 h-full">
            <div class="border-2-2 absolute border-blue-500 h-full border" style="left: 50%;"></div>
            """
    for index, row in enumerate(df.rows()):
        flex_direction = "flex-row-reverse" if index % 2 == 0 else "flex-row"
        html += f"""
        <div class="mb-8 flex w-full">
            <div class="flex items-center w-full {flex_direction}">
                <div class="w-1/2"></div>
                <div class="z-20 flex items-center justify-center">
                <div class="w-6 h-1 bg-blue-600 rounded"></div>
                </div>

                <div class="bg-white rounded-lg shadow-md w-1/2 px-6 py-4 ml-4">
                    <div class="mb-2">
                        <h2 class="font-bold text-3xl text-gray-800">{row[1]}</h2>
                        <p class="text-sm text-gray-500">Wind Direction</p>
                    </div>
                    <div>
                        <h2 class="font-bold text-2xl text-gray-800">{row[0]}</h2>
                        <p class="text-sm text-gray-500">Date</p>
                    </div>
                </div>
            </div>
        </div>"""
    html += "</div></div></body></html>"
    return html


def get_all_data():
    return {
        "flow_rate_div": get_flow_rate_graph(),
        "wind_speed_div": get_wind_speed_graph(),
        "temperature_div": get_temp_graph(),
        "wind_direction_table": get_wind_direction_table()
    }