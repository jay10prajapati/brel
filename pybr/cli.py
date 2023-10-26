"""
CLI interface for pybr project.
"""

import os
from pybr import *
from pybr.examples import *

# import argparser
import sys

def main():  # pragma: no cover
    print("running main")
    print(f"working dir: {os.getcwd()}")

    # parse the arguments

    if "c" in sys.argv:
        # clear the cache
        for file in os.listdir("pybr/dts_cache/"):
            os.remove("pybr/dts_cache/" + file)

    if "1" in sys.argv:
        # execute example 1
        print("[RUNNING EXAMPLE 1]")
        example1()
        print()
    
    if "2" in sys.argv:
        # execute example 2
        print("[RUNNING EXAMPLE 2]")
        example2()
        print()
    
    if "3" in sys.argv:
        # execute example 3
        print("[RUNNING EXAMPLE 3]")
        example3()
        print()
    
    if "4" in sys.argv:
        # execute example 4
        print("[RUNNING EXAMPLE 4]")
        example4()
        print()
    
    if "s" in sys.argv:
        # execute sandbox
        print("[RUNNING SANDBOX]")
        sandbox()
        print()
