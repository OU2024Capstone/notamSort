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
            notamFetch.get_all_notams(arrival_airport, departure_airport)
        

    # Test invalid inputs in the frontend
        
    def test_inputs_invalid(self):
        arrival_airport = "Oklahoma City"
        departure_airport = "Dallas"
        print("Testing inputs with full city names")
        with self.assertRaises(Exception):
            notamFetch.get_all_notams(arrival_airport, departure_airport)

    ## Tests involving valid airports:

    # Check two close airports in the continental US

    def test_close(self) :
        arrival_airport = "MCI" # Kansas City, MO
        departure_airport = "OKC" # Oklahoma City, OK
        print("Testing flight between " + arrival_airport + " and " + departure_airport)
        try:
            notamFetch.get_all_notams(arrival_airport, departure_airport)
        except Exception as err:
            self.fail("Airport was not located when it should have been.")

    # Check two far airports in the continental US
    
    def test_far(self) :
        arrival_airport = "PWM" # Portland, ME
        departure_airport = "LAX" # Los Angeles, CA
        print("Testing flight between " + arrival_airport + " and " + departure_airport)
        try:
            notamFetch.get_all_notams(arrival_airport, departure_airport)
        except Exception as err:
            self.fail("Airport was not located when it should have been.")

    # Check one airport in the continental US and one outside (i.e. Alaska and Hawaii)
            
    def test_alaska(self) :
        arrival_airport = "JNU" # Juneau, AK
        departure_airport = "OKC" # Oklahoma City, OK
        print("Testing flight between " + arrival_airport + " and " + departure_airport)
        try:
            notamFetch.get_all_notams(arrival_airport, departure_airport)
        except Exception as err:
            self.fail("Alaska Test Failed: Airport was found.")

    def test_hawaii(self) :
        arrival_airport = "HNL" # Honolulu, HI
        departure_airport = "OKC" # Oklahoma City, OK
        print("Testing flight between " + arrival_airport + " and " + departure_airport)
        try:
            notamFetch.get_all_notams(arrival_airport, departure_airport)
        except Exception as err:
            self.fail("Hawaii Test Failed: Airport was found.")

    # Check one airport in the continental US and one outside (i.e. Canada, Mexico, etc.)
            
    def test_canada(self):
        arrival_airport = "YOW" # Ottawa, Canada
        departure_airport = "DCA" # Washington D.C
        print("Testing flight between " + arrival_airport + " and " + departure_airport)
        try:
            notamFetch.get_all_notams(arrival_airport, departure_airport)
        except Exception as err:
            self.fail("Canada Test Failed: Airport was found.") 

    # Check two airports outside the continental US 
            
    def test_mexico(self):
        arrival_airport = "MEX" # Mexico City, Mexico
        departure_airport = "DCA"  # Washington D.C
        print("Testing flight between " + arrival_airport + " and " + departure_airport)
        try:
            notamFetch.get_all_notams(arrival_airport, departure_airport)
        except Exception as err:
            self.fail("Mexico Test Failed: Airport was found.")

    # Check two airports in other countries
            
    def test_canada_mexico(self):
        arrival_airport = "YOW" # Ottawa, Canada
        departure_airport = "MEX" # Mexico City, Mexico
        print("Testing flight between " + arrival_airport + " and " + departure_airport)
        try:
            notamFetch.get_all_notams(arrival_airport, departure_airport)
        except Exception as err:
            self.fail("Canada to Mexico Test Failed: Airport was found.")
    