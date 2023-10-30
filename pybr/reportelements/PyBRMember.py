from pybr import QName, PyBRLabel
from pybr.reportelements import IReportElement

class PyBRMember(IReportElement):
    def __init__(self, name: QName, labels: list[PyBRLabel]):
        self.__name = name
        self.__labels = labels 
    
    def get_name(self) -> QName:
        # TODO: write docstring
        return self.__name
    
    def get_labels(self) -> list[PyBRLabel]:
        # TODO: write docstring
        return self.__labels
    
    def add_label(self, label: PyBRLabel):
        # TODO: write docstring
        self.__labels.append(label)
    
    def __str__(self) -> str:
        return self.__name.__str__()