import plotly.graph_objects as go
from plotly.io import to_html
import polars as pl


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
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines+markers", name=name))
    fig.update_layout(
        title=title, xaxis_title=x_label, yaxis_title=y_label, template="plotly_white"
    )
    return to_html(fig, full_html=False)
