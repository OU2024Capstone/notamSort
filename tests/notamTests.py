import unittest
import notamFetch
from NavigationTools import *

class TestNotams(unittest.TestCase) :

    ## Tests involving user input:

    # Test valid inputs in the frontend

    @unittest.skip("Waiting on IATA code inputs to be murged to main.")
    def test_inputs_valid_IATA(self):
        arrival_airport = PointObject.from_airport_code("OKC")
        departure_airport = PointObject.from_airport_code("DFW")
        print("Testing IATA airport code inputs:")
        try:
            notamFetch.get_notams_at(departure_airport)
            notamFetch.get_notams_at(arrival_airport)
        except Exception as err:
            self.fail("Airport was not located when it should have been.")
    
    def test_inputs_valid_ICAO(self):
        arrival_airport = PointObject.from_airport_code("KOKC")
        departure_airport = PointObject.from_airport_code("KDFW")
        print("Testing ICAO airport code inputs:")
        try:
            notamFetch.get_notams_at(departure_airport)
            notamFetch.get_notams_at(arrival_airport)
        except Exception as err:
            self.fail("Airport was not located when it should have been.")
        
    # Test invalid inputs in the frontend
        
    def test_inputs_invalid_none(self):
        airport = None
        print("Testing no inputs:")
        with self.assertRaises(Exception):
            notamFetch.get_notams_at(airport)

    def test_inputs_invalid_int(self):
        airport = 46
        print("Testing integer inputs:")
        with self.assertRaises(Exception):
            notamFetch.get_notams_at(airport)

    def test_inputs_invalid_float(self):
        airport = 35.3955
        print("Testing float decimal inputs:")
        with self.assertRaises(Exception):
            notamFetch.get_notams_at(airport)

    ## Tests involving valid airports:

    # Check two close airports in the continental US
    
    @unittest.skip("get_all_notams takes awhile to run as of now.")
    def test_close(self) :
        arrival_airport = "KMCI" # Kansas City, MO
        departure_airport = "KOKC" # Oklahoma City, OK
        print("Testing flight between " + departure_airport + " and " + arrival_airport + ":")
        try:
            notamFetch.get_all_notams(departure_airport, arrival_airport)
        except Exception as err:
            self.fail("Airport was not located when it should have been.")

    # Check two far airports in the continental US
    
    @unittest.skip("get_all_notams takes awhile to run as of now.")
    def test_far(self) :
        arrival_airport = "KPWM" # Portland, ME
        departure_airport = "KLAX" # Los Angeles, CA
        print("Testing flight between " + departure_airport + " and " + arrival_airport + ":")
        try:
            notamFetch.get_all_notams(departure_airport, arrival_airport)
        except Exception as err:
            self.fail("Airport was not located when it should have been.")
    
    ## Tests involving invalid airports:

    # Check one airport in the continental US and one outside (i.e. Alaska and Hawaii)
            
    def test_alaska_fail(self) :
        airport = "PAJN" # Juneau, AK
        print("Testing " + airport + ":")
        with self.assertRaises(Exception):
            notamFetch.get_notams_at(airport)

    def test_hawaii_fail(self) :
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

    def test_germany_fail(self):
        airport = "EDDB" # Berlin, Germany
        print("Testing " + airport + ":")
        with self.assertRaises(Exception):
            notamFetch.get_notams_at(airport)
