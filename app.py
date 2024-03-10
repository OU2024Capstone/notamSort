from flask import Flask, request
from flask import render_template
import notamFetch
from flask_table import Table, Col

app = Flask(__name__)

# Home displays the form for user input
@app.route("/")
def home():
    return render_template(
        "user_input.html",
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
        # call backend to retrieve list of notams
        all_notams = notamFetch.get_all_notams(
            departure_airport = departure_airport, 
            arrival_airport = arrival_airport)
        
        return render_template('query.html', 
                               table = NotamTable(all_notams, border='1px solid black'),
                               DepartureAirport = departure_airport, 
                               ArrivalAirport = arrival_airport)
    
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

