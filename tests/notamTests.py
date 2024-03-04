import unittest
import notamFetch

class TestNotams(unittest.TestCase) :

    ## Tests involving user input:

    # Test valid inputs in the frontend

    # Test invalid inputs in the frontend

    ## Tests involving valid airports:

    # Check two close airports in the continental US

    def test_close(self) :
        try:
            notamFetch.get_all_notams("MCI", "OKC")
        except Exception as err:
            self.fail("Airport was not located when it should have been.")

    # Check two far airports in the continental US
    
    def test_far(self) :
        try:
            notamFetch.get_all_notams("PWM", "LAX")
        except Exception as err:
            self.fail("Airport was not located when it should have been.")

    # Check one airport in the continental US and one outside (i.e. Alaska and Hawaii)

    # Check one airport in the continental US and one outside (i.e. Canada, Mexico, etc.)

    # Check two airports outside the continental US 

    # Check two airports in other countries

    