import unittest
import notamFetch
from NavigationTools import PointObject

# Run unit tests by running `python3 -m unittest tests/api_http_errors.py`

# Making a note here that it's not really a great idea to have unit tests that
# test a live API. Not only could it be swingy and give false positives when
# the API is down, but it's additional load on FAA servers that's likely
# unwanted. The better way would be to mock up requests.get() to return HTTP
# codes and mocked responses.

class TestHttpResponseStatusCodes( unittest.TestCase ):

    COORDINATES = PointObject(35, -95)

    def test_authorized( self ):
        try:
            notamFetch.get_notams_at( self.COORDINATES )
        except Exception as err:
            self.fail( "An exception was raised when it shouldn't have" )
        pass

    def test_unauthorized( self ):
        good_credentials = notamFetch.credentials
        with self.assertRaises( RuntimeError ) as context:
            notamFetch.credentials = { "client_id": "bad_id", "client_secret": "bad_secret" }
            notamFetch.get_notams_at( self.COORDINATES )

        self.assertTrue( "HTTP 401" in str(context.exception), f"Expected a 401 exception but got {str(context.exception)} instead" )
        notamFetch.credentials = good_credentials

    def test_bad_request( self ):
        with self.assertRaises( RuntimeError ) as context:
            notamFetch.get_notams_at( self.COORDINATES, additional_params={"pageSize":999999} )

        self.assertTrue( "Received error message" in str(context.exception), f"Expected an error message but got {str(context.exception)} instead" )

    def test_not_found( self ):
        good_url = notamFetch.faa_api
        with self.assertRaises( RuntimeError ) as context:
            notamFetch.faa_api = f"{good_url}_OBVIOUSLY_BAD_URL"
            notamFetch.get_notams_at( self.COORDINATES )

        self.assertTrue( "HTTP 404" in str(context.exception), f"Expected a 404 exception but got {str(context.exception)} instead" )
        notamFetch.faa_api = good_url
