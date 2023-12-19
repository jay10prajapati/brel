"""
This module contains the XML namespace normalizer.
In XML, namespaces can be defined per element. Therefore, the same prefix can map to different urls and the same url can map to different prefixes.
It all depends on the context in which the prefix is used. From a user perspective, this is very confusing. 
When a user looks for e.g. us-gaap:Assets, he usually doesn't care if it is us-gaap's 2022 or 2023 version. 
Also, if the filing calls the prefix us-gaap1 instead of us-gaap for some contexts, then the user will have to know this and use the correct prefix.

Namespace normalizing turns the nested namespace mappings into a flat namespace mapping. It also generates redirects for the prefixes.
For the example before, it would generate the following mapping:

us-gaap -> us-gaap-2023-01-31
redirect: us-gaap1 -> us-gaap

More precisely, it does the following:
- It groups the prefix->url mappings by their unversioned url.
- For each group, it picks the main prefix and the latest version of the url.
- For each non-main prefix, it generates a redirect to the main prefix.

@author: Robin Schmidiger
@version: 0.0.2
@date: 2023-12-06
"""

from collections import defaultdict
import itertools
import re
import json

DEBUG = False

# Load the namespace config
# TODO: make this configurable
nsconfig_path = "brel/config/nsconfig.json"

default_namespace_mappings: dict[str, str] = {}

with open(nsconfig_path, "r") as nsconfig_file:
    nsconfig = json.load(nsconfig_file)
    for prefix, re_uri in nsconfig["default_mappings"].items():
        default_namespace_mappings[re_uri] = prefix

# helper functions
def get_default_prefix_from_uri(uri: str) -> str | None:
    """
    Get the default prefix for a URI.
    :param uri: The URI to get the prefix for.
    :return: The prefix.
    """
    longest_match_url = ""
    longest_match_prefix = ""

    for uri_regex, prefix in default_namespace_mappings.items():

        if re.match(uri_regex, uri):
            # return prefix
            if len(uri_regex) > len(longest_match_url):
                longest_match_url = uri_regex
                longest_match_prefix = prefix

    if longest_match_url != "":
        if DEBUG:  # pragma: no cover
            print(f"Found default prefix {longest_match_prefix} for uri {longest_match_url}")
        return longest_match_prefix
    else:
        return None

def generate_alternative_prefixes(prefix: str) -> str:
    """
    Generate alternative prefixes for a prefix.
    :param prefix: The prefix to generate an alternative prefix for
    :return: A str containing the alternative prefix
    """
    # TODO: make this more robust
    # get the number at the end of the prefix
    prefix_numbers = re.findall(r"\d+$", prefix)
    # if there is a number, increment it. else, set it to 1
    if len(prefix_numbers) > 0:
        prefix_number = int(prefix_numbers[0]) + 1
    else:
        prefix_number = 1
    
    # get the prefix without the number
    prefix = re.sub(r"\d+$", "", prefix)
    return prefix + str(prefix_number)

def url_remove_version(url: str) -> str:
    """
    Remove the version from a url.
    :param url: The url to remove the version from.
    :return: The url without the version.
    """
    # strip all numbers and - and _ and dots from the url
    return re.sub(r"[\d\-\_\.]", "", url)

def are_urls_versions(urls: list[str]) -> bool:
    """
    Check if a list of urls are compatible.
    :param urls: A list of urls.
    :return: True if the urls are versions of each other, False otherwise.
    """
    if DEBUG:  # pragma: no cover
        print(f"Checking if urls {urls} are versions of each other.")
    
    # Trivial case. If there is only one url, then it is a version of itself. 
    # If there are no urls, then there are no versions.
    if len(urls) < 2:
        return True
    
    # compare all adjacent urls
    for i in range(len(urls) - 1):
        url1 = url_remove_version(urls[i])
        url2 = url_remove_version(urls[i + 1])

        if url1 != url2:
            if DEBUG:  # pragma: no cover
                print(f"Found incompatible urls {url1} and {url2} at positions {i} and {i+1}.")
            return False
    
    if DEBUG:  # pragma: no cover
        print(f"All urls are versions of each other.")

    return True

def get_latest_url_version(urls: list[str]) -> str:
    """
    Get the latest version of a list of urls.
    :param urls: A list of urls.
    :return: The latest version of the urls.
    """
    def url_to_value(url:str) -> int:
        """
        Convert a url to a value.
        :param url: The url to convert.
        :return: The value.
        """
        # get all numbers in the url
        numbers = re.findall(r"\d+", url)
        # add them up
        return sum([int(number) for number in numbers])
    
    # return the url with the max value
    latest_url = max(urls, key=url_to_value)

    if DEBUG:  # pragma: no cover
        print(f"Found latest url {latest_url} from urls {urls}.")

    return latest_url

def get_best_prefix(prefixes: list[str]) -> str:
    """
    Get the best prefix from a list of prefixes.
    :param prefixes: A list of prefixes.
    :return: The best prefix.
    """
    def prefix_to_value(prefix:str) -> int:
        """
        Convert a prefix to a value.
        :param prefix: The prefix to convert.
        :return: The value.
        """
        return len(prefix)
    
    best_prefix = min(prefixes, key=prefix_to_value)

    if DEBUG:  # pragma: no cover
        print(f"Found best prefix {best_prefix} from prefixes {prefixes}.")
    
    return best_prefix

def component_to_nsmap(urls: list[str], prefixes: list[str]) -> tuple[str, str, list[str]]:
    """
    Extract the namespace mappings from a component.
    :param urls: A list of the urls in the component.
    :param prefixes: A list of the prefixes in the component.
    :return: A tuple containing the prefix, the url and the prefixes to be redirected.
    """

    if DEBUG:  # pragma: no cover
        print(f"Extracting namespace mappings from component with urls {urls} and prefixes {prefixes}.")
    
    if len(urls) < 1 or len(prefixes) < 1:
        raise ValueError(f"The component is too simple. It does not contain enough urls or prefixes: {urls+prefixes}")

    # get the main url
    if not are_urls_versions(urls):
        raise ValueError(f"The namespace mapping is too complex. The prefix {prefixes[0]} maps to multiple urls: {urls}")
    
    main_url = get_latest_url_version(urls)

    # get the main prefix
    default_prefix = get_default_prefix_from_uri(main_url)

    if default_prefix is not None and default_prefix in prefixes:
        main_prefix = default_prefix
    elif default_prefix is not None and default_prefix not in prefixes:
        main_prefix = default_prefix
        print(f"Warning: the default prefix {default_prefix} is not in the prefixes list {prefixes}")
    else:
        main_prefix = get_best_prefix(prefixes)
    
    # get the redirects
    redirects = []
    for prefix in prefixes:
        if prefix != main_prefix:
            redirects.append(prefix)
    
    if DEBUG:  # pragma: no cover
        print(f"Extracted namespace mappings: {main_prefix} -> {main_url} with redirects {redirects}")
    
    return main_prefix, main_url, redirects

def normalize_nsmap(namespace_mappings: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    """
    Normalize the namespace mappings.
    A normalized namespace mapping is a mapping where each prefix maps to a single url. 
    If a prefix maps to multiple versions of an url, then the latest version is chosen.
    If multiple prefixes map to the same url, then a main prefix is chosen, which tends to be the shortest prefix.
    The other prefixes are redirected to the main prefix.
    :param namespace_mappings: A list of namespace mappings.
    :return: A tuple containing the normalized namespace mapping and the redirects.
    the namespacemap maps prefix -> uri
    the redirects map prefix -> prefix
    """
    # compute all components by grouping the urls by their unversioned uri
    components: dict[str, tuple[set[str], set[str]]] = defaultdict(lambda: (set(), set()))
    for namespace_mapping in namespace_mappings:
        for prefix, uri in namespace_mapping.items():
            if prefix is not None:
                unversioned_uri = url_remove_version(uri)
                components[unversioned_uri][0].add(uri)
                components[unversioned_uri][1].add(prefix)

    if DEBUG:  # pragma: no cover
        print(f"Found components:")
        for uri_a_unversioned, (uris_a, prefixes_a) in components.items():
            print(f"{uri_a_unversioned} -> {uris_a} with prefixes {prefixes_a}")

    nsmap: dict[str, str] = {}
    redirects: dict[str, str] = {}
    renames: dict[str, str] = {}
    
    # for each connected component, pick the main prefix and the main url
    # raise an error if the connected component is too complex
    for connected_component in components.values():
        urls = list(connected_component[0])
        prefixes = list(connected_component[1])
        component_prefix, component_url, component_redirects = component_to_nsmap(urls, prefixes)

        # check if the component prefix is already in the nsmap
        # if so, create an alternative prefix
        if component_prefix in nsmap:
            new_component_prefix = generate_alternative_prefixes(component_prefix)
            renames[new_component_prefix] = component_prefix
            component_prefix = new_component_prefix        

        # add the component to the nsmap and the redirects
        nsmap[component_prefix] = component_url
        for redirect in component_redirects:
            redirects[redirect] = component_prefix
    
    if DEBUG:  # pragma: no cover
        print(f"Normalized namespace mappings: {nsmap} with redirects {redirects}")

    return {
        "nsmap": nsmap,
        "redirects": redirects,
        "renames": renames
    }