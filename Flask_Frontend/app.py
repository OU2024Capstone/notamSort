from flask import Flask, request
from flask import render_template
app = Flask(__name__)
#import notamFetch

# Home displays the form for user input
@app.route("/")
def home():
    return render_template(
        "user_input.html",
    )

# /query displays the notams
@app.route('/query/', methods = ['POST', 'GET'])
def query():
    if request.method == 'POST':
        #notamFetch.getNotams(depAP, arrAP)
        return render_template('query.html', 
                DepartureAirport = request.form['DepartureAirport'], 
                ArrivalAirport = request.form['ArrivalAirport'])