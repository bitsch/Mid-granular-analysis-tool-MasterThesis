import pandas as pd
from pm4py import convert_to_dataframe
from pm4py.util import xes_constants as xes
from datetime import timedelta as td
import core.utils.utils as utils
import core.data_transformation.data_transform_utils as data_transform
import ruptures as rpt
import os
from django.conf import settings
import numpy as np
import matplotlib.pyplot as plt

from sklearn.decomposition import PCA
import pandas as pd
from datetime import timedelta as td
import ruptures as rpt
import datetime
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.log.importer.xes import importer as xes_importer
from datetime import date
from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.visualization.petri_net import visualizer as pn_visualizer
import seaborn as sns
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
import pm4py
import datetime
from functools import reduce
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report, confusion_matrix
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.linear_model import LinearRegression
from sklearn import tree,metrics
import warnings
warnings.filterwarnings('ignore')




event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
sensitivity=1.5
timeframe='D'
minstartdate=None
maxenddate=None
##usage= get_labels_set(input_transition_set)
def get_labels_set(input_transition_set):
    label_set=set()
    for transition in input_transition_set:
        label_set.add(transition._Transition__get_label())
    return label_set

##usage= get_input_transitions(,net 'n4')
def get_initial_start(net, intial_place):
    for place in net.places:
        if place._Place__get_name()==intial_place:
            initial_start=place
    return initial_start

##usage= get_input_transitions(net,initial_start)
def get_input_transitions(net,place):
    transition=list()
    if place in net.places:
        for arc in net.arcs:
            if arc._Arc__get_target()==place:
                if arc._Arc__get_source()._Transition__get_label() is None:
                    transition.append(arc._Arc__get_source())
                    for new_place in arc._Arc__get_source()._Transition__get_in_arcs():
                        transition.extend(get_input_transitions(net,new_place._Arc__get_source()))
                else:
                    transition.append(arc._Arc__get_source())
        return transition
    else:
        return None

##usage= get_output_transitions(net,initial_start)
def get_output_transitions(net,place):
    transition=list()
    if place in net.places:
        for arc in net.arcs:
            if arc._Arc__get_source()==place:
                transition.append(arc._Arc__get_target())
        return transition
    else:
        return None

def filter_none(input_transition_set):
    transition_set=set()
    for transition in input_transition_set:
        if transition._Transition__get_label() is not None:
            transition_set.add(transition)
    return transition_set

def globaldata(Zone):
    Zone['StartDateTime'] = pd.to_datetime(Zone['StartTime'], utc=True)
    Zone['StartDate'] = pd.to_datetime(Zone['StartDateTime']).dt.date
    Zone['EndDateTime'] = pd.to_datetime(Zone['EndTime'], utc=True)
    Zone['EndDate'] = pd.to_datetime(Zone['EndDateTime']).dt.date
    Zone['TotalWaitingTime']=  (pd.to_datetime(Zone['EndTime'], utc=True)-pd.to_datetime(Zone['StartTime'], utc=True))

    global minstartdate
    global maxenddate
    if minstartdate is None:
        minstartdate=min(Zone['StartDate'])
    else :
        minstartdate=min(minstartdate,min(Zone['StartDate']))
    if maxenddate is None:
        maxenddate=max(Zone['EndDate'])
    else :
        maxenddate=max(maxenddate,max(Zone['EndDate']))

def DataPreparation(Zone,timeFrame):
    global minstartdate
    global maxenddate
    print(minstartdate)
    print(maxenddate)
    return pd.DataFrame({'date':pd.date_range(start=minstartdate, end=maxenddate, freq=timeFrame),
                                       'tokenproduced':0,'tokenconsumed':0,'tokenleft':0,'oneframetoken':0,
                                       'TimeSpent':0,'Count':0})

def getZoneData(Zone,timeFrame):
    ZoneDataFrame=DataPreparation(Zone,timeFrame)
    if timeFrame=='H':
        timeformat='%Y-%m-%d %H'
    if timeFrame=='D':
        timeformat='%Y-%m-%d'
    if timeFrame=='W':
        timeformat='%Y-%m-%W'
    if timeFrame=='M':
        timeformat='%Y-%m'
    for index, row in ZoneDataFrame.iterrows():
        currentdate=row['date'].strftime(timeformat)
        print(currentdate)
        currentDateValue=row['date']
        produced=0
        left=0
        consumed=0
        oneFrame=0
        waiting=td(days=0)
        waitingdays=0
        #print(type(waiting))
        count=0
        itemlist=[]
        #if currentdate.strftime('%Y-%m-%d')<='1999-10-13':
        #    continue
        #print(currentdate)
        for indexdata, rowdata in Zone.iterrows():
            oneFramecheck=False
            StartDate=rowdata['StartTime'].strftime(timeformat)
            EndDate=rowdata['EndTime'].strftime(timeformat)
            #print(StartDate)
            #TotalWaitingTime=rowdata['TotalWaitingTime']
            TotalWaitingTime=rowdata['TotalWaitingTime']
            if timeFrame=='H':
                WaitingTimeTillDate=currentDateValue+td(hours=1)
            if timeFrame=='D':
                WaitingTimeTillDate=currentDateValue+td(hours=24)
            if timeFrame=='W':
                WaitingTimeTillDate=currentDateValue+td(weeks=1)
            if timeFrame=='M':
                WaitingTimeTillDate=currentDateValue+td(weeks=4)

            if currentdate==StartDate and currentdate==EndDate:
                oneFrame=oneFrame+1
                oneFramecheck=True
            if currentdate==StartDate:
                produced=produced+1
            if currentdate==EndDate:
                consumed=consumed+1
                WaitingTimeTillDate=rowdata['EndDateTime']
                itemlist.append(StartDate)
            if currentdate<EndDate and currentdate>=StartDate:
                #print(StartDate+" "+currentdate+" "+EndDate)
                left=left+1
            if currentdate<=EndDate and currentdate>=StartDate:
                TotalWaitingTime=WaitingTimeTillDate.replace(tzinfo=None)-rowdata['StartDateTime'].replace(tzinfo=None)
                if waiting is None:
                    waiting=TotalWaitingTime
                else:
                    if waiting.days<100000:
                        waiting=waiting+TotalWaitingTime
                        waitingdays=waiting.days
                    else :
                        waitingdays=TotalWaitingTime.days+waitingdays
                count=count+1
        ZoneDataFrame.at[index, 'tokenproduced']=produced
        ZoneDataFrame.at[index, 'tokenconsumed']=consumed
        ZoneDataFrame.at[index, 'oneframetoken']=oneFrame
        ZoneDataFrame.at[index, 'tokenleft']=left
        if waiting.days<100000:
            ZoneDataFrame.at[index, 'TimeSpent']=waiting
        else:
            ZoneDataFrame.at[index, 'TimeSpent']=waitingdays
        ZoneDataFrame.at[index, 'Count']=count
    return ZoneDataFrame.copy()



def createZone(log,net,replayed_traces,placeSet):
    input_transition_set=set()
    input_transition_label_set=set()
    output_transition_set=set()
    output_transition_label_set=set()
    all_transition_set=set()
    all_transition_label_set=set()
    for start in placeSet.members:
        print(start)
        initial_start=get_initial_start(net, start)
        input_transition_set|=set(get_input_transitions(net,initial_start))
        output_transition_set|=set(get_output_transitions(net,initial_start))

    all_transition_set|=input_transition_set
    all_transition_set|=output_transition_set
    temp=input_transition_set.difference(output_transition_set)
    output_transition_set.difference_update(input_transition_set)
    input_transition_set=temp

    input_transition_set=filter_none(input_transition_set)
    all_transition_set.difference_update(input_transition_set)
    all_transition_set=filter_none(all_transition_set)

    input_transition_label_set|=get_labels_set(input_transition_set)
    output_transition_label_set|=get_labels_set(output_transition_set)
    all_transition_label_set|=get_labels_set(all_transition_set)

    print(all_transition_set)
    print(all_transition_label_set)
    print(input_transition_set)
    print(input_transition_label_set)
    print(output_transition_set)
    print(output_transition_label_set)

    token_produced=0
    token_consumed=0
    token_left=0
    dataframe=pd.DataFrame(columns= ['StartEvent','StartTime','EndEvent','EndTime','User'])
    for trace,case in zip(replayed_traces, log):
        last_event=None
        first_event=None
        goodstart=False
        if trace['trace_is_fit']==True or True:
            backupstart=None
            backup_event=None
            for active_trace in trace['activated_transitions']:
                if active_trace in input_transition_set :
                    goodstart=True
                    for events in case:
                        if events['concept:name'] in input_transition_label_set:
                            last_event=events
                            backup_event=events
                if active_trace in output_transition_set:
                    for events in case:
                        if events['concept:name'] in output_transition_label_set:
                            first_event=events
                if active_trace in all_transition_set :
                    for events in case:
                        if events['concept:name'] in all_transition_label_set:
                            backup_event=events
                            if goodstart==False and backupstart is None:
                                backupstart=events

            if first_event is None and backup_event is not None:
                first_event=backup_event
            if last_event is None and backupstart is not None:
                last_event=backupstart
            if last_event is not None and first_event  is not None :
                token_produced=token_produced+1
                token_consumed=token_consumed+1
                row_df = pd.DataFrame([[last_event['concept:name'], last_event['time:timestamp'],first_event['concept:name'], first_event['time:timestamp'], case.attributes['concept:name']]],columns= ['StartEvent','StartTime','EndEvent','EndTime','User'])
                dataframe = pd.concat([row_df, dataframe], ignore_index=True)

    print(token_produced)
    print(token_consumed)

    global timeframe
    if timeframe is None:
        timeFrame='D'
    else :
        timeFrame=timeframe
    for zone in [dataframe]:
        globaldata(zone)
    global minstartdate
    global maxenddate
    print(minstartdate)
    print(maxenddate)
    if timeFrame=='H':
        maxenddate=maxenddate+td(hours=1)
    if timeFrame=='D':
        maxenddate=maxenddate+td(days=1)
    if timeFrame=='W':
        maxenddate=maxenddate+td(days=7)
    if timeFrame=='M':
        maxenddate=maxenddate+td(days=31)
    dataframedf=getZoneData(dataframe,timeFrame)
    return dataframedf

def create_concurrency_frame(df, Groups, freq="5T"):
    """
    Compute a dataframe for plotting of concurrent
    events used in the associated plotting functions

    input:  pandas DF log in a double timestamp format
            list-like of Group Objects
            pandsa freq str

    output: pandas DF containing the count of
            concurrent activities per group on
            a freq-level
    """

    df = df.copy()
    df = df.loc[
        df[xes.DEFAULT_TRACEID_KEY].isin(
            utils.flatten([group.members for group in Groups])
        ),
        :,
    ]

    for group in Groups:
        df.loc[:, group.name] = df[xes.DEFAULT_TRACEID_KEY].isin(group.members)

    df = df.drop(["case:concept:name", xes.DEFAULT_TRACEID_KEY], axis=1)

    df.loc[:, xes.DEFAULT_START_TIMESTAMP_KEY] = pd.to_datetime(
        df.loc[:, xes.DEFAULT_START_TIMESTAMP_KEY], utc=True
    )
    df.loc[:, xes.DEFAULT_TIMESTAMP_KEY] = pd.to_datetime(
        df.loc[:, xes.DEFAULT_TIMESTAMP_KEY], utc=True
    )

    df.loc[:, "interpolate_date"] = [
        pd.date_range(s, e, freq=freq)
        for s, e in zip(
            pd.to_datetime(df.loc[:, xes.DEFAULT_START_TIMESTAMP_KEY]),
            pd.to_datetime(df.loc[:, xes.DEFAULT_TIMESTAMP_KEY]),
        )
    ]

    df = df.drop(
        [xes.DEFAULT_START_TIMESTAMP_KEY, xes.DEFAULT_TIMESTAMP_KEY], axis=1
    ).explode("interpolate_date")

    agg_func = {group.name: sum for group in Groups}

    date_frame = df.groupby(pd.Grouper(key="interpolate_date", freq=freq)).agg(agg_func)

    return date_frame


def create_plotting_data(log, file_format, log_information):
    """
    Transforms a log, such that it can be easer
    used for plotting, removes unnecessary data,
    creates df from xes data, and renames columns

    input: XES/CSV log ,
           file_format str,
           log_information django session dict

    output: pandas df with pm4py default names for attributes in a two timestamp format
    """
    if file_format == "csv":

        # Select only the Relevant columns of the Dataframe
        if log_information["log_type"] == "noninterval":

            # Project the Log onto the Group activities

            log = log[
                [
                    "case:concept:name",
                    xes.DEFAULT_TIMESTAMP_KEY,
                    xes.DEFAULT_TRACEID_KEY,
                ]
            ]

        elif log_information["log_type"] == "lifecycle":

            log = log[
                [
                    "case:concept:name",
                    xes.DEFAULT_TIMESTAMP_KEY,
                    xes.DEFAULT_TRACEID_KEY,
                    xes.DEFAULT_TRANSITION_KEY,
                ]
            ]
            log = data_transform.transform_lifecycle_csv_to_interval_csv(log)

        elif log_information["log_type"] == "timestamp":

            log = log[
                [
                    "case:concept:name",
                    xes.DEFAULT_TIMESTAMP_KEY,
                    xes.DEFAULT_TRACEID_KEY,
                    xes.DEFAULT_START_TIMESTAMP_KEY,
                ]
            ]
            log = log.rename(
                {
                    log_information["start_timestamp"]: xes.DEFAULT_START_TIMESTAMP_KEY,
                    log_information["end_timestamp"]: xes.DEFAULT_TIMESTAMP_KEY,
                },
                axis=1,
            )

    # Simply load the log using XES
    elif file_format == "xes":

        log = convert_to_dataframe(log)

        if log_information["log_type"] == "noninterval":

            log[log_information["timestamp"]] = pd.to_datetime(
                log[log_information["timestamp"]], utc=True
            )
            log = log[
                [
                    "case:concept:name",
                    xes.DEFAULT_TIMESTAMP_KEY,
                    xes.DEFAULT_TRACEID_KEY,
                ]
            ]

        # Transform the Timestamp to Datetime, and rename the transition:lifecycle
        elif log_information["log_type"] == "lifecycle":

            # Convert the Timestamps to Datetime
            log[log_information["timestamp"]] = pd.to_datetime(
                log[log_information["timestamp"]], utc=True
            )

            # Rename the Columns to the XES defaults
            log = log.rename(
                {log_information["lifecycle"]: xes.DEFAULT_TRANSITION_KEY}, axis=1
            )
            log = log[
                [
                    "case:concept:name",
                    xes.DEFAULT_TIMESTAMP_KEY,
                    xes.DEFAULT_TRACEID_KEY,
                    xes.DEFAULT_TRANSITION_KEY,
                ]
            ]
            log = data_transform.transform_lifecycle_csv_to_interval_csv(log)

        elif log_information["log_type"] == "timestamp":

            # Convert the Timestamps to Datetime
            log[log_information["end_timestamp"]] = pd.to_datetime(
                log[log_information["end_timestamp"]], utc=True
            )
            log[log_information["start_timestamp"]] = pd.to_datetime(
                log[log_information["start_timestamp"]], utc=True
            )

            log = log[
                [
                    "case:concept:name",
                    xes.DEFAULT_TIMESTAMP_KEY,
                    xes.DEFAULT_TRACEID_KEY,
                    xes.DEFAULT_START_TIMESTAMP_KEY,
                ]
            ]
            log = log.rename(
                {
                    log_information["start_timestamp"]: xes.DEFAULT_START_TIMESTAMP_KEY,
                    log_information["end_timestamp"]: xes.DEFAULT_TIMESTAMP_KEY,
                },
                axis=1,
            )

    return log
def process(Zone):
    def categorise(row):
        if type( row['TimeSpent']) is int :
            return row['TimeSpent']
        return row['TimeSpent'].days
    Zone['DaysSpent'] = Zone.apply(lambda row: categorise(row), axis=1)

    def categorise(row):
        if row['Count']==0:
            return 0
        return row['DaysSpent']/row['Count']
    Zone['AverageTimeSpent'] = Zone.apply(lambda row: categorise(row), axis=1)
    index=Zone.index.values
    try:
        Zone.insert(0, column='index',value = index+1)
    except:
        print("index already exists")

        algo_python = rpt.Pelt(model="rbf",min_size=1,jump=1).fit(Zone[[feature]])  # written in pure python
        result = algo_python.predict(penalty)
        Zone.loc[Zone['index'].isin(result),'drift']=1



def AnalyzeZone(Zone,featurelist,penalty,timeFrameValue,target=False):
    global timeFrame
    #reduced=pca_reduction(Zone[featurelist],len(featurelist), normalize = True, normalize_function="max")
    Zone['drift'] = 0
    for feature in featurelist:

        algo_python = rpt.Pelt(model="rbf",min_size=1,jump=1).fit(Zone[[feature]])  # written in pure python
        result = algo_python.predict(penalty)
        Zone.loc[Zone['index'].isin(result),'drift']=1
        fig, ax_array = rpt.display(Zone[feature], result)
        fig.suptitle('Change in Behaviour of '+feature+' over '+ timeFrameValue, fontsize=12)

        Zone['chunkmean'] = 0
        Zone['chunkindex'] = 1
        Zone['chunkstd']=0
        start=0
        sns.set(rc={'figure.figsize':(11.7,3.27)})
        i=1
        for index in result:
            Zone['chunkmean'].iloc[start:index]=Zone[ [feature] ].iloc[start:index].mean(axis=0)[0]
            Zone['chunkstd'].iloc[start:index]=Zone[ [feature] ].iloc[start:index].std(axis=0)[0]
            Zone['chunkindex'].iloc[start:index]=i
            i=i+1
            start=index
        Zone['pthreshold'] = Zone['chunkmean']+(Zone['chunkstd'])
        Zone['nthreshold'] = Zone['chunkmean']-(Zone['chunkstd'])

        if target==True:
            Zone['Strange_'+feature]=0
            def categorise(row,feature):
                if row['pthreshold'] < row[feature] or row['nthreshold']>row[feature] :
                    return 1
                return 0
            Zone['Strange_'+feature] = Zone.apply(lambda row: categorise(row,feature), axis=1)

        result=result[:-1]
        print(Zone.name,feature,result)




def create_analysis_dataframe(log, net, replayed_traces, group,log_information):

    global timeframe
    global sensitivity
    if sensitivity is None:
        sensitivity=3
    try:
        df=pd.read_csv(event_logs_path+'_'+log_information['log_name']+'_'+group.name+'_'+timeframe+'_'+str(sensitivity)+".csv")
        print('cached'+group.name)
        df['TimeSpent']=pd.to_timedelta(df['TimeSpent'])
        df['date']=pd.to_datetime(df['date'])
    except:
        df=createZone(log,net, replayed_traces, group)
        print('created'+group.name)
        df.to_csv(event_logs_path+'_'+log_information['log_name']+'_'+group.name+'_'+timeframe+'_'+str(sensitivity)+".csv", index = False, header=True)

    if timeframe is None:
        timeFrame='D'
    else :
        timeFrame=timeframe
    if timeFrame=='H':
        timeFrameValue='Hour(s)'
    if timeFrame=='D':
        timeFrameValue='Day(s)'
    if timeFrame=='W':
        timeFrameValue='Week(s)'
    if timeFrame=='M':
        timeFrameValue='Month(s)'

    df.name =group.name

    process(df)
    featurelist=['tokenproduced', 'tokenconsumed', 'tokenleft','oneframetoken', 'Count', 'AverageTimeSpent']
    AnalyzeZone(df,featurelist,sensitivity,timeFrameValue,True)
    return df

def set_sensitivity(param_sensitivity):
    global sensitivity
    sensitivity=float(param_sensitivity)
    return

def set_timeframe(param_timeframe):
    global timeframe
    timeframe=param_timeframe
    return