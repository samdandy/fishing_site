from joefish_site.database.database import FishDatabase
import plotly.graph_objects as go
from plotly.io import to_html
def get_flow_rate_data(db: FishDatabase = None):
    if db is None:
        db = FishDatabase()
    query = """
    SELECT reading_time_central, flow_rate
    FROM river.bra_flow_rate
    WHERE reading_time_central >= current_date - INTERVAL '7 days'
    ORDER BY reading_time_central DESC
    """
    df = db.query_to_df(query)
    return df

def get_flow_rate_graph(db: FishDatabase = None):
    if db is None:
        db = FishDatabase()
    
    df = get_flow_rate_data(db)
    dates = df['reading_time_central'].to_list()
    flow_rates = df['flow_rate'].to_list()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=dates, y=flow_rates, mode='lines+markers', name='Flow Rate (cfs)')
    )
    fig.update_layout(
        title='River Flow Rate Over Past 7 Days',
        xaxis_title='Reading Time (Central)',
        yaxis_title='Flow Rate (cfs)',
        template='plotly_white'
    )
    return to_html(fig, full_html=False)


def get_wind_speed_data(db: FishDatabase = None):
    if db is None:
        db = FishDatabase()
    query = """
    select date(start_time_central) as start_time_central,avg(wind_speed_mph) as wind_speed_mph from weather.nws_wind
    where start_time_central >= current_date
    group by date(start_time_central)
    order by date(start_time_central) asc
    """
    df = db.query_to_df(query)
    return df

def get_wind_speed_graph(db: FishDatabase = None):
    if db is None:
        db = FishDatabase()
    
    df = get_wind_speed_data(db)
    dates = df['start_time_central'].to_list()
    wind_speeds = df['wind_speed_mph'].to_list()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=dates, y=wind_speeds, mode='lines+markers', name='Wind Speed (mph)')
    )
    fig.update_layout(
        title='Average Wind Speed Over Next 7 Days',
        xaxis_title='Reading Time (Central)',
        yaxis_title='Wind Speed (mph)',
        template='plotly_white'
    )
    return to_html(fig, full_html=False)


def get_temp_data(db: FishDatabase = None):
    if db is None:
        db = FishDatabase()
    query = """
    SELECT date(start_time_central) as start_time_central, avg(temperature_f) as temperature_f
    FROM weather.nws_wind
    WHERE start_time_central >= current_date
    GROUP BY date(start_time_central)
    ORDER BY date(start_time_central) ASC
    """
    df = db.query_to_df(query)
    return df

def get_temp_graph(db: FishDatabase = None):
    if db is None:
        db = FishDatabase()

    df = get_temp_data(db)
    dates = df['start_time_central'].to_list()
    temps = df['temperature_f'].to_list()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=dates, y=temps, mode='lines+markers', name='Air Temperature (°F)')
    )
    fig.update_layout(
        title='Average Air Temperature Over Next 7 Days',
        xaxis_title='Reading Time (Central)',
        yaxis_title='Air Temperature (°F)',
        template='plotly_white'
    )
    return to_html(fig, full_html=False)

def get_wind_direction_data(db: FishDatabase = None):
    if db is None:
        db = FishDatabase()
    query = """
    WITH WindCounts AS (
        SELECT 
            DATE(start_time_central) AS day,
            wind_direction,
            COUNT(*) AS direction_count
        FROM weather.nws_wind
        WHERE start_time_central >= current_date
        GROUP BY DATE(start_time_central), wind_direction
    ),
    RankedWinds AS (
        SELECT 
            day,
            wind_direction,
            direction_count,
            RANK() OVER (PARTITION BY day ORDER BY direction_count DESC) AS rank
        FROM WindCounts
    )
    SELECT 
        day,
        wind_direction,
        direction_count
    FROM RankedWinds
    WHERE rank = 1
    ORDER BY day;
    """
    df = db.query_to_df(query)
    return df

def get_wind_direction_table(db: FishDatabase = None):
    if db is None:
        db = FishDatabase()
    df = get_wind_direction_data(db)
    

    html = """<div class="container mx-auto p-4">
        <h1 class="text-2xl font-bold text-center mb-8">Wind Direction Next 7 Days</h1>
        <div class="relative wrap overflow-hidden p-10 h-full">
            <div class="border-2-2 absolute border-blue-500 h-full border" style="left: 50%;"></div>
            """
    for index, row in enumerate(df.rows()):
        flex_direction = "flex-row-reverse" if index % 2 == 0 else "flex-row"
        html += f"""
      <div class="mb-8 flex w-full">
    <!-- Conditional flex direction for staggering -->
    <div class="flex items-center w-full {flex_direction}">
        <!-- Left empty space for stagger -->
        <div class="w-1/2"></div>

        <!-- Index circle -->
        <div class="z-20 flex items-center justify-center bg-blue-600 w-10 h-10 rounded-full shadow-md">
            <h1 class="font-bold text-white text-lg">{index + 1}</h1>
        </div>

        <!-- Content box -->
        <div class="bg-white rounded-lg shadow-md w-1/2 px-6 py-4 ml-4">
            <!-- Wind Direction -->
            <div class="mb-2">
                <h2 class="font-bold text-3xl text-gray-800">{row[1]}</h2>
                <p class="text-sm text-gray-500">Wind Direction</p>
            </div>

            <!-- Date -->
            <div>
                <h2 class="font-bold text-2xl text-gray-800">{row[0]}</h2>
                <p class="text-sm text-gray-500">Date</p>
            </div>
        </div>
    </div>
</div>




        """
    
    # Close HTML tags
    html += """
            </div>
        </div>
    </body>
    </html>
    """

    return html



