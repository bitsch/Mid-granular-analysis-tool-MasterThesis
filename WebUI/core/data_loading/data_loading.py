# PM4PY Dependencies
import pandas as pd
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.util import xes_constants as xes
from pm4py import format_dataframe


def log_import(file_path, file_format, log_information):
    """
    Imports the file using PM4PY functionalitites, formats
    it in a processable fashion, accoding to the Log information,
    if it is an CSV

    input: file_path str, file_format str, interval bool

    output: PM4PY default object dependent on Filetype, fromatted in case of csv
            The Set of all trace activities
    """

    activities = set()

    if file_format == "csv":

        # TODO Apply further file integrity check

        log = pd.read_csv(file_path)

        # Transform the Timestamp to Datetime
        if log_information["log_type"] == "noninterval":

            log[log_information["timestamp"]] = pd.to_datetime(
                log[log_information["timestamp"]], utc=True
            )

            log = format_dataframe(
                log,
                case_id=log_information["case_id"],
                activity_key=log_information["concept_name"],
                timestamp_key=log_information["timestamp"],
            )

        # Transform the Timestamp to Datetime, and rename the transition:lifecycle
        elif log_information["log_type"] == "lifecycle":

            # Convert the Timestamps to Datetime
            log[log_information["timestamp"]] = pd.to_datetime(
                log[log_information["timestamp"]], utc=True
            )

            log = format_dataframe(
                log,
                case_id=log_information["case_id"],
                activity_key=log_information["concept_name"],
                timestamp_key=log_information["timestamp"],
            )
            # Rename the Columns to the XES defaults
            log = log.rename(
                {log_information["lifecycle"]: xes.DEFAULT_TRANSITION_KEY}, axis=1
            )

        elif log_information["log_type"] == "timestamp":

            # Convert the Timestamps to Datetime
            log[log_information["end_timestamp"]] = pd.to_datetime(
                log[log_information["end_timestamp"]], utc=True
            )
            log[log_information["start_timestamp"]] = pd.to_datetime(
                log[log_information["start_timestamp"]], utc=True
            )

            log = format_dataframe(
                log,
                case_id=log_information["case_id"],
                activity_key=log_information["concept_name"],
                timestamp_key=log_information["end_timestamp"],
            )

            # Rename the Columns to the XES defaults
            log = log.rename(
                {log_information["start_timestamp"]: xes.DEFAULT_START_TIMESTAMP_KEY},
                axis=1,
            )

        activities = set(log[xes.DEFAULT_NAME_KEY].unique())

    # Simply load the log using XES
    elif file_format == "xes":

        log = xes_importer.apply(file_path, parameters={"show_progress_bar": False})

        for trace in log:
            for event in trace:
                activities.add(event[log_information["concept_name"]])

    else:

        # TODO Throw some Warning / Show a warning Message in the Console
        print("Invalid Filepath")

    return log, activities


def get_log_format(file_path):

    """
    Function that extracts the file format in lowercase from a valid filepath
    input: file_path str
    output: file_format str
    """

    file_format = file_path.split(".")[-1].lower()

    return file_format
