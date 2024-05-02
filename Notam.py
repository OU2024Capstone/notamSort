class Notam:
# Property names as they appear in the FAA API for an easier way to 
# retreive specific properties without having to reference the FAA 
# API for spelling/casing conventions.
    ID="id"
    EFFECTIVE_START = "effectiveStart"
    EFFECTIVE_END = "effectiveEnd"
    TEXT = "text"
    TYPE = "type"
    LOCATION = "location"
    NUMBER = "number"
    SCORE = 0
    ISSUED = "issued"
    SELECTION_CODE = "selectionCode"
    TRAFFIC = "traffic"
    PURPOSE = "purpose"
    SCOPE = "scope"
    CLASSIFICATION = "classification"
    ICAOLOCATION = "icaoLocation"
    COORDINATES = "coordinates"
    RADIUS = "radius"
    
    def __init__(self, raw_notam_data):
        """
        Parameters
        ----------
        raw_notam_data : str
            The raw NOTAM response from the FAA API.
        """
        notam_properties = raw_notam_data.get("properties").get("coreNOTAMData").get("notam")
        self.id = notam_properties.get(Notam.ID)
        self.effective_start = notam_properties.get(Notam.EFFECTIVE_START)
        self.effective_end = notam_properties.get(Notam.EFFECTIVE_END)
        self.text = notam_properties.get(Notam.TEXT)
        self.type = notam_properties.get(Notam.TYPE)
        self.location = notam_properties.get(Notam.LOCATION)
        self.number = notam_properties.get(Notam.NUMBER)
        self.issued = notam_properties.get(Notam.ISSUED)
        self.classification = notam_properties.get(Notam.CLASSIFICATION)
        self.location = notam_properties.get(Notam.LOCATION)
        self.icao_location = notam_properties.get(Notam.ICAOLOCATION)
        self.traffic = notam_properties.get(Notam.TRAFFIC)
        self.purpose = notam_properties.get(Notam.PURPOSE)
        self.scope = notam_properties.get(Notam.SCOPE)
        self.radius = notam_properties.get(Notam.RADIUS)
        self.selection_code = notam_properties.get(Notam.SELECTION_CODE)

    # If two NOTAMs share the same number, they are considered to be the same NOTAM.
    def __eq__(self, other):
        # Only compare other Notam objects
        if not isinstance(other, Notam):
             return False
        return self.id == other.id
    
    # The number attribute is chosen for the hash as it is a unique value.
    def __hash__(self):
            return hash(self.ID)
        
    def __str__(self):
        """Returns a string representing the notam object in the form
            [number] variable : value

        Can easily print a list of notams with print(*notam_list).
        """

        notam_vars = vars(self)
        output=""        
        for item in notam_vars:
            output += f"[{self.number}] {item}: {notam_vars[item]}\n"
        return output
    
    # To print NOTAMs in a list or set.
    def __repr__(self):
        return str(self)