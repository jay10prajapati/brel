"""
This module contains the XMLFootnoteNetworkFactory class.
XMLFootnoteNetworkFactories are used to create physical FootnoteNetworks from XML.
This module is used by the XML network parser to build physical footnote networks.
At the time of writing, footnote nodes are the only nodes that can point to facts.

====================

- author: Robin Schmidiger
- version: 0.5
- date: 30 January 2024

====================
"""

from typing import cast, Mapping

import lxml
import lxml.etree

from brel import Fact, QName, QNameNSMap
from brel.networks import (
    FootnoteNetwork,
    FootnoteNetworkNode,
    INetwork,
    INetworkNode,
)
from brel.parsers.utils import get_str
from brel.parsers.XML.networks import IXMLNetworkFactory
from brel.reportelements import *
from brel.reportelements import IReportElement
from brel.resource import BrelFootnote, IResource


class FootnoteNetworkFactory(IXMLNetworkFactory):
    def __init__(self, qname_nsmap: QNameNSMap) -> None:
        super().__init__(qname_nsmap)

    def create_network(
        self, xml_link: lxml.etree._Element, roots: list[INetworkNode]
    ) -> INetwork:
        nsmap = self.get_qname_nsmap().get_nsmap()

        link_role = get_str(xml_link, f"{{{nsmap['xlink']}}}role")
        link_qname = QName.from_string(xml_link.tag, self.get_qname_nsmap())

        if not all(isinstance(root, FootnoteNetworkNode) for root in roots):
            raise TypeError("roots must all be of type FootnoteNetworkNode")

        if len(roots) == 0:
            raise ValueError("roots must not be empty")

        roots_cast = cast(list[FootnoteNetworkNode], roots)

        return FootnoteNetwork(roots_cast, link_role, link_qname, self.is_physical())

    def create_node(
        self,
        xml_link: lxml.etree._Element,
        xml_referenced_element: lxml.etree._Element,
        xml_arc: lxml.etree._Element | None,
        points_to: IReportElement | IResource | Fact,
    ) -> INetworkNode:
        nsmap = self.get_qname_nsmap().get_nsmap()

        label = get_str(xml_referenced_element, f"{{{nsmap['xlink']}}}label")

        if xml_arc is None:
            # the node is not connected to any other node
            arc_role: str = "unknown"
            order = 1.0
            arc_qname = QName.from_string("link:unknown", self.get_qname_nsmap())
        elif xml_arc.get(f"{{{nsmap['xlink']}}}from", None) == label:
            # the node is a root
            arc_role = get_str(xml_arc, f"{{{nsmap['xlink']}}}arcrole")
            order = 1.0
            arc_qname = QName.from_string(xml_arc.tag, self.get_qname_nsmap())
        elif xml_arc.get(f"{{{nsmap['xlink']}}}to", None) == label:
            # the node is an inner node
            arc_role = get_str(xml_arc, f"{{{nsmap['xlink']}}}arcrole")
            order = float(xml_arc.attrib.get("order") or 1)
            arc_qname = QName.from_string(xml_arc.tag, self.get_qname_nsmap())
        else:
            raise ValueError(
                f"referenced element {xml_referenced_element} is not connected to arc {xml_arc}"
            )

        link_role = get_str(xml_link, f"{{{nsmap['xlink']}}}role")
        link_name = QName.from_string(xml_link.tag, self.get_qname_nsmap())

        if isinstance(points_to, IResource) and not isinstance(points_to, BrelFootnote):
            raise ValueError(
                f"points_to must be of type BreelFootnote, not {type(points_to)}"
            )

        return FootnoteNetworkNode(
            points_to, [], arc_role, arc_qname, link_role, link_name, order
        )

    def update_report_elements(
        self, report_elements: Mapping[QName, IReportElement], network: INetwork
    ):
        pass

    def is_physical(self) -> bool:
        return True
