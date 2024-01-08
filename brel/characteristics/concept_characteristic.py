"""
Contains the class for representing an XBRL concept characteristic

=================

- author: Robin Schmidiger
- version: 0.2
- date: 19 December 2023

=================
"""

from brel import QName

from brel.characteristics import Aspect, ICharacteristic
from brel.reportelements import Concept


class ConceptCharacteristic(ICharacteristic):
    """
    Class for representing a concept characteristic.
    The concept characteristic links the `Aspect.CONCEPT` aspect to a concept.

    """

    __concept_cache: dict[QName, "ConceptCharacteristic"] = {}

    def __init__(self, concept: Concept) -> None:
        """
        Create a ConceptCharacteristic.
        :param concept: the concept of the characteristic
        :returns ConceptCharacteristic: the ConceptCharacteristic
        :raises ValueError: if concept argument is not a Concept instance
        """
        # check if the concept is actually a Concept instance
        if not isinstance(concept, Concept):
            raise ValueError(f"concept is not a Concept instance: {concept}")

        self.__concept: Concept = concept
        self.__concept_cache[concept.get_name()] = self

    def __str__(self) -> str:
        """
        Returns the name of the concept.
        :returns str: the name of the concept
        """
        return self.__concept.get_name().__str__()

    def get_value(self) -> Concept:
        """
        :returns Concept: the concept of the characteristic
        """
        return self.__concept

    def get_aspect(self) -> Aspect:
        """
        :returns Aspect: returns the `Aspect.CONCEPT` aspect
        """
        return Aspect.CONCEPT
