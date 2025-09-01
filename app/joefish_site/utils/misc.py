from concurrent.futures import ThreadPoolExecutor
from django.core.cache import cache

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