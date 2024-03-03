from abc import ABC, abstractmethod

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
