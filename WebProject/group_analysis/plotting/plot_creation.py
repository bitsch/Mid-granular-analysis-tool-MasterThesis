import pandas as pd
import numpy as np
from django.conf import settings
import plotly.graph_objs as go
import plotly.io as pio
import core.plotting.plotting_utils as plt_util
import plotly.express as px
import datetime
from sklearn import tree,metrics
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report, confusion_matrix
from functools import reduce
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.linear_model import LinearRegression
from imblearn.over_sampling import RandomOverSampler
ros = RandomOverSampler(random_state=0)

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
def max_lag(x,y):
    corr = np.correlate(x, y, mode='full')
    # find lag with highest correlation
    lag = np.argmax(corr) - len(x) + 1
    # create lagged variable
    lagged_y = y.shift(lag)
    # calculate correlation between x and lagged_y
    corr = x.corr(lagged_y)
    return lag,corr

def correlation(predictordatedataframe,targetdatedataframe):
    result=[]

    Corrdataframe=pd.DataFrame(columns= ['targetZone','targetFeature','sourceZone','sourceFeature','lag','MaxCorr'])
    featurelist=['tokenproduced', 'tokenconsumed', 'tokenleft', 'oneframetoken', 'Count','AverageTimeSpent']
    targetZoneList=[predictordatedataframe,targetdatedataframe]
    for targetZone in targetZoneList:
        for targetFeature in featurelist:
            for zone in targetZoneList:
                lagsum=0
                for feature in featurelist:
                    maxlag,maxcorr = max_lag(targetZone[targetFeature].dropna(),zone[feature].dropna())
                    corrow_df = pd.DataFrame([[targetZone.name, targetFeature,zone.name, feature, maxlag,maxcorr]],columns=  ['targetZone','targetFeature','sourceZone','sourceFeature','lag','MaxCorr'])
                    Corrdataframe = pd.concat([corrow_df, Corrdataframe], ignore_index=True)
    Data=Corrdataframe[(Corrdataframe['MaxCorr']>0.7) & (Corrdataframe['lag']>0)].sort_values(by=['MaxCorr'], ascending=False).head(5)
    for index,row in Data.iterrows():
        result.append("Source: "+row['sourceFeature']+ " of "+row['sourceZone']+" target : "+row['targetFeature']+" of "+row['targetZone']+" Corr: "+ str(row['MaxCorr'])+" lag: "+str(row['lag']))
    return result

def traindtmultiple(x,y,columnlist,feature,i):
    ros = RandomOverSampler(random_state=0)
    try:
        X_resampled, y_resampled = ros.fit_resample(x, y)
        x_train, x_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size = 0.3)
    except:
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.3)
    #x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.3)
    clf = tree.DecisionTreeClassifier(criterion="entropy",max_depth=4,min_samples_leaf=15)
    clf = clf.fit(x_train, y_train)
    prediction=clf.predict(x_test)
    Y_test_pred = pd.DataFrame(prediction).applymap(lambda x: 1 if x>0.5 else 0)
    #Y_test_pred = pd.DataFrame(prediction)
    if accuracy_score(y_test, Y_test_pred)>0.7 and accuracy_score(y_test, Y_test_pred)<1 and f1_score(y_test, Y_test_pred, average="macro")>0.7:
        print('feature-',feature,':',' Day :',i)
        print("Mean absolute error LR-",metrics.mean_absolute_error(y_test, Y_test_pred))
        metrics.mean_squared_error(y_test, Y_test_pred)
        print("Mean Squared error LR-",np.sqrt(metrics.mean_squared_error(y_test, Y_test_pred)))
        print("Accuracy:",accuracy_score(y_test, Y_test_pred))
        print("F1:",f1_score(y_test, Y_test_pred, average="macro"))
        print("Precision:",precision_score(y_test, Y_test_pred, average="macro"))
        print("Recall:",recall_score(y_test, Y_test_pred, average="macro"))
        tree.plot_tree(clf,feature_names=columnlist,fontsize=16)
        cm = confusion_matrix(y_test, Y_test_pred)
        return 1
    return 0
def predict(targetZone,predictorZone,featurelist,predictionDelay):
    result=[]
    for feature in featurelist:
        combineddata=None
        for i in range(len(predictorZone)):
            if combineddata is None:
                combineddata=pd.merge(predictorZone[0],predictorZone[1],on=['date'],how='left',suffixes=("_"+predictorZone[0].name, "_"+predictorZone[1].name))
                combineddata['tokenproduced']=0
                combineddata['tokenconsumed']=0
                combineddata['tokenleft']=0
                combineddata['Count']=0
                combineddata['oneframetoken']=0
                combineddata['AverageTimeSpent']=0
            elif i>1:
                combineddata=combineddata.merge(predictorZone[i],on=['date'],how='left',suffixes=(None,"_"+predictorZone[i].name))

        def categorise(row,numdays):
            return row['date'] -  datetime.timedelta(hours=1)
        for j in range (predictionDelay):
            combineddata=combineddata.merge(targetZone[['date',feature]].rename({feature: feature+'_'+str(j)}, axis=1), on='date', how='left')
            targetZone['date'] = targetZone.apply(lambda row: categorise(row,j), axis=1)
        combineddata=combineddata.dropna()
        for j in range (predictionDelay):
            combineddata[feature+'_'+str(j)] = combineddata[feature+'_'+str(j)].astype(int)

        columnlist=[]
        columnlist.extend(combineddata.loc[:, combineddata.columns.str.startswith('token')].columns)
        columnlist.extend(combineddata.loc[:, combineddata.columns.str.startswith('oneframetoken')].columns)
        columnlist.extend(combineddata.loc[:, combineddata.columns.str.startswith('AverageTimeSpent')].columns)
        columnlist.extend(combineddata.loc[:, combineddata.columns.str.startswith('Count')].columns)
        x = combineddata[columnlist]
        columnlistnew = [s.replace('token', 'token ') for s in columnlist]
        columnlistnew = [s.replace('oneframetoken', 'one frame token') for s in columnlistnew]
        columnlistnew = [s.replace('AverageTimeSpent', 'Time Spent') for s in columnlistnew]

        for i in range(predictionDelay):

            y = combineddata[feature+'_'+str(i)].fillna(0).copy()
            x = combineddata[columnlist].copy()
            res = traindtmultiple(x,y,columnlistnew,feature,i)
            if res>0:
                result.append("Model Trained with good metrics for feature "+feature+" with a delay of "+str(i)+" timeframe.")
    return result


def prediction(predictordatedataframe,targetdatedataframe):
    result=[]
    predictionDelay=40
    targetfeaturelist=['Strange_tokenproduced', 'Strange_tokenconsumed', 'Strange_tokenleft','Strange_oneframetoken',
                     'Strange_Count', 'Strange_AverageTimeSpent']
    targetZoneList=[targetdatedataframe]
    zonelist=[predictordatedataframe,targetdatedataframe]
    for targetZone in targetZoneList:
        print(targetZone.name)
        result=predict(targetZone.copy(),zonelist,targetfeaturelist,predictionDelay)
    return result

def make_prediction(preddf,targetdf):
    result=[]
    result.extend(correlation(preddf,targetdf))
    result.extend(prediction(preddf,targetdf))
    return result