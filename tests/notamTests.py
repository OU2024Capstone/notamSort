import unittest
import notamFetch

class TestNotams(unittest.TestCase) :

    ## Tests involving user input:

    # Test valid inputs in the frontend

    # Test invalid inputs in the frontend

    ## Tests involving valid airports:

    # Check two close airports in the continental US

    def test_close(self) :
        arrival_airport = "MCI"
        destination_airport = "OKC"
        print("Testing flight between " + arrival_airport + " and " + destination_airport)
        try:
            notamFetch.get_all_notams(arrival_airport, destination_airport)
        except Exception as err:
            self.fail("Airport was not located when it should have been.")

    # Check two far airports in the continental US
    
    def test_far(self) :
        arrival_airport = "PWM"
        destination_airport = "LAX"
        print("Testing flight between " + arrival_airport + " and " + destination_airport)
        try:
            notamFetch.get_all_notams(arrival_airport, destination_airport)
        except Exception as err:
            self.fail("Airport was not located when it should have been.")

    # Check one airport in the continental US and one outside (i.e. Alaska and Hawaii)
            
    def test_alaska(self) :
        arrival_airport = "JNU"
        destination_airport = "OKC"
        print("Testing flight between " + arrival_airport + " and " + destination_airport)
        try:
            notamFetch.get_all_notams(arrival_airport, destination_airport)
        except Exception as err:
            self.fail("Alaska Test Failed: Airport was found.")

    def test_hawaii(self) :
        arrival_airport = "HNL"
        destination_airport = "OKC"
        print("Testing flight between " + arrival_airport + " and " + destination_airport)
        try:
            notamFetch.get_all_notams(arrival_airport, destination_airport)
        except Exception as err:
            self.fail("Alaska Test Failed: Airport was found.")

    # Check one airport in the continental US and one outside (i.e. Canada, Mexico, etc.)
            
    def test_canada(self):
        arrival_airport = "YOW"
        destination_airport = "DCA"
        print("Testing flight between " + arrival_airport + " and " + destination_airport)
        try:
            notamFetch.get_all_notams(arrival_airport, destination_airport)
        except Exception as err:
            self.fail("Alaska Test Failed: Airport was found.") 

    # Check two airports outside the continental US 

    # Check two airports in other countries

    