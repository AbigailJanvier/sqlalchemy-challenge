import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


# set up database
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Routes 
app = Flask(__name__)


# Create our session (link) from Python to the DB
session = Session(engine)

# Retrieve the last 12 months of data

# Find the most recent date in the data set.
recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    
# Calculate the date one year from the last date in data set.
year_ago = (dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)).date()

# Find the most active station id 
most_active = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()
most_active = most_active[0]



# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<p>Welcome to the Hawaii weather API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
    )

# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
   
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Perform a query to retrieve the data and precipitation scores
    date_prcp = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).\
        group_by(Measurement.date).all()
    return jsonify(date_prcp)



# Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():

    statn = session.query(Station.station, Station.name).all()
    return jsonify(statn)

# Query the dates and temperature observations of the most-active station for the previous year of data.

@app.route("/api/v1.0/tobs")
def tobs():

    tob = session.query(Measurement.date, Measurement.station == most_active, Measurement.tobs).filter(Measurement.date >= year_ago).all()
    return jsonify(tob)

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.

