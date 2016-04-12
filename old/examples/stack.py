#!/usr/bin/env python

# pylint: disable=missing-docstring, invalid-name, line-too-long, redefined-outer-name, too-many-arguments

from amazonia.templates.stack import Stack


def main():
    template = Stack(keypair_nat="pipeline",keypair_jump="pipeline")
    print(template.to_json(indent=2, separators=(',', ': ')))

if __name__ == "__main__":
    main()
