from pybr import PyBRLabel, QName
from pybr.reportelements import IReportElement

class PyBRDimension(IReportElement):
    def __init__(self, name: QName, labels: list[PyBRLabel]) -> None:
        self.__name = name
        self.__labels = labels
        self.__is_explicit = True
        self.__type: QName | None = None
    
    def get_name(self) -> QName:
        """
        Get the name of the dimension.
        @return: QName containing the name of the dimension
        """
        return self.__name
    
    def get_labels(self) -> list[PyBRLabel]:
        """
        Get the labels of the dimension.
        @return: list[PyBRLabel] containing the labels of the dimension
        """        
        return self.__labels
    
    def add_label(self, label: PyBRLabel):
        """
        Add a label to the dimension.
        @param label: the label to add to the dimension
        """
        self.__labels.append(label)
    
    def is_explicit(self) -> bool:
        """
        Check if the dimension is explicit.
        @return: True 'IFF' the dimension is explicit, False otherwise
        """
        return self.__is_explicit
    
    def get_type(self):
        """
        Get the type of the dimension.
        @return: type of the dimension
        """
        if self.__is_explicit:
            raise Exception("Cannot get type of explicit dimension")
        
        return self.__type
    
    def make_typed(self, dim_type: QName):
        self.__is_explicit = False
        self.__type = dim_type
    
    def __str__(self) -> str:
        return self.__name.__str__()
