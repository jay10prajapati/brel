"""
This module parses multiple etrees into a dict of networks.

=================

- author: Robin Schmidiger
- version: 0.18
- date: 31 January 2024

=================
"""


import json
import os
import re
from collections import defaultdict
import time
from importlib.resources import path
from typing import Any, cast, Callable, Mapping, Tuple, Iterable

import lxml.etree

from brel import QName, QNameNSMap
from brel.networks import *
from brel.parsers.XML.networks import parse_xml_link
from brel.parsers.utils import get_str
from brel.reportelements import *
from brel.resource import *

from brel.parsers.utils import combine_networks

# CONFIG_PATH = "brel/config/linkconfig.json"

DEBUG = False


with path("brel.config", "linkconfig.json") as config_path:
    with open(config_path, "r") as f:
        LINK_CONFIG = json.load(f)
        STANDARD_LINK_NAMES: list[str] = LINK_CONFIG["standard_link_names"]
        STANDARD_RESOURCE_ROLES: list[str] = LINK_CONFIG["standard_resource_roles"]
        STANDARD_LINK_ROLES: list[str] = LINK_CONFIG["standard_link_roles"]


def parse_networks_from_xmls(
    xml_trees: Iterable[lxml.etree._ElementTree],
    qname_nsmap: QNameNSMap,
    id_to_any: Mapping[str, Any],
    report_elements: Mapping[QName, IReportElement],
) -> Mapping[str, list[INetwork]]:
    nsmap = qname_nsmap.get_nsmap()

    # first, we want to get all extended links in all xml trees
    # we do this by going over all xml trees and getting all extended links
    if DEBUG:  # pragma: no cover
        start_time = time.time()

    links = []
    for xml_tree in xml_trees:
        all_links = xml_tree.findall(
            ".//link:*[@xlink:type='extended']", namespaces=nsmap
        )
        links.extend(all_links)

    if DEBUG:  # pragma: no cover
        end_time = time.time()
        print(
            f"Found {len(links)} extended links in {end_time - start_time:.2f} seconds"
        )
        start_time = time.time()

    # then we want to parse the extended links with the default role first.
    # This is because some extended links may rely on labels that are defined in other extended links.
    # Specifically, the presentation networks rely on labels that are defined in the label networks.
    # Label networks have the default link role.
    def is_standard_role(role: str) -> bool:
        return any(standard_role in role for standard_role in STANDARD_LINK_ROLES)

    links.sort(
        key=lambda link: is_standard_role(link.get("{" + nsmap["xlink"] + "}role", "")),
        reverse=True,
    )

    networks: dict[str, list[INetwork]] = defaultdict(list)

    if DEBUG:  # pragma: no cover
        end_time = time.time()
        print(f"Sorted the extended links in {end_time - start_time:.2f} seconds")

    # go over all extended links in all xml trees
    for xml_link in links:
        if DEBUG:  # pragma: no cover
            start_time = time.time()

        # get the link role
        link_role = get_str(xml_link, f"{{{nsmap['xlink']}}}role")

        # get the link name
        link_name = xml_link.tag
        if not isinstance(link_name, str):
            raise ValueError(
                f"the link element {xml_link} has an invalid tag name '{link_name}'. The tag name must be a string."
            )

        # According to the XBRL Generic Links spec, if the xlink:role is not the default link role,
        # then the ancestor linkbase must have a roleRef with the roleURI equal to the xlink:role.
        # this roleRef's href must point to a role definition that has a usedOn attribute that contains the link element's name.
        # rolerefs are only required for standard links and standard resources.
        # http://www.xbrl.org/specification/xbrl-2.1/rec-2003-12-31/xbrl-2.1-rec-2003-12-31+corrected-errata-2013-02-20.html#_3.5.2.4

        # check the integrity of all xlink:role attributes
        # If the xlink:role is NOT a standard link role and NOT a standard resource role,
        # And if the link name is a standard link name,
        # Then the ancestor linkbase needs to have a roleRef with the roleURI equal to the xlink:role.

        link_role_elems = xml_link.findall(".//*[@xlink:role]", namespaces=nsmap) + [
            xml_link
        ]

        if DEBUG:  # pragma: no cover
            print(f"The link has {len(link_role_elems)} elements")
        for link_role_elem in link_role_elems:
            role = link_role_elem.get(f"{{{nsmap['xlink']}}}role", None)
            if role is None:
                raise ValueError(
                    f"the element {link_role_elem} does not have a xlink:role attribute"
                )
            if not isinstance(role, str):
                raise ValueError(
                    f"the element {link_role_elem} has an invalid xlink:role attribute '{role}'. The xlink:role attribute must be a string."
                )

            role = cast(str, role)

            # check if the role is a standard role
            if any(standard_role in role for standard_role in STANDARD_LINK_ROLES):
                continue

            # check if the role is a standard resource role
            if any(standard_role in role for standard_role in STANDARD_RESOURCE_ROLES):
                continue

            # check if the link name is a standard link name
            if any(
                standard_link_name in link_name
                for standard_link_name in STANDARD_LINK_NAMES
            ):
                # first, get the parent linkbase
                linkbase: lxml.etree._Element | None = xml_link.getparent()
                while (
                    linkbase is not None
                    and linkbase.tag != f"{{{nsmap['link']}}}linkbase"
                ):
                    linkbase = linkbase.getparent()

                if linkbase is None:
                    raise ValueError(
                        f"the element {link_role_elem} does not have a parent linkbase. All elements with an xlink:role must be in a linkbase."
                    )

                # find the roleRef in the linkbase
                role_ref = linkbase.find(
                    f".//link:roleRef[@roleURI='{role}']", namespaces=nsmap
                )

                if role_ref is None:
                    raise ValueError(
                        f"the linkbase {linkbase} does not have a roleRef with the roleURI '{role}'. All roleRefs must have a roleURI attribute."
                    )

                # read the component name from the xlink:href of the roleRef
                href = role_ref.get(f"{{{nsmap['xlink']}}}href", None)
                if href is None:
                    raise ValueError(
                        f"the roleRef {role_ref} does not have a href attribute. All roleRefs must have a href attribute."
                    )

        # parse the network and update the report elements
        link_networks = parse_xml_link(
            xml_link, qname_nsmap, id_to_any, report_elements
        )

        if DEBUG:  # pragma: no cover
            end_time = time.time()

            print(
                f"parsed the link element {xml_link.tag} {link_role} in {end_time - start_time:.2f} seconds"
            )

        # add the presentation network to the networks dict
        networks[link_role].extend(link_networks)

    # Do a second pass over all networks and combine all non-physical networks of the same type into a single network
    combined_networks: dict[str, list[INetwork]] = defaultdict(list)
    for role, network_list in networks.items():
        # separate them by type
        networks_by_type: dict[type, list[INetwork]] = defaultdict(list)

        combined_network_list: list[INetwork] = []
        for network in network_list:
            if network.is_physical():
                combined_network_list.append(network)
            else:
                networks_by_type[type(network)].append(network)

        for network_type_list in networks_by_type.values():
            combined_network_list.append(combine_networks(network_type_list))

        combined_networks[role] = combined_network_list

    return combined_networks
