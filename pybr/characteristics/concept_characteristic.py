import lxml
import lxml.etree

from ..pybr_label import PyBRLabel
from ..qname import QName

from .pybr_aspect import PyBRAspect
from .i_characteristic import PyBRICharacteristic
from ..reportelements.pybr_concept import PyBRConcept

class PyBRConceptCharacteristic(PyBRICharacteristic):
    """
    Class for representing a concept characteristic.
    This class links a fact to a concept report element.
    """

    __concept_cache: dict[QName, "PyBRConceptCharacteristic"] = {}

    def __init__(self, concept: PyBRConcept) -> None:
        """
        Create a PyBRConceptCharacteristic.
        @param concept: the concept of the characteristic
        @returns PyBRConceptCharacteristic: the PyBRConceptCharacteristic
        @raises ValueError: if concept is not a PyBRConcept instance
        """
        # check if the concept is actually a PyBRConcept instance
        if not isinstance(concept, PyBRConcept):
            raise ValueError(f"concept is not a PyBRConcept instance: {concept}")

        self.__concept : PyBRConcept = concept
        self.__concept_cache[concept.get_name()] = self

    def __str__(self) -> str:
        """
        Returns the name of the concept.
        @returns str: the name of the concept
        """
        return self.__concept.get_name().__str__()
    
    def get_value(self) -> PyBRConcept:
        """
        Returns the concept of the characteristic.
        @returns PyBRConcept: the concept of the characteristic
        """
        return self.__concept
    
    def get_aspect(self) -> PyBRAspect:
        """
        Returns the aspect of the characteristic. This is always PyBRAspect.CONCEPT.
        @returns PyBRAspect: the aspect of the characteristic
        """

        return PyBRAspect.CONCEPT
    
    
