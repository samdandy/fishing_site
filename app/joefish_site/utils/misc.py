from concurrent.futures import ThreadPoolExecutor
from django.core.cache import cache
from joefish_site.database.database import FishDatabase
import plotly.graph_objects as go
from plotly.io import to_html
import polars as pl

def cached_or_fetch(key, func):
    """Helper to wrap cache.get_or_set with error handling."""
    try:
        return cache.get_or_set(key, func, timeout= 60 * 5)
    except Exception as e:
        return func() 
    
def execute_threaded_queries(query_map, max_workers=10, cache_timeout=60 * 5):
    """
    Execute multiple queries in parallel using ThreadPoolExecutor and cache results.
    
    Args:
        query_map (dict): Dictionary mapping payload keys to tuples of (cache_key, query_function).
                          Example: {"flow_rate_div": ("flow_rate_graph", get_flow_rate_graph)}
        max_workers (int): Maximum number of threads for ThreadPoolExecutor (default: 4).
        cache_timeout (int): Cache timeout in seconds (default: None, uses env or 300).
    
    Returns:
        dict: Dictionary with payload keys mapped to query results or error placeholders.
    """
    payload = {}
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                payload_key: executor.submit(cached_or_fetch, cache_key, query_func)
                for payload_key, (cache_key, query_func) in query_map.items()
            }
            payload = {name: future.result() for name, future in futures.items()}
    except Exception as e:
        payload = {
            payload_key: "<div>Error loading data</div>"
            for payload_key in query_map
        }

    return payload


def queryset_to_polars(qs, values=None):
    """
    Convert a Django QuerySet into a Polars DataFrame.
    """
    if values:
        data = list(qs.values(*values))
    else:
        data = list(qs.values())
    return pl.DataFrame(data)

def query_data(model, filters=None, order_by=None, values=None, annotations=None):
    """
    Generic Django ORM → DataFrame function.
    
    Args:
        model: Django model class
        filters: dict of filters for .filter()
        order_by: list of fields to order by
        values: list of fields to include (default = all)
    """
    qs = model.objects.all()

    if filters:
        qs = qs.filter(**filters)
    if order_by:
        qs = qs.order_by(*order_by)
    if annotations:
        qs = qs.annotate(**annotations)
    if values:
        qs = qs.values(*values)
    else:
        qs = qs.values()

    return qs

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