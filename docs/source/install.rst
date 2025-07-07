Install
=======

**data.all CLI** runs on Linux and macOS operating systems.



Locally
-------

    >>> git clone https://github.com/data-dot-all/dataall-programmatic-tools.git
    >>> cd dataall-programmatic-tools/dataall_cli
    >>> poetry remove dataall-core && poetry add ../dataall_core
    >>> poetry install
    >>> poetry shell


CodeArtifact Private PyPI (pip)
-------------------------------
Follow the **README.md** from the GitLab Repository to set up a CICD Pipeline that publishes **dataall_cli** pacakge to a CodeArtifact Repository.

Then you can install via running the below commands:

    >>> aws codeartifact login --tool pip --repository dataall-package-artifact-repo --domain dataall-package-domain --domain-owner 846588883471 --region eu-west-1
    >>> pip install dataall_cli


[Coming Soon] PyPI (pip)
------------------------

.. note:: Coming Soon...

To install:
    >>> pip install dataall_cli


[Coming Soon] AWS Glue PySpark Jobs
-----------------------------------

.. note:: Coming Soon...


[Coming Soon] Public Artifacts (TBD)
------------------------------------

.. note:: Coming Soon...

[Coming Soon] Amazon SageMaker Notebook
---------------------------------------

.. note:: Coming Soon...


Run this command in any Python 3 notebook cell and then make sure to
**restart the kernel** before importing the **dataall_cli** package.

    >>> !pip install dataall_cli

[Coming Soon] Amazon SageMaker Notebook Lifecycle
-------------------------------------------------

.. note:: Coming Soon...

[Coming Soon] EMR Cluster
-------------------------

.. note:: Coming Soon...

