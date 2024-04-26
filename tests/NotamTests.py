from io import StringIO
import unittest
import warnings
import NotamFetch
from NavigationTools import *
import time

class TestNotams(unittest.TestCase) :
    
    # Will not actually be used, but needs to be passed as an argument in notamFetch.
    dummy_output = StringIO()
    
    ## Tests involving user input:

    # Tests involving valid inputs in the frontend

    # Checks to see if IATA codes are valid inputs.
    def test_inputs_valid_IATA(self):
        airport = "OKC"
        print("Testing IATA airport code input:")
        self.assertTrue(NotamFetch.is_valid_US_airport_code(airport, self.dummy_output), 
                            f"{airport} was not detected as valid.")
          
    # Checks to see if ICAO codes are valid inputs.  
    def test_inputs_valid_ICAO(self):
        airport = "KOKC"
        print("Testing ICAO airport code input:")
        self.assertTrue(NotamFetch.is_valid_US_airport_code(airport, self.dummy_output), 
                            f"{airport} was not detected as valid.")
        
    ## Tests involving invalid inputs in the frontend
        
    # Test should fail given no input.
    def test_inputs_invalid_none(self):
        airport = None
        print("Testing no inputs:")
        try:
            NotamFetch.get_notams_at(airport, 25, self.dummy_output)
            self.fail("Airport was flagged as being the wrong type when checked.")
        except ValueError as err:
            pass
            
            
    # Test should fail given a code with too few characters.
    def test_inputs_invalid_few_char(self):
        airport = "OK"
        print("Testing inputs fewer than 3:")
        try:
            NotamFetch.is_valid_US_airport_code(airport, self.dummy_output)
            self.fail("Airport was detected as valid.")
        except ValueError as err:
            pass
            
        
    # Test should fail given a code with too many characters.
    def test_inputs_invalid_many_char(self):
        airport = "OKCDFW"
        print("Testing inputs greater than 4:")
        try:
            NotamFetch.is_valid_US_airport_code(airport, self.dummy_output)
            self.fail("Airport was detected as valid.")
        except ValueError as err:
            pass
        
    # Test other non-string inputs such as int and double:
    def test_inputs_invalid_int(self):
        airport = 46
        print("Testing integer inputs:")
        with self.assertRaises(ValueError):
            NotamFetch.get_notams_at(airport, 25, self.dummy_output)

    def test_inputs_invalid_float(self):
        airport = 35.3955
        print("Testing float decimal inputs:")
        with self.assertRaises(ValueError):
            NotamFetch.get_notams_at(airport, 25, self.dummy_output)

    ## Tests involving invalid airport inputs:
            
    # Check one airport in the continental US and one outside (i.e. Alaska and Hawaii)
            
    def test_alaska_fail(self) :
        airport = "PAJN" # Juneau, AK
        print(f"Testing {airport}:")
        with self.assertRaises(Exception):
            NotamFetch.get_notams_at(airport, 25, self.dummy_output)

    def test_hawaii_fail(self) :
        airport = "PHNL" # Honolulu, HI
        print(f"Testing {airport}:")
        with self.assertRaises(Exception):
            NotamFetch.get_notams_at(airport, 25, self.dummy_output)

    # Check airports in North America (i.e. Canada, Mexico, etc.)
            
    def test_canada(self):
        airport = "CYOW" # Ottawa, Canada
        print(f"Testing {airport}:")
        try:
            NotamFetch.is_valid_US_airport_code(airport, self.dummy_output)
            self.fail("Airport was detected as valid.")
        except ValueError as err:
            pass
            
    def test_mexico(self):
        airport = "MMMX" # Mexico City, Mexico
        print(f"Testing {airport}:")
        self.assertFalse(NotamFetch.is_valid_US_airport_code(airport, self.dummy_output), 
                            f"{airport} was detected as a valid US airport.")

    # Check airports outside North America

    def test_germany_fail(self):
        airport = "EDDB" # Berlin, Germany
        print(f"Testing {airport}:")
        self.assertFalse(NotamFetch.is_valid_US_airport_code(airport, self.dummy_output), 
                            f"{airport} was detected as a valid US airport.")

    ## Tests getting all notams with valid airports:

    # Check two close airports in the continental US
    
    def test_close(self) :
        arrival_airport = "KMCI" # Kansas City, MO
        departure_airport = "KOKC" # Oklahoma City, OK
        print(f"Testing flight between {departure_airport} and {arrival_airport}:")
        try:
            NotamFetch.get_all_notams(departure_airport, arrival_airport, self.dummy_output)
        except ValueError as err:
            self.fail("Airport was flagged as being the wrong type when checked.")

    # Check two far airports in the continental US
    
    @unittest.skip("Currently this path is too far for the program to handle")
    def test_far(self) :
        arrival_airport = "KPWM" # Portland, ME
        departure_airport = "KLAX" # Los Angeles, CA
        print(f"Testing flight between {departure_airport} and {arrival_airport}:")
        try:
            NotamFetch.get_all_notams(departure_airport, arrival_airport, self.dummy_output)
        except ValueError as err:
            self.fail("Airport was flagged as being the wrong type when checked.")
       
# Make sure to run `python3 -m unittest tests.NotamTests.TestNotamSpeed.[test_name]` to run the tests in this class.
# Adding a warning filter on these tests as they need a StringIO to pass through as a parameter.
# We do not need to worry about the ResourceWarnings nor the output into the StringIO.
# If you need to add any tests, make sure that filter is present if you only want the end result.
class TestNotamSpeed(unittest.TestCase) :
    
    # Will not actually be used, but needs to be passed as an argument in notamFetch.
    dummy_output = StringIO()
    
    # Testing the efficiency of out method with short distances and long distances.
    
    ## The following test takes the same airport twice to check the efficiency of the shortest distance possible, that being 0.0.
    def test_zero_dist_eff(self) :
        warnings.simplefilter("ignore", category=ResourceWarning)
        airport = "OKC" # Oklahoma City, OK
        print(f"Testing speed efficiency between {airport} and {airport}")
        start_time = time.time()
        try :
            NotamFetch.get_all_notams(airport, airport, self.dummy_output)
        except RuntimeError as err:
            raise err
        end_time = time.time()
        run_time = end_time - start_time
        if (run_time >= 30) :
            self.fail(f"get_all_notams was not able to complete in less than 30 seconds given {airport} and {airport}. Time elapsed: {run_time}")
        else :
            print(f"Elapsed time to find notams between {airport} and {airport}: {run_time}")
            
    ## The following two tests take two flight paths across the US that are very short, about ~10 nm from each other, and testing our method's efficiency.
    def test_close_eff_1(self) :
        warnings.simplefilter("ignore", category=ResourceWarning)
        arrival_airport = "DFW" # Dallas, TX
        departure_airport = "DAL" # Dallas, TX
        print(f"Testing speed efficiency between {arrival_airport} and {departure_airport}")
        start_time = time.time()
        try :
            NotamFetch.get_all_notams(departure_airport, arrival_airport, self.dummy_output)
        except RuntimeError as err:
            raise err
        end_time = time.time()
        run_time = end_time - start_time
        if (run_time >= 30) :
            self.fail(f"get_all_notams was not able to complete in less than 30 seconds given {arrival_airport} and {departure_airport}. Time elapsed: {run_time}")
        else :
            print(f"Elapsed time to find notams between {arrival_airport} and {departure_airport}: {run_time}")
            
    def test_close_eff_2(self) :
        warnings.simplefilter("ignore", category=ResourceWarning)
        arrival_airport = "OUN" # Norman, OK
        departure_airport = "OKC" # Oklahoma City, OK
        print(f"Testing speed efficiency between {arrival_airport} and {departure_airport}")
        start_time = time.time()
        try :
            NotamFetch.get_all_notams(departure_airport, arrival_airport, self.dummy_output)
        except RuntimeError as err:
            raise err
        end_time = time.time()
        run_time = end_time - start_time
        if (run_time >= 30) :
            self.fail(f"get_all_notams was not able to complete in less than 30 seconds given {arrival_airport} and {departure_airport}. Time elapsed: {run_time}")
        else :
            print(f"Elapsed time to find notams between {arrival_airport} and {departure_airport}: {run_time}")
    
    ## The following two tests take two flight paths across the US that are very long, from about coast to coast, and testing our method's efficiency.
    def test_far_eff_1(self) :
        warnings.simplefilter("ignore", category=ResourceWarning)
        arrival_airport = "KEYW" # Key West, FL
        departure_airport = "KBLI" # Bellingham, WA
        print(f"Testing speed efficiency between {arrival_airport} and {departure_airport}")
        start_time = time.time()
        try :
            NotamFetch.get_all_notams(departure_airport, arrival_airport, self.dummy_output)
        except RuntimeError as err:
            raise err
        end_time = time.time()
        run_time = end_time - start_time
        if (run_time >= 30) :
            self.fail(f"get_all_notams was not able to complete in less than 30 seconds given {arrival_airport} and {departure_airport}. Time elapsed: {run_time}")
        else :
            print(f"Elapsed time to find notams between {arrival_airport} and {departure_airport}: {run_time}")
            
    def test_far_eff_2(self) :
        warnings.simplefilter("ignore", category=ResourceWarning)
        arrival_airport = "STS" # Santa Rosa, CA
        departure_airport = "BGR" # Bangor, ME
        print(f"Testing speed efficiency between {arrival_airport} and {departure_airport}")
        start_time = time.time()
        try :
            NotamFetch.get_all_notams(departure_airport, arrival_airport, self.dummy_output)
        except RuntimeError as err:
            raise err
        end_time = time.time()
        run_time = end_time - start_time
        if (run_time >= 30) :
            self.fail(f"get_all_notams was not able to complete in less than 30 seconds given {arrival_airport} and {departure_airport}. Time elapsed: {run_time}")
        else :
            print(f"Elapsed time to find notams between {arrival_airport} and {departure_airport}: {run_time}")
