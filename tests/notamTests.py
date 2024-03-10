import unittest
import notamFetch
from NavigationTools import *

class TestNotams(unittest.TestCase) :

    ## Tests involving user input:

    # Test valid inputs in the frontend
    '''' Will remove comment if IATA becomes a valid input (or move to invalid)
    def test_inputs_valid_IATA(self):
        arrival_airport = PointObject.from_airport_code("OKC")
        departure_airport = PointObject.from_airport_code("DFW")
        print("Testing inputs with airport codes:")
        try:
            notamFetch.get_notams_at(departure_airport)
            notamFetch.get_notams_at(arrival_airport)
        except Exception as err:
            self.fail("Airport was not located when it should have been.")
    '''
    def test_inputs_valid_ICAO(self):
        arrival_airport = PointObject.from_airport_code("KOKC")
        departure_airport = PointObject.from_airport_code("KDFW")
        print("Testing inputs with airport codes:")
        try:
            notamFetch.get_notams_at(departure_airport)
            notamFetch.get_notams_at(arrival_airport)
        except Exception as err:
            self.fail("Airport was not located when it should have been.")
        
    # Test invalid inputs in the frontend
        
    def test_inputs_invalid_none(self):
        arrival_airport = None
        departure_airport = None
        print("Testing no inputs:")
        with self.assertRaises(Exception):
            notamFetch.get_notams_at(departure_airport)
            notamFetch.get_notams_at(arrival_airport)

    def test_inputs_invalid_int(self):
        arrival_airport = 46
        departure_airport = 28
        print("Testing integer inputs:")
        with self.assertRaises(Exception):
            notamFetch.get_notams_at(departure_airport)
            notamFetch.get_notams_at(arrival_airport)

    def test_inputs_invalid_float(self):
        arrival_airport = 35.3955
        departure_airport = 97.5962
        print("Testing float decimal inputs:")
        with self.assertRaises(Exception):
            notamFetch.get_notams_at(departure_airport)
            notamFetch.get_notams_at(arrival_airport)

    ## Tests involving valid airports:

    # Check two close airports in the continental US
    ''''
    def test_close(self) :
        arrival_airport = "KMCI" # Kansas City, MO
        departure_airport = "KOKC" # Oklahoma City, OK
        print("Testing flight between " + departure_airport + " and " + arrival_airport + ":")
        try:
            notamFetch.get_all_notams(departure_airport, arrival_airport)
        except Exception as err:
            self.fail("Airport was not located when it should have been.")
    '''
    # Check two far airports in the continental US
    ''''
    def test_far(self) :
        arrival_airport = "KPWM" # Portland, ME
        departure_airport = "KLAX" # Los Angeles, CA
        print("Testing flight between " + departure_airport + " and " + arrival_airport + ":")
        try:
            notamFetch.get_all_notams(departure_airport, arrival_airport)
        except Exception as err:
            self.fail("Airport was not located when it should have been.")
    '''
    ## Tests involving invalid airports:

    # Check one airport in the continental US and one outside (i.e. Alaska and Hawaii)
            
    def test_alaska(self) :
        airport = "PAJN" # Juneau, AK
        print("Testing " + airport + ":")
        with self.assertRaises(Exception):
            notamFetch.get_notams_at(airport)

    def test_hawaii(self) :
        airport = "PHNL" # Honolulu, HI
        print("Testing " + airport + ":")
        with self.assertRaises(Exception):
            notamFetch.get_notams_at(airport)

    # Check airports in North America (i.e. Canada, Mexico, etc.)
            
    def test_canada(self):
        airport = "CYOW" # Ottawa, Canada
        print("Testing " + airport + ":")
        with self.assertRaises(Exception):
            notamFetch.get_notams_at(airport)
            
    def test_mexico(self):
        airport = "MMMX" # Mexico City, Mexico
        print("Testing " + airport + ":")
        with self.assertRaises(Exception):
            notamFetch.get_notams_at(airport)

    # Check airports outside North America
    '''' Need to change this to be another country,
    def test_canada_mexico(self):
        arrival_airport = "CYOW" # Ottawa, Canada
        departure_airport = "MMMX" # Mexico City, Mexico
        print("Testing " + airport + ":")
        with self.assertRaises(Exception):
            notamFetch.get_notams_at(airport)
    '''
