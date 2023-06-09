import pandas as pd
from django.conf import settings
import plotly.graph_objs as go
import plotly.io as pio
import core.plotting.plotting_utils as plt_util
import plotly.express as px


def concurrency_plot_factory(date_frame, Groups, aggregate, freq):
    """
    Create a concurrency plot from a dateframe
    input: pandas df created with the create_concurrency_dataframe function,
           list-like of Group obj,
           pandas aggregate fnc,
           pandas freq str
    output: plotly div containing a line-style concurreny plot
    """
    # Create a graph object

    pio.templates.default = settings.DEFAULT_PLOT_STYLE
    fig = go.Figure()

    # Groupe the Data, if it is an interval, simply use the dateframe

    date_frame = date_frame.groupby(by=pd.Grouper(freq=freq)).agg(aggregate)

    # Add the lines to the Plot object
    for group in Groups:
        fig.add_trace(
            go.Scatter(
                x=date_frame.index,
                y=date_frame[group.name],
                mode="lines",
                name=group.name,
            )
        )

    # TODO Add the Legend in a Place of Convenience

    # Add a timerange selector
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all"),
                    ]
                )
            ),
            rangeslider=dict(visible=True),
            type="date",
        )
    )

    # Return a Div Block

    return plt_util.create_div_block(fig)


def amplitude_plot_factory(date_frame, Groups, Unified=True):
    """
    Produces an div Block containing an Plotly Graphobject in the Style of a Amplitude Plot.
    Used in the Concurrency GroupAnalysis view as a way to represent concurrency.
    Use Unified to indicate if the bars should be scaled per group or uniform.

    input: pandas df created with the create_concurrency_dataframe function,
           list-like of Group obj,
           bool Unified
    output: plotly plot div cotaining an ampliude plot
    """

    pio.templates.default = settings.DEFAULT_PLOT_STYLE
    fig = go.Figure()

    # Compute the Scaling factor depedent on all groups
    if Unified:

        # Assume that at least one event did happen, else the plot remains empty, and compute highest group value
        scaling = date_frame.max().max()

    # Add the lines to the Plot object
    for group in Groups:

        series = date_frame[date_frame[group.name] > 0][group.name]

        # Compute the Scaling factor per individual group
        if not Unified:
            scaling = series.max()

        # TODO Implement Individual and Unified Scaling
        fig.add_trace(
            go.Scatter(
                x=series.index,
                y=series.apply(lambda x: group.name),
                mode="markers",
                name=group.name,
                marker_symbol="line-ns-open",
                marker=dict(size=65 * series / scaling),
                hovertemplate="Group: %{y} <br>Date: %{x}<br>%{text}<extra></extra>",
                text=["Concurrent Events: {}".format(i) for i in list(series)],
            )
        )

    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="YTD", step="year", stepmode="todate"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all"),
                    ]
                )
            ),
            rangeslider=dict(visible=True),
            type="date",
        )
    )

    return plt_util.create_div_block(fig)


def timeframe_plot_factory(df):

    fig = px.timeline(
        df,
        x_start="start_timestamp",
        x_end="time:timestamp",
        y="case:concept:name",
        color="case:concept:name",
        hover_name="case:concept:name",
    )

    return plt_util.create_div_block(fig)
