#!/usr/bin/env python

from troposphere import Template
from amazonia.amazonia_resources import *


def main():
    template = Template()

    cd_application = add_cd_application(template, app_name="testapp")

    print(template.to_json(indent=2, separators=(',', ': ')))

if __name__ == "__main__":
    main()
