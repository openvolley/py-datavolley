#!/usr/bin/env python3
"""
Example usage of the datavolley package to extract and parse volleyball match data.
"""

import datavolley as dv


def main():
    return dv.read_dv(dv.example_file())


if __name__ == "__main__":
    data = main()
    print(data[5:14])
