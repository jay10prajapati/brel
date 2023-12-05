import lxml
import lxml.etree
from .characteristics.pybr_aspect import BrelAspect
from .qname import QName
from .characteristics.concept_characteristic import ConceptCharacteristic
from .characteristics.i_characteristic import ICharacteristic
from .characteristics.entity_characteristic import EntityCharacteristic
from .characteristics.period_characteristic import PeriodCharacteristic
from .characteristics.unit_characteristic import UnitCharacteristic
from .characteristics.typed_dimension_characteristic import TypedDimensionCharacteristic
from .characteristics.explicit_dimension_characteristic import ExplicitDimensionCharacteristic
from .reportelements import Dimension, Member, IReportElement
from typing import cast

class Context:
    """
    Class for representing an XBRL context.
    an XBRL context is a collection of aspects.
    There are 5 types of aspects: concept, period, entity, unit and additional dimensions.
    The only required aspect is the concept
    """

    def __init__(self, context_id, aspects: list[BrelAspect]) -> None:
        self.__id : str = context_id

        # aspects are the axis, characteristics are the values per axis
        self.__aspects : list[BrelAspect] = aspects
        self.__characteristics: dict[BrelAspect, ICharacteristic] = {}

        self.__aspects.sort(key=lambda aspect: aspect.get_name())
    
    # First class citizens
    def get_aspects(self) -> list[BrelAspect]:
        """
        Get the aspects of the context.
        """
        return self.__aspects
    
    def get_characteristic(self, aspect: BrelAspect) -> ICharacteristic | None:
        """
        Get the value of an aspect.
        """
        return next((c for a, c in self.__characteristics.items() if a == aspect), None)
    
    # Second class citizens
    def has_characteristic(self, aspect: BrelAspect) -> bool:
        """
        Check if the context has a certain aspect.
        """
        return any(aspect == aspect for aspect in self.__aspects)
    
    # TODO: implement
    def get_characteristic_as_str(self, aspect: BrelAspect) -> str:
        raise NotImplementedError()
    
    def get_characteristic_as_qname(self, aspect: BrelAspect) -> QName:
        raise NotImplementedError()
    
    def get_characteristic_as_int(self, aspect: BrelAspect) -> int:
        raise NotImplementedError()
    
    def get_characteristic_as_float(self, aspect: BrelAspect) -> float:
        raise NotImplementedError()
    
    def get_characteristic_as_bool(self, aspect: BrelAspect) -> bool:
        raise NotImplementedError()
    
    def get_concept(self) -> ConceptCharacteristic:
        """
        Get the concept of the context.
        """
        return cast(ConceptCharacteristic, self.get_characteristic(BrelAspect.CONCEPT))
    
    def get_period(self) -> PeriodCharacteristic | None:
        """
        Get the period of the context.
        """
        return cast(PeriodCharacteristic, self.get_characteristic(BrelAspect.PERIOD))
    
    def get_entity(self) -> EntityCharacteristic | None:
        """
        Get the entity of the context.
        """
        return cast(EntityCharacteristic, self.get_characteristic(BrelAspect.ENTITY))
    
    def get_unit(self) -> UnitCharacteristic | None:
        """
        Get the unit of the context.
        """
        return cast(UnitCharacteristic, self.get_characteristic(BrelAspect.UNIT))

    # Internal methods
    def __add_characteristic(self, characteristic: ICharacteristic) -> None:
        """
        Add an aspect to the context.
        """
        aspect = characteristic.get_aspect()

        if aspect not in self.__aspects:
            self.__aspects.append(aspect)

            self.__characteristics[aspect] = characteristic

            self.__aspects.sort(key=lambda aspect: aspect.get_name())
        else:
            pass
    
    def _get_id(self) -> str:
        """
        Get the id of the context.
        This is an implementation detail of the underlying XBRL library.
        It serves as a good sanity check 
        """
        return self.__id
    
    def __str__(self) -> str:
        output = ""
        for aspect in self.__aspects:
            output += f"{aspect} "
        return output
    
    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Context):
            return False
        
        # TODO: dont use the _id, compare the aspects instead
        return self._get_id() == __value._get_id()
    
    @classmethod
    def from_xml(cls, xml_element: lxml.etree._Element, characteristics: list[UnitCharacteristic | ConceptCharacteristic], report_elements: dict[QName, IReportElement]) -> "Context":
        """
        Creates a Context from an lxml.etree._Element.
        @param xml_element: lxml.etree._Element. The lxml.etree._Element to create the Context from.
        @param report_elements: list[IReportElement]. The report elements to use for the context. If the context contains a dimension, then both the dimension and the member must be in the report elements.
        """

        context_id = xml_element.attrib["id"]

        # check if the supplied list of characteristics only contains units and concepts
        for characteristic in characteristics:
            if not isinstance(characteristic, UnitCharacteristic) and not isinstance(characteristic, ConceptCharacteristic):
                raise ValueError(f"Context id {context_id} contains a characteristic that is not a unit or a concept. Please make sure that the list of characteristics only contains units and concepts.")

        context_period = xml_element.find("{*}period", namespaces=None)
        context_entity = xml_element.find("{*}entity", namespaces=None)

        context = cls(context_id, [])

        # add the characteristics provided by the user. these are the unit and concept
        for characteristic in characteristics:
            context.__add_characteristic(characteristic)

        context.__add_characteristic(PeriodCharacteristic.from_xml(context_period))
        context.__add_characteristic(EntityCharacteristic.from_xml(context_entity))

        # add the dimensions. the dimensions are the children of context/entity/segment
        if context_entity.find("{*}segment") is not None:
            for xml_dimension in context_entity.find("{*}segment").getchildren():
                # if it is an explicit dimension, the tag is xbrli:explicitMember
                if "explicitMember" in xml_dimension.tag: 

                    # get the dimension
                    dimension_axis = QName.from_string(xml_dimension.get("dimension"))
                    dimension = cast(Dimension, report_elements.get(dimension_axis))

                    # get the member
                    dimension_value = QName.from_string(xml_dimension.text)
                    member = cast(Member, report_elements.get(dimension_value)) 

                    # make sure the member and dimension are in the report elements
                    if dimension is None or member is None:
                        print(dimension, member)
                        raise ValueError("Dimension or member not found in report elements. Please make sure that the dimension and member are in the report elements.")
                    
                    # also make sure that they are Dimension and Member instances
                    if not isinstance(dimension, Dimension) or not isinstance(member, Member):
                        print(dimension, member)
                        raise ValueError("Dimension or member not found in report elements. Please make sure that the dimension and member are in the report elements.")
                    
                    # create and add the characteristic
                    dimension_characteristic: ICharacteristic = ExplicitDimensionCharacteristic.from_xml(xml_dimension, dimension, member)
                    context.__add_characteristic(dimension_characteristic)
                # if it is a typed dimension, the tag is xbrli:typedMember
                elif "typedMember" in xml_dimension.tag:

                    # get the dimension
                    dimension_axis = QName.from_string(xml_dimension.get("dimension"))
                    dimension = cast(Dimension, report_elements.get(dimension_axis))

                    # get the value from the xml element
                    # TODO: parse the value as a type instead of just getting the text as a str
                    dimension_value = xml_dimension.getchildren()[0].text

                    # make sure the dimension is in the report elements
                    if dimension is None:
                        raise ValueError("Dimension not found in report elements. Please make sure that the dimension is in the report elements.")
                    
                    # also make sure that it is a Dimension instance
                    if not isinstance(dimension, Dimension):
                        raise ValueError("Dimension not found in report elements. Please make sure that the dimension is in the report elements.")
                    
                    # create and add the characteristic
                    dimension_characteristic: ICharacteristic = TypedDimensionCharacteristic.from_xml(xml_dimension, dimension, dimension_value)
                    context.__add_characteristic(dimension_characteristic)
                else:
                    raise ValueError(f"Unknown dimension type. Please make sure that the dimension is either an explicitMember or a typedMember. {xml_dimension.tag}")
                    raise ValueError("Unknown dimension type. Please make sure that the dimension is either an explicitMember or a typedMember.")
        
        return context
