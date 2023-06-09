import pandas as pd
import os
import json
from django.conf import settings
import plotly.graph_objs as go
import plotly.express as px
import plotly.io as pio
from pm4py.util import xes_constants as xes
import core.plotting.plotting_utils as plt_util
from perspective_views.plotting.data_frame_creation import create_df_case


def timeframe_plot(df, waterfall_mode=False):
    """
    Creates a Plot representing a singluar trace based on its activitites over time
    Input: A case df
    """
    df.sort_values(xes.DEFAULT_START_TIMESTAMP_KEY, inplace=True)

    # Makes the Concept:Name Labeling unique, so that they are not plotted in the same row
    if waterfall_mode:
        occurences = df.value_counts(xes.DEFAULT_NAME_KEY)
        occurences = occurences[occurences > 1]

        for col, num in occurences.iteritems():
            df.loc[df[xes.DEFAULT_NAME_KEY] == col, [xes.DEFAULT_NAME_KEY]] = [
                col + "_" + str(x) for x in range(num)
            ]

    df.loc[:, xes.DEFAULT_NAME_KEY] = df.loc[:, xes.DEFAULT_NAME_KEY].apply(
        lambda x: x.capitalize()
    )

    fig = px.timeline(
        df,
        x_start=xes.DEFAULT_START_TIMESTAMP_KEY,
        x_end=xes.DEFAULT_TIMESTAMP_KEY,
        y=xes.DEFAULT_NAME_KEY,
        color=xes.DEFAULT_NAME_KEY,
        hover_name=xes.DEFAULT_NAME_KEY,
    )

    return plt_util.create_div_block(fig)


def multi_variants_plot_factory(df, variant_idxs):
    """
    Creates a Plot representing multiple variants in time, by their minimum start and end times
    Input: An variant df, the list-like integer indicies of the variants
    """

    # Add HTML breaks into the trace event, to make it plottable, without breaking the Hover

    df = df.iloc[variant_idxs]

    hover_data_dict = {
        "Start": True,
        "End": True,
    }

    # Add HTML breaks into the trace event, to make it plottable

    styled_trace_events = [plt_util.trace_plotting_styler(x) for x in df["variant"]]
    hover_data_dict["Events"] = styled_trace_events

    fig = px.timeline(
        df,
        x_start="Start",
        x_end="End",
        y="Name",
        color="Name",
        hover_name="Name",
        hover_data=hover_data_dict,
    )

    # TODO Add a better hovertemplate
    # fig.update_traces(hovertemplate=None)

    return plt_util.create_div_block(fig)


def single_variant_plot_factory(
    log, file_format, log_information, variant_index, df_variant
):
    """
    Creates a Plot representing the different cases associated with a variant in time
    Calls the case df function to accumulate the different individual cases, making up each variant.
    """

    df = create_df_case(
        log,
        file_format,
        df_variant.iloc[variant_index]["Cases"].values[0],
        log_information,
    )
    df = (
        df.groupby("case:concept:name")
        .agg({xes.DEFAULT_START_TIMESTAMP_KEY: min, xes.DEFAULT_TIMESTAMP_KEY: max})
        .reset_index()
    )

    df = df.rename(
        {
            "case:concept:name": "Name",
            xes.DEFAULT_START_TIMESTAMP_KEY: "Start",
            xes.DEFAULT_TIMESTAMP_KEY: "End",
        },
        axis=1,
    )

    fig = px.timeline(
        df, x_start="Start", x_end="End", y="Name", color="Name", hover_name="Name"
    )

    # TODO Add a better hovertemplate
    # fig.update_traces(hovertemplate=None)

    return plt_util.create_div_block(fig)


def dfg_to_g6(dfg):
    unique_nodes = []

    for i in dfg:
        unique_nodes.extend(i)
    unique_nodes = list(set(unique_nodes))

    unique_nodes_dict = {}

    for index, node in enumerate(unique_nodes):
        unique_nodes_dict[node] = "node_" + str(index)

    nodes = [
        {
            "id": unique_nodes_dict[i],
            "name": i,
            "isUnique": False,
            "conf": [{"label": "Name", "value": i}],
        }
        for i in unique_nodes_dict
    ]
    freqList = [int(dfg[i]) for i in dfg]
    maxVal = max(freqList) if len(freqList) != 0 else 0
    minVal = min(freqList) if len(freqList) != 0 else 0

    edges = [
        {
            "source": unique_nodes_dict[i[0]],
            "target": unique_nodes_dict[i[1]],
            "label": round(dfg[i], 2),
            "style": {"endArrow": True},
        }
        for i in dfg
    ]
    data = {
        "nodes": nodes,
        "edges": edges,
    }
    temp_path = os.path.join(settings.MEDIA_ROOT, "temp")
    temp_file = os.path.join(temp_path, "data.json")
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data, temp_file
