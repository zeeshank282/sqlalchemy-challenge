# Import the dependencies.
import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///C:/Users/zeesh/Starter_Code (6)/Starter_Code/Resources/hawaii.sqlite"")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
   return (
       f"Welcome to the Climate App!<br/>"
       f"Available Routes:<br/>"
       f"/api/v1.0/precipitation<br/>"
       f"/api/v1.0/stations<br/>"
       f"/api/v1.0/tobs<br/>"
       f"/api/v1.0/start<br/>"
       f"/api/v1.0/start/end"
   )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Calculate the date one year from the last date in data set.
    query_date = dt.date(2017, 8, 23)-dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    prcp_scores = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= query_date).all()

    # dictionary using date as the key and prcp as the value.
    precipData = []
    message = {'message': 'This is the data of precipitation in inches in the past 12 months'}
    precipData.append(message)
    for x in prcp_scores:
        precipDict = {'date':x.date, 'precipitation(inches)':x.prcp}
        precipData.append(precipDict)

    return jsonify(precipData)


@app.route("/api/v1.0/stations")
def stations():
    station_query = session.query(Station.station, Station.name).all()

    stationData = []
    message = {'message': 'This is the data of stations and its name'}
    stationData.append(message)
    for y in station_query:
        stationDict = {'station': y.station, 'name': y.name}
        stationData.append(stationDict)

    return jsonify(stationData)


@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year from the last date in the dataset
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature(TOBS).
    sel = [func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs)]
    tobs_query = session.query(*sel).\
    filter(Measurement.station == "USC00519281").all()

    # Query the last 12 months of temperature observation data for this station 
    query_temperature = session.query(Measurement.tobs).\
    filter(Measurement.station == "USC00519281").\
    filter(Measurement.date >= query_date).all()

    tobsData = []
    message = {'message': 'This is the data of the last 12 months of temperature observation data (tobs) for the station USC00519281'}
    tobsData.append(message)
    for z in query_temperature:
        tobsDict = {'tobs': z.tobs, 'date': query_date}
        tobsData.append(tobsDict)
        
    return jsonify(tobsData)

@app.route("/api/v1.0/start")
def start():
    startDate = dt.date(2010, 1, 1)

    sel = [Measurement.date,
           func.min(Measurement.tobs), 
           func.max(Measurement.tobs), 
           func.avg(Measurement.tobs)]
    tobs_query = session.query(*sel).\
        filter(Measurement.date >= startDate).\
        group_by(Measurement.date).all()

    startData = []

    message = {'message': 'This is the data of the TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.'}
    startData.append(message)

    for row in tobs_query:
        date_dict = {}
        date_dict["Date"] = row[0]
        date_dict["Min Temp"] = row[1]
        date_dict["Avg Temp"] = row[3]
        date_dict["Max Temp"] = row[2]
        startData.append(date_dict)

    return jsonify(startData)

@app.route("/api/v1.0/start/end")
def start_end():
    start_date = dt.date(2010, 1, 1)
    end_date = dt.date(2017, 8, 23)

    sel = [Measurement.date,
           func.min(Measurement.tobs),
           func.avg(Measurement.tobs),
           func.max(Measurement.tobs)]
    tobs_query = session.query(*sel).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).\
        group_by(Measurement.date).all()

    start_end_data = []
    message = {'message': f'This is the data of the TMIN, TAVG, and TMAX for the dates between {start_date} and {end_date}, inclusive.'}
    start_end_data.append(message)

    for result in tobs_query:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        start_end_data.append(date_dict)

    return jsonify(start_end_data)



if __name__ == '__main__':
    app.run(debug=True)