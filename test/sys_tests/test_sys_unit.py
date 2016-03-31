#!/usr/bin/python3

from amazonia.classes.unit import Unit


def main():
    unit = Unit()
    print(unit.stack.to_json(indent=2, separators=(',', ': ')))


if __name__ == '__main__':
    main()
