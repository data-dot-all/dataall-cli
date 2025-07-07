
.. image:: ./_static/logo.png
   :alt: Data.all Logo
   :align: center
   :scale: 30%

An `AWS Professional Service <https://aws.amazon.com/professional-services>`_ open source initiative | aws-proserve-opensource@amazon.com

AWS data.all CLI is a command-line interface (CLI) tool for data.all which aims to provide users with a seamless and efficient means of interfacing with data.all programmatically. Users can leverage the  data.all CLI to enhance automation, develop scripting, and integrate data.all APIs into their existing workflows. The CLI tool encompasses a comprehensive set of commands and functions, enabling users to perform operations related to data.all features such as datasets, dataset share, environment, organization and consumption role through programmatic interfaces. The data.all CLI tool empowers developers and administrators to leverage data.all functionalities in a programmatic manner.

Quick Start
-----------

To install data.all CLI, check out the **Install** Page of the documentation.

To get a list of supported commands can use the `--help` parameter:
    >>> dataall_cli --help # Get list of supported commands

To configure a new data.all user (i.e. `profile`) run the `configure` command:
    >>> dataall_cli configure # Configure new profile

To learn more about supported arguments for a operation use the `--help` parameter:
    >>> dataall_cli list_organizations --help # Get list of supported input arguments

To run a CLI command specifying a profile, pass the `--profile` parameter as such:
    >>> dataall_cli list_organizations --profile PROFILE # Run list_organizations command


Read The Docs
-------------

.. toctree::
   :maxdepth: 2

   about
   install
   tutorials
   Community Resources <https://data-dot-all.github.io/dataall/deploy-aws/>
   Logging <https://data-dot-all.github.io/dataall/deploy-aws/>
   License <https://github.com/awslabs/aiops-modules/blob/main/LICENSE>
   Contributing <https://github.com/awslabs/aiops-modules/blob/main/CONTRIBUTING.md>


Dataall CLI
-------------

.. toctree::
   :maxdepth: 2

   cli
