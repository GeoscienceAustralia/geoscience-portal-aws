####Usage

To install library locally for the current user, from the amazonia root directory use:

`make install`

Alternatively, you can use:

`pip install -e . --user`

Note: this will install all of the dependencies for the project. The dependencies list can be found in the setup.py file in the 'Install Requires:' section.

Amazonia expects either a HIERA_PATH environment variable that points to a hiera instance with variables for amazonia/amazonia_resources.py, or a config.yaml file in the root of the amazonia directory with those variables. There is an example of this config.yaml file in the examples folder.

To generate cloud formation using this library, you can use make to refer to any of the existing examples:

`make AutoscalingWebEnv.json`

Alternatively, you can use:

`python ./examples/AutoscalingWebEnv > yourfilenamehere.template`

To use in a downstream project:

```python
from troposphere import Template
from amazonia.amazonia_resources import *
from amazonia.cftemplates import *

template = new Template()
vpc = add_vpc(template, "yourvpccidr")
private_subnet = add_subnet(template, vpc, "yoursubnetname", "yoursubnetcidr")
template.add_resource(...)
template.add_resource(...)
print(template.to_json())
```

Note: amazonia classes (such as cftemplates.dualAZ) extend the troposphere.Template class. This means that any troposphere calls can be made to add resources. The amazonia_resources file contains functions that hope to provide somewhat of a 'shortcut' for users.
