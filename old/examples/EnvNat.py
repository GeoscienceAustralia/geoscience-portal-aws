#!/usr/bin/env python

# pylint: disable=missing-docstring, invalid-name, line-too-long, redefined-outer-name, too-many-arguments

from amazonia.cftemplates import EnvNat
import sys


def main(args):
    keypair = args[0]
    template = EnvNat(keypair)
    print(template.to_json(indent=2, separators=(',', ': ')))

if __name__ == "__main__":
    main(sys.argv[1:])
