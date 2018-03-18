Welcome to Xtesting's documentation!
====================================

Xtesting have leveraged on Functest efforts to provide a reference testing
framework:

  * `Requirements Management
    <https://wiki.opnfv.org/display/functest/Requirements+management>`_
  * `Docker Slicing <http://testresults.opnfv.org/functest/dockerslicing/>`_
  * `Functest Framework <http://testresults.opnfv.org/functest/framework/>`_

Xtesting aims at allowing a smooth integration of new Functest Kubernetes
testcases.

But, more generally, it eases building any CI/CD toolchain for other
domains than testing Virtualized Infrastructure Managers (VIM) such as
`OpenStack <https://www.openstack.org/>`_.

It now offers a possible reuse of our framework in other OpenSource projects
such as ONAP: `integration_demo_E2E_chain.pdf`_

.. _`integration_demo_E2E_chain.pdf`: https://wiki.onap.org/pages/viewpage.action?pageId=6593670&preview=%2F6593670%2F25433913%2Fintegration_demo_E2E_chain.pdf

Technical guidelines
--------------------

* to support both python2 and python3
* to be fully covered by unit tests
* to be well rated by pylint (only local exceptions are accepted on purpose)
* to be released as a  `python package`_ and then to be unlinked to OPNFV
  Milestones
* to provide `Docker containers`_ and manifests for both architectures
  supported by OPNFV: amd64 and arm64
* to publish the API documentation online

.. _`python package`: https://pypi.python.org/pypi/xtesting/
.. _`Docker containers`: https://hub.docker.com/r/opnfv/xtesting/

Try it!
-------

* run xtesting container::

  $ sudo docker run opnfv/xtesting

* run xtesting via package (python2)::

  $ virtualenv xtesting-py2
  $ . xtesting-py2/bin/activate
  $ pip install xtesting
  $ sudo xtesting-py2/bin/run_tests -t all
  $ deactivate

* run xtesting via package (python3)::

  $ virtualenv xtesting-py3 -p python3
  $ . xtesting-py3/bin/activate
  $ pip install xtesting
  $ sudo xtesting-py3/bin/run_tests -t all
  $ deactivate

Contents:
---------

.. toctree::
   :maxdepth: 2

   apidoc/modules


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
