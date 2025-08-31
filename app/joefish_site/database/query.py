from joefish_site.database.database import FishDatabase
import plotly.graph_objects as go
from plotly.io import to_html
from joefish_site.database.database import FishDatabase
import plotly.graph_objects as go
from plotly.io import to_html

# Create a single DB instance to reuse
db = FishDatabase()

def query_data(query: str, db_instance: FishDatabase = db):
    """Generic query function"""
    return db_instance.query_to_df(query)

def create_graph(x, y, title, x_label, y_label, name):
    """Generic Plotly line+marker graph to HTML"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines+markers', name=name))
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        template='plotly_white'
    )
    return to_html(fig, full_html=False)

# Flow Rate
def get_flow_rate_data():
    query = """
    SELECT reading_time_central, flow_rate
    FROM river.bra_flow_rate
    WHERE reading_time_central >= current_date - INTERVAL '7 days'
    ORDER BY reading_time_central DESC
    """
    return query_data(query)

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

# Wind Speed
def get_wind_speed_data():
    query = """
    SELECT date(start_time_central) AS start_time_central,
           AVG(wind_speed_mph) AS wind_speed_mph
    FROM weather.nws_wind
    WHERE start_time_central >= current_date
    GROUP BY date(start_time_central)
    ORDER BY date(start_time_central) ASC
    """
    return query_data(query)

def get_wind_speed_graph():
    df = get_wind_speed_data()
    return create_graph(
        df['start_time_central'].to_list(),
        df['wind_speed_mph'].to_list(),
        'Average Wind Speed Over Next 7 Days',
        'Reading Time (Central)',
        'Wind Speed (mph)',
        'Wind Speed (mph)'
    )

# Temperature
def get_temp_data():
    query = """
    SELECT date(start_time_central) AS start_time_central,
           AVG(temperature_f) AS temperature_f
    FROM weather.nws_wind
    WHERE start_time_central >= current_date
    GROUP BY date(start_time_central)
    ORDER BY date(start_time_central) ASC
    """
    return query_data(query)

def get_temp_graph():
    df = get_temp_data()
    return create_graph(
        df['start_time_central'].to_list(),
        df['temperature_f'].to_list(),
        'Average Air Temperature Over Next 7 Days',
        'Reading Time (Central)',
        'Air Temperature (°F)',
        'Air Temperature (°F)'
    )

# Wind Direction
def get_wind_direction_data():
    query = """
    WITH WindCounts AS (
        SELECT DATE(start_time_central) AS day,
               wind_direction,
               COUNT(*) AS direction_count
        FROM weather.nws_wind
        WHERE start_time_central >= current_date
        GROUP BY DATE(start_time_central), wind_direction
    ),
    RankedWinds AS (
        SELECT day, wind_direction, direction_count,
               RANK() OVER (PARTITION BY day ORDER BY direction_count DESC) AS rank
        FROM WindCounts
    )
    SELECT day, wind_direction, direction_count
    FROM RankedWinds
    WHERE rank = 1
    ORDER BY day;
    """
    return query_data(query)

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
                <div class="z-20 flex items-center justify-center bg-blue-600 w-10 h-10 rounded-full shadow-md">
                    <h1 class="font-bold text-white text-lg">{index + 1}</h1>
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
