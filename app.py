from io import StringIO
from flask import Flask, jsonify, request
from flask import render_template
import NotamFetch
from flask_table import Table, Col

app = Flask(__name__)
# All print statements write to output, which is displayed on the homepage.
message_log = StringIO()
figure = None

# Home displays the form for user input
@app.route("/")
def home():
    return render_template(
        "user_input.html"
    )

# /query displays the notams
@app.route('/query/', methods = ['POST', 'GET'])
def query():
    """Search functionality using the search button is implemented here.

    When a user clicks the 'search' button, notamFetch is called to 
    retreive all relevant notams, and this list is passed to webpage 
    /query as a NotamTable.
    """
    if request.method == 'POST':
        clear_log()
        NotamFetch.clear_map()
        
        departure_airport = request.form['DepartureAirport']
        arrival_airport = request.form['ArrivalAirport']
        
        print(f"Finding all NOTAMs on flight path from {departure_airport} to {arrival_airport}.", file=message_log)

        # call backend to retrieve list of notams
        all_notams = NotamFetch.get_all_notams(
            departure_airport = departure_airport, 
            arrival_airport = arrival_airport, message_log=message_log)
        
        figure = NotamFetch.get_map()

        return render_template('query.html', 
                               figure = figure,
                               table = NotamTable(all_notams, border='1px solid black'),
                               DepartureAirport = departure_airport, 
                               ArrivalAirport = arrival_airport)

@app.errorhandler(Exception)
def handle_backend_errors(e):
        return render_template("error.html", error_message = e)

@app.route('/out', methods=['GET'])
def out():
    """Returns all printed messages as a JSON-formatted Response object.
    
    Real-time query updates can be displayed on the homepage by converting 
    the json response into text.
    """

    # Use seek(0) to read from the start of the StringIO
    message_log.seek(0)

    return jsonify(message_log.read())

def clear_log():
    """Clears all log messages."""

    message_log.truncate(0)
    message_log.seek(0)

class TextCol(Col):
    """Replaces newlines with <br></br> in a table column for HTML display."""

    def td_format(self, content):
       return content.replace("\n", "<br />")

class NotamTable(Table):
    """It's a table...for notams.

    Implements a custom html Table object using flask_table, which will
    automatically create an html table from a list of Notam objects. 
    Table can be made like so:
        table = NotamTable(all_notams)
    """

    location = Col('Location')
    number = Col('Number')
    effective_start = Col('Effective Start')
    effective_end = Col('Effective End')
    text = TextCol('Description')
    type = Col('Type')
    selection_code = Col('Selection Code')
    traffic = Col('Traffic')
    purpose = Col('Purpose')
    score = Col('Score')