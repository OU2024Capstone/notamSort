from abc import ABC, abstractmethod
from datetime import datetime
import json

class SortStategyInterface(ABC):

    @abstractmethod
    def sort(self, notam_list):
        pass

# Implemented SimpleSort on alphabetical text attribute to indicate
# how a sorting algorithm can utilize the interface implemented above
class SimpleSort(SortStategyInterface):

    def sort(self, notam_list):
        notam_list.sort(key=lambda x: x.text)

        return notam_list
    
class RatingSort(SortStategyInterface):

    def sort(self, notam_list, departure, arrival):
        self.scoring(notam_list, departure, arrival)
        notam_list.sort(key=lambda x: x.score, reverse=True)

        return notam_list
    
    def is_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    # Designate scores to the given notams for later sorting
    def scoring(self, notam_list, departure, arrival):
        today = datetime.utcnow()

        # load in reference json files
        classification = json.load(open('./ranking/Classification.json'))
        traffic = json.load(open('./ranking/Traffic.json'))
        purpose = json.load(open('./ranking/Purpose.json'))
        scope = json.load(open('./ranking/Scope.json'))
        selection_code23 = json.load(open('./ranking/Selection_Code_23.json'))
        selection_code45 = json.load(open('./ranking/Selection_Code_45.json'))

        for notam in notam_list:
            score = 0

            if notam.type != None:
                type = json.load(open('./ranking/Type.json'))
                try:
                    score += type['MaxValue'] / type['dataScores'].get(notam.type, 0)
                except (ZeroDivisionError, KeyError):
                    score += type['MinValue']

            # scoring based on days since date issued
            given_date = datetime.strptime(notam.issued, "%Y-%m-%dT%H:%M:%S.%fZ")
            difference = given_date - today
            difference_in_days = abs(difference.days)
            try:
                score += 10 / difference_in_days
            except (ZeroDivisionError):
                # provide a score higher in the case current date is exactly issued date
                score += 11

            if notam.classification != None:
                try:
                    score += classification['MaxValue'] / classification['dataScores'].get(notam.classification, 0)
                except (ZeroDivisionError, KeyError):
                    score += classification['MinValue']

            # large score boost for arrival and departure related notams
            if notam.location == departure or notam.icao_location == departure:
                score += 20000
            elif notam.location == arrival or notam.icao_location == arrival:
                score += 10000

            if notam.traffic != None:
                # parse through multiple character property
                for char in str(notam.traffic):
                    try:
                        score += traffic['MaxValue'] / traffic['dataScores'].get(char, 0)
                    except (ZeroDivisionError, KeyError):
                        score += traffic['MinValue']

            if notam.purpose != None:
                if notam.purpose == "SCHEDULED":
                    score += purpose['MaxValue'] / purpose['dataScores'].get('SCHEDULED')
                else:
                    # parse through multiple character property
                    for char in str(notam.purpose):
                        try:
                            score += purpose['MaxValue'] / purpose['dataScores'].get(char, 0)
                        except (ZeroDivisionError, KeyError):
                            score += purpose['MinValue']

            if notam.scope != None:
                # parse through multiple character property
                for char in str(notam.scope):
                    try:
                        score += scope['MaxValue'] / scope['dataScores'].get(char, 0)
                    except (ZeroDivisionError, KeyError):
                        score += scope['MinValue']

            if notam.radius != None and self.is_float(notam.radius):
                score += float(notam.radius)
            elif "IC" in str(notam.radius):
                score += 200

            # Selection codes are determined by pairs of characters
            # Characters 2 and 3 can determine subject being reported
            # Characters 4 and 5 determine status of the given subject
            # Each pair combination has been given ranks based on Selection_Code related json
            if notam.selection_code != None:
                # characters 2 and 3
                
                char2 = notam.selection_code[1]
                char3 = notam.selection_code[2]

                try:
                    category_rank = selection_code23['SubCategories'][char2].get('categoryRank', 0)
                    subsub_category = selection_code23['SubCategories'][char2].get(char3, 0)

                    score += selection_code23['MinValue'] + ( selection_code23['MaxValue']- selection_code23['MinValue'] ) * (1 / category_rank) * (1 / subsub_category)
                except (ZeroDivisionError, KeyError):
                    score += selection_code23['MinValue']

                # characters 4 and 5
                char4 = notam.selection_code[3]
                char5 = notam.selection_code[4]

                try:
                    category_rank = selection_code45['SubCategories'][char4].get('categoryRank', 0)
                    subsub_category = selection_code45['SubCategories'][char4].get(char5, 0)

                    score += selection_code45['MinValue'] + ( selection_code45['MaxValue']- selection_code45['MinValue'] ) * (1 / category_rank) * (1 / subsub_category)
                except (ZeroDivisionError, KeyError):
                    score += selection_code45['MinValue']

            notam.score = score
            # print(notam.score)
