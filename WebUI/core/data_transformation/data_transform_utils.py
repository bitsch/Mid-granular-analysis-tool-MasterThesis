from pm4py.util import xes_constants as xes
import pandas as pd


def transform_lifecycle_csv_to_interval_csv(df):
    """ """

    # Check if the Dataframe is well-formed

    # Check if the Lifecycle Events are Start/Complete

    # TODO Throw some User Visible Error, to communicate

    # Group the df and create timestamp lists
    df = (
        df.sort_values(xes.DEFAULT_TIMESTAMP_KEY)
        .groupby(
            by=[xes.DEFAULT_NAME_KEY, "case:concept:name", xes.DEFAULT_TRANSITION_KEY]
        )
        .agg({xes.DEFAULT_TIMESTAMP_KEY: list})
    )

    #  Unstack the Lists and reset the data frame index
    df = df.unstack().droplevel(0, axis=1).reset_index()

    # Drop incomplete cases
    df = df[~df["complete"].isna()]

    # Fill in empty start tims and explode the columns seperatly to derive the wished for format
    df = df.ffill(axis=1).apply(pd.Series.explode)

    df = df.rename(
        {
            "start": xes.DEFAULT_START_TIMESTAMP_KEY,
            "complete": xes.DEFAULT_TIMESTAMP_KEY,
        },
        axis=1,
    )

    return df
