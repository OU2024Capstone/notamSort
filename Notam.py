class Notam:
# Property names as they appear in the FAA API for an easier way to 
# retreive specific properties without having to reference the FAA 
# API for spelling/casing conventions.
    EFFECTIVE_START = "effectiveStart"
    EFFECTIVE_END = "effectiveEnd"
    TEXT = "text"
    TYPE = "type"
    LOCATION = "location"
    NUMBER = "number"
    
    def __init__(self, raw_notam_data):
        """
        Parameters
        ----------
        raw_notam_data : str
            The raw NOTAM response from the FAA API.
        """
        notam_properties = raw_notam_data.get("properties").get("coreNOTAMData").get("notam")

        self.effective_start = notam_properties.get(Notam.EFFECTIVE_START)
        self.effective_end = notam_properties.get(Notam.EFFECTIVE_END)
        self.text = notam_properties.get(Notam.TEXT)
        self.type = notam_properties.get(Notam.TYPE)
        self.location = notam_properties.get(Notam.LOCATION)
        self.number = notam_properties.get(Notam.NUMBER)
            
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