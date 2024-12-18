# import necessary packages
import numpy as np
from pybaseball import statcast
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from math import sqrt

# set up global variables
Model = None
scaler = None

# This method retrains the model on the latest month of data
def refresh_data():
    global scaler
    # Get today's date
    today = datetime.today()

    # Get the date for 3 weeks ago and a month before that
    week_ago = today - timedelta(weeks=3)
    month_ago = week_ago - timedelta(weeks=5)

    # get data
    data = statcast(week_ago.strftime('%Y-%m-%d'), month_ago.strftime('%Y-%m-%d'), verbose=False)


    # clean and organize data
    nan_indices1 = data[data['release_speed'].isna()].index
    data = data.drop(index=nan_indices1, axis=0)
    # input features
    X = data[['release_speed', 'zone', 'pfx_x', 'pfx_z', 'balls', 'strikes']]
    # output features
    y = data['description']
    yArr = np.ravel(y)
    # Change the output feature to contain only ball, strike, and contact
    for i in range(len(yArr)):
        if yArr[i] == 'blocked_ball':
            yArr[i] = 'ball'
        elif yArr[i] == 'foul_tip':
            yArr[i] = 'strike'
        elif yArr[i] == 'swinging_strike_blocked':
            yArr[i] = 'strike'
        elif yArr[i] == 'hit_by_pitch':
            yArr[i] = 'ball'
        elif yArr[i] == 'foul_bunt':
            yArr[i] = 'contact'
        elif yArr[i] == 'missed_bunt':
            yArr[i] = 'strike'
        elif yArr[i] == 'pitchout':
            yArr[i] = 'ball'
        elif yArr[i] == 'bunt_foul_tip':
            yArr[i] = 'contact'
        elif yArr[i] == 'swinging_strike':
            yArr[i] = 'strike'
        elif yArr[i] == 'called_strike':
            yArr[i] = 'strike'
        elif yArr[i] == 'foul':
            yArr[i] = 'contact'
        elif yArr[i] == 'hit_into_play':
            yArr[i] = 'contact'

    # scale data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    # call the train model method
    trainModel(X_scaled, y)

# this method trains the model on our data
def trainModel(X_train, y_train):
    global Model
    n = int(sqrt(len(X_train)))
    # ML model training
    Model = KNeighborsClassifier(n_neighbors=n, weights='distance', p=1, algorithm='auto')
    Model.fit(X_train, y_train)
    print('trained')

# use the model to get the pitch outcome probabilities and return them
def getResult(pitch_input):
    global Model
    global scaler
    # change input to a 2D array
    pitch_input = [pitch_input]
    # scale the input
    pitch_input = scaler.transform(pitch_input)
    
    if Model != None:
        # get the probabilities
        result = Model.predict_proba(pitch_input)
        return result
    else:
        return "Model is null"

