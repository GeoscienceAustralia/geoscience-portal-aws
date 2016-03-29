#!/usr/bin/env python

# pylint: disable=missing-docstring, invalid-name, line-too-long, redefined-outer-name, too-many-arguments

from amazonia.cftemplates import Env


def main():
    template = Env()
    print(template.to_json(indent=2, separators=(',', ': ')))

if __name__ == "__main__":
    main()
