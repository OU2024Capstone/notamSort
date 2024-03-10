import unittest
import notamFetch

class TestNotams(unittest.TestCase) :

    ## Tests involving user input:

    # Test valid inputs in the frontend

    def test_inputs_valid(self):
        arrival_airport = "OKC"
        departure_airport = "DFW"
        print("Testing inputs with full city names")
        with self.assertRaises(Exception):
            notamFetch.get_all_notams(departure_airport, arrival_airport)
        

    # Test invalid inputs in the frontend
        
    def test_inputs_invalid(self):
        arrival_airport = "Oklahoma City"
        departure_airport = "Dallas"
        print("Testing inputs with full city names")
        with self.assertRaises(Exception):
            notamFetch.get_all_notams(departure_airport, arrival_airport)

    ## Tests involving valid airports:

    # Check two close airports in the continental US

    def test_close(self) :
        arrival_airport = "MCI" # Kansas City, MO
        departure_airport = "OKC" # Oklahoma City, OK
        print("Testing flight between " + departure_airport + " and " + arrival_airport)
        try:
            notamFetch.get_all_notams(departure_airport, arrival_airport)
        except Exception as err:
            self.fail("Airport was not located when it should have been.")

    # Check two far airports in the continental US
    
    def test_far(self) :
        arrival_airport = "PWM" # Portland, ME
        departure_airport = "LAX" # Los Angeles, CA
        print("Testing flight between " + departure_airport + " and " + arrival_airport)
        try:
            notamFetch.get_all_notams(departure_airport, arrival_airport)
        except Exception as err:
            self.fail("Airport was not located when it should have been.")

    # Check one airport in the continental US and one outside (i.e. Alaska and Hawaii)
            
    def test_alaska(self) :
        airport = "JNU" # Juneau, AK
        print("Testing " + airport)
        with self.assertRaises(Exception):
            notamFetch.get_notams_at(airport)

    def test_hawaii(self) :
        airport = "HNL" # Honolulu, HI
        print("Testing " + airport)
        with self.assertRaises(Exception):
            notamFetch.get_notams_at(airport)

    # Check one airport in the continental US and one outside (i.e. Canada, Mexico, etc.)
            
    def test_canada(self):
        airport = "YOW" # Ottawa, Canada
        print("Testing " + airport)
        with self.assertRaises(Exception):
            notamFetch.get_notams_at(airport)

    # Check two airports outside the continental US 
            
    def test_mexico(self):
        airport = "MEX" # Mexico City, Mexico
        print("Testing " + airport)
        with self.assertRaises(Exception):
            notamFetch.get_notams_at(airport)

    # Check two airports in other countries
    ''''
    def test_canada_mexico(self):
        arrival_airport = "YOW" # Ottawa, Canada
        departure_airport = "MEX" # Mexico City, Mexico
        print("Testing " + airport)
        with self.assertRaises(Exception):
            notamFetch.get_notams_at(airport)
    '''
