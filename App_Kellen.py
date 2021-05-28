# Import Modules
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from sqlalchemy.sql.expression import true

# Database Setup
engine = create_engine(f"sqlite:////Users/kellenquinn/Desktop/SQLALCHEMY CHALLENGE/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)
print(Base.classes.keys())

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Create Session
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return ( 
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start</br>"
        f"/api/v1.0/start/end"
    )   

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    #Create our session from Python to the DB
    session = Session(engine)

    """Return list of all precipitation data"""

    # Calculate the date one year from the last date in data set.
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date_dt=dt.date.fromisoformat(last_date[0])
    prev_date_dt=last_date_dt-dt.timedelta(days=365)
    prev_date_dt

    #Query of all data
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_date_dt).all()  

    session.close()

    #Create a dictionary from the row data and append to a list of all_precipitation
    all_precipitation = []
    for date, prcp, in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp

        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)    

@app.route("/api/v1.0/stations")
def stations():

    #Create our session from Python to the DB
    session = Session(engine)

    """Return list of all station data"""
    results = session.query(Station.station).all()
    
    session.close()

    #Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():

    #Create our session from Python to the DB
    session = Session(engine)

    """Return list of all tobs data"""

    # Calculate the date one year from the last date in data set.
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date_dt=dt.date.fromisoformat(last_date[0])
    prev_date_dt=last_date_dt-dt.timedelta(days=365)
    prev_date_dt

    station_id = 'USC00519281'

    results = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
    filter(Measurement.station == station_id).\
    filter(Measurement.date > prev_date_dt).all()

    session.close()

    #Create a dictionary from the row data and append to a list of all_tobs
    all_tobs = []
    for station, date, tobs in results:
        tobs_dict = {}
        tobs_dict["station"] = station
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs

        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start_date>") 
def stats(start_date = None):

    last_date_dt=dt.datetime.strptime(start_date, '%Y-%M-%d').date()
    print(last_date_dt)
    #Create our session from Python to the DB
    session = Session(engine)

    """Return list of min, max, and avg tob start data"""

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= last_date_dt).all()
    print(results)
    session.close() 

    return jsonify(results)    

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end_date(start_date, end_date):

    start_date_dt=dt.datetime.strptime(start_date, '%Y-%M-%d').date()
    end_date_dt=dt.datetime.strptime(end_date, '%Y-%M-%d').date()

    #Create our session from Python to the DB
    session = Session(engine)

    """Return list of min, max, and avg tob start and end data"""

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date_dt).filter(Measurement.date <= end_date_dt).all()

    session.close()

    return jsonify(results)        

if __name__ == '__main__':
    app.run()