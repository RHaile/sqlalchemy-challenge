import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precip = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > query_date).\
        order_by(Measurement.date).all()

    session.close()

    list = []
    for result in precip:
        dict = {"Date":result[0],"Precipitation":result[1]}
        list.append(dict)
    return jsonify(list)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations = session.query(Station.station, Station.name).all()

    session.close()

    list=[]
    for station in stations:
        dict = {"Station ID:":station[0],"Station Name":station[1]}
        list.append(dict)

    return jsonify(list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    active = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc())[0][0]

    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > query_date).\
    filter(Measurement.station==active).order_by(Measurement.date.desc()).all()
    
    session.close()

    list = []
    for temp in tobs:
        dict = {"date": temp[0], "tobs": temp[1]}
        list.append(dict)

    return jsonify(list)

@app.route("/api/v1.0/<start>")
def trip1(start):
    session = Session(engine)
    
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= query_date).order_by(Measurement.date.desc()).all()
    
    session.close()
    
    for temps in results:
        dict = {"Minimum Temp":results[0][0],"Average Temp":results[0][1],"Maximum Temp":results[0][2]}

    return jsonify(dict)

@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end): 
    session = Session(engine)
    
    trip_start = dt.date(2017, 12, 23) - dt.timedelta(days=365)
    trip_end = dt.date(2017, 12, 28) - dt.timedelta(days=365)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
                  filter(Measurement.date >= trip_start, Measurement.date <= trip_end).order_by(Measurement.date.desc()).all()

    session.close()

    for temps in results:
        dict = {"Minimum Temp":results[0][0],"Average Temp":results[0][1],"Maximum Temp":results[0][2]}
    return jsonify(dict)

if __name__ == '__main__':
    app.run(debug=True)
