# Xtesting

[Cédric Ollivier](mailto:cedric.ollivier@orange.com)

2018/03/23



## Why Xtesting?


### Functest framework

- handle all interactions with OPNFV CI/CD components (entry points,
results publication, status codes, etc.)
- ease the development of third-party testcases by offering multiple drivers:
Python, Bash, unittest, Robot Framework and VNF.

**It has worked very well for E-release, but updates were required for
the next ones**


### Internal needs

- Functest has to verify Kubernetes deployment but
[its former framework](http://testresults.opnfv.org/functest/framework/) was
linked to OpenStack (e.g. credentials sourcing, rally verifiers, etc.)
- hosting both OpenStack and Kubernetes in the same Python package would
increase dependencies and then complexify
[container slicing](http://testresults.opnfv.org/functest/dockerslicing/)

**Why not refactoring the first Functest framework?**


### External needs

- Functest Python and containers framework could be very useful out of OPNFV
(ease developing testcases, manage requirements and offer lightweight Docker
images)
- a new Functest design could simplify test integration in a complete
[OPNFV-based CI/CD toolchain](http://docs.opnfv.org/en/stable-euphrates/testing/ecosystem/overview.html)
(e.g. Testing Containers, Test API and dashboard)

**Let the developer only work on the test suites without diving into CI/CD
integration**



## What's been done for Fraser?


### Xtesting framework

- Functest framework were moved to a new xtesting repository
(functest only hosts OpenStack testcases)
- it has been updated and improved to follow all Xtesting technical
guidelines:
  - unlink to **OpenStack** and **OPNFV**
  - support both Python2 and Python3 (required by **Functional Gating**)
  - be fully covered by unit tests and well rated by pylint (10/10)


### Xtesting deliverables

- Xtesting is released as [a Python package](https://pypi.python.org/pypi/xtesting/)
and then is unlinked to OPNFV Milestones (Functest Python package now depends
on it)
- [opnfv/xtesting](https://hub.docker.com/r/opnfv/xtesting/) is proposed to
build third-parties containers (both amd64 and arm64 architectures).
- the API documentation is automatically built
[online](http://xtesting.readthedocs.io/en/latest/apidoc/xtesting.html)



## Functest & Xtesting in Orange ONAP OpenLab


### first verify the infrastructure via Functest

```
+----------------------------+------------------+---------------------+------------------+----------------+
|         TEST CASE          |     PROJECT      |         TIER        |     DURATION     |     RESULT     |
+----------------------------+------------------+---------------------+------------------+----------------+
|      connection_check      |     functest     |     healthcheck     |      00:07       |      PASS      |
|         api_check          |     functest     |     healthcheck     |      07:46       |      PASS      |
|     snaps_health_check     |     functest     |     healthcheck     |      00:36       |      PASS      |
+----------------------------+------------------+---------------------+------------------+----------------+
```
<!-- .element: style="font-size: 0.34em" -->


```
+------------------------------+------------------+---------------+------------------+----------------+
|          TEST CASE           |     PROJECT      |      TIER     |     DURATION     |     RESULT     |
+------------------------------+------------------+---------------+------------------+----------------+
|          vping_ssh           |     functest     |     smoke     |      00:57       |      PASS      |
|        vping_userdata        |     functest     |     smoke     |      00:33       |      PASS      |
|     tempest_smoke_serial     |     functest     |     smoke     |      13:22       |      PASS      |
|         rally_sanity         |     functest     |     smoke     |      24:07       |      PASS      |
|       refstack_defcore       |     functest     |     smoke     |      05:21       |      PASS      |
|           patrole            |     functest     |     smoke     |      04:29       |      PASS      |
|         snaps_smoke          |     functest     |     smoke     |      46:54       |      PASS      |
|             odl              |     functest     |     smoke     |      00:00       |      SKIP      |
|         odl_netvirt          |     functest     |     smoke     |      00:00       |      SKIP      |
|        neutron_trunk         |     functest     |     smoke     |      00:00       |      SKIP      |
+------------------------------+------------------+---------------+------------------+----------------+
```
<!-- .element: style="font-size: 0.34em" -->

```
+----------------------+------------------+--------------+------------------+----------------+
|      TEST CASE       |     PROJECT      |     TIER     |     DURATION     |     RESULT     |
+----------------------+------------------+--------------+------------------+----------------+
|     cloudify_ims     |     functest     |     vnf      |      28:15       |      PASS      |
|     vyos_vrouter     |     functest     |     vnf      |      17:59       |      PASS      |
|       juju_epc       |     functest     |     vnf      |      46:44       |      PASS      |
+----------------------+------------------+--------------+------------------+----------------+
```
<!-- .element: style="font-size: 0.34em" -->


### then run ONAP HealthCheck

- All tests are run by a specialized Docker container(**<100 MB**) instead of
the classical ONAP testing virtual machine (**> 1GB**).
- the container mainly inherits from opnfv/xtesting and is completed by:
  - Python dependencies
  - all ONAP Robot Framework files retrieved from the original repositories
  - testcases.yaml describing the testcases

[Orange-OpenSource/xtesting-onap-robot](https://github.com/Orange-OpenSource/xtesting-onap-robot/)


![ONAP](ONAP.png)
<!-- .element: style="border: 0; width: 70%" -->



## Conclusion


## Benefits

- Xtesting allows a proper design inside OPNFV
- Xtesting and Functest help other LFN projects:
  - verifying the infrastructure on top of which the components are deployed
  - ease verifying the components as well in the same CI/CD toolchain

  **All contributions coming from LFN projects are more than welcome!**
