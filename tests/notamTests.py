import unittest
import notamFetch
from NavigationTools import *
from io import StringIO

class TestNotams(unittest.TestCase) :

    message_log = StringIO()

    ## Tests involving user input:

    # Tests involving valid inputs in the frontend

    # Checks to see if IATA codes are valid inputs.
    def test_inputs_valid_IATA(self):
        airport = "OKC"
        print("Testing IATA airport code input:")
        self.assertTrue(notamFetch.is_valid_US_airport_code(airport, self.message_log), 
                            f"{airport} was not detected as valid.")
          
    # Checks to see if ICAO codes are valid inputs.  
    def test_inputs_valid_ICAO(self):
        airport = "KOKC"
        print("Testing ICAO airport code input:")
        self.assertTrue(notamFetch.is_valid_US_airport_code(airport, self.message_log), 
                            f"{airport} was not detected as valid.")
        
    ## Tests involving invalid inputs in the frontend
        
    # Test should fail given no input.
    def test_inputs_invalid_none(self):
        airport = None
        print("Testing no inputs:")
        with self.assertRaises(ValueError):
            notamFetch.get_notams_at(airport, self.message_log)
            
    # Test should fail given a code with too few characters.
    def test_inputs_invalid_few_char(self):
        airport = "OK"
        print("Testing inputs fewer than 3:")
        self.assertFalse(notamFetch.is_valid_US_airport_code(airport, self.message_log), 
                                f"{airport} was detected as valid.")
        
    # Test should fail given a code with too many characters.
    def test_inputs_invalid_many_char(self):
        airport = "OKCDFW"
        print("Testing inputs greater than 4:")
        self.assertFalse(notamFetch.is_valid_US_airport_code(airport, self.message_log), 
                            f"{airport} was detected as valid.")
        
    # Test other non-string inputs such as int and double:
    def test_inputs_invalid_int(self):
        airport = 46
        print("Testing integer inputs:")
        with self.assertRaises(ValueError):
            notamFetch.get_notams_at(airport, self.message_log)

    def test_inputs_invalid_float(self):
        airport = 35.3955
        print("Testing float decimal inputs:")
        with self.assertRaises(ValueError):
            notamFetch.get_notams_at(airport, self.message_log)

    ## Tests involving invalid airport inputs:
            
    # Check one airport in the continental US and one outside (i.e. Alaska and Hawaii)
            
    def test_alaska_fail(self) :
        airport = "PAJN" # Juneau, AK
        print(f"Testing {airport}:")
        with self.assertRaises(Exception):
            notamFetch.get_notams_at(airport, self.message_log)

    def test_hawaii_fail(self) :
        airport = "PHNL" # Honolulu, HI
        print(f"Testing {airport}:")
        with self.assertRaises(Exception):
            notamFetch.get_notams_at(airport, self.message_log)

    # Check airports in North America (i.e. Canada, Mexico, etc.)
            
    def test_canada(self):
        airport = "CYOW" # Ottawa, Canada
        print(f"Testing {airport}:")
        self.assertFalse(notamFetch.is_valid_US_airport_code(airport, self.message_log), 
                            f"{airport} was detected as a valid US airport.")
            
    def test_mexico(self):
        airport = "MMMX" # Mexico City, Mexico
        print(f"Testing {airport}:")
        self.assertFalse(notamFetch.is_valid_US_airport_code(airport, self.message_log), 
                            f"{airport} was detected as a valid US airport.")

    # Check airports outside North America

    def test_germany_fail(self):
        airport = "EDDB" # Berlin, Germany
        print(f"Testing {airport}:")
        self.assertFalse(notamFetch.is_valid_US_airport_code(airport, self.message_log), 
                            f"{airport} was detected as a valid US airport.")

    ## Tests getting all notams with valid airports:

    # Check two close airports in the continental US
    
    def test_close(self) :
        arrival_airport = "KMCI" # Kansas City, MO
        departure_airport = "KOKC" # Oklahoma City, OK
        print(f"Testing flight between {departure_airport} and {arrival_airport}:")
        try:
            notamFetch.get_all_notams(departure_airport, arrival_airport, self.message_log)
        except ValueError as err:
            self.fail("Airport was flagged as being the wrong type when checked.")

    # Check two far airports in the continental US
    
    @unittest.skip("Currently this path is too far for the program to handle")
    def test_far(self) :
        arrival_airport = "KPWM" # Portland, ME
        departure_airport = "KLAX" # Los Angeles, CA
        print(f"Testing flight between {departure_airport} and {arrival_airport}:")
        try:
            notamFetch.get_all_notams(departure_airport, arrival_airport, self.message_log)
        except ValueError as err:
            self.fail("Airport was flagged as being the wrong type when checked.")