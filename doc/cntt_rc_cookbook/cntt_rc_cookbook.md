# CNTT Snezka RC Cookbook

[Cédric Ollivier](mailto:cedric.ollivier@orange.com)

2020/01/15



## CNTT Snezka RC


### CNTT RI and RC toolchains

- leverage on existing OPNFV testing knowledge and experience
- conform to LFN CI/CD toolchain continuously deploying and testing NFVI
- deploy locally the same components via
  [Xtesting CI](https://galaxy.ansible.com/collivier/xtesting) in case of RC


### TC integration requirements

- enforce that the test cases are delivered with all runtime dependencies
- avoid manual operations when configuring the server running the test cases
- conform to the common test case execution
- leverage on an unified way to manage all the interactions with the CI/CD
  components and with third-parties

**2 simple requirements: [Docker](https://www.docker.com/) + [Xtesting](https://xtesting.readthedocs.io/en/latest/)**


### Run CNTT RC Cookbook

- copy/paste the following commands:
```bash
virtualenv functest
. functest/bin/activate
pip install ansible
ansible-galaxy install collivier.xtesting
git clone https://gerrit.opnfv.org/gerrit/functest functest-src
(cd functest-src && git checkout -b stable/hunter origin/stable/hunter)
ansible-playbook functest-src/ansible/site.cntt.yml
```
- prepare the TC requirements (credentials, images, etc.)
- trigger the job on the local Jenkins and send the final archive to
  third-party certification

**Try it, and you will love it!**



## CNTT Post-Snezka RC


### Update the OPNFV TCs

- [port YardStick testcases to Xtesting](https://github.com/cntt-n/CNTT/issues/509)
- [port Bottlenecks to Xtesting](https://github.com/cntt-n/CNTT/issues/511)
- [port StorPerf testcases to Xtesting](https://github.com/cntt-n/CNTT/issues/673)
- [port NFVbench testcases to Xtesting](https://github.com/cntt-n/CNTT/issues/865)


### Increase the test coverage

- [add heat-tempest-plugin to Functest](https://github.com/cntt-n/CNTT/issues/483)
- [add KloudBuster to Functest](https://github.com/cntt-n/CNTT/issues/508)
- [add tempest-stress to Functest](https://github.com/cntt-n/CNTT/issues/916)



## Conclusion


### Takeaways

- the RI/RC model is very simple and pragmatic
- it eases smootly integrating new test cases without extra logics and skills
- it's already in-use in Functest Kubernetes which should be more than an help
  for CNTT RC2 (see k8s_conformance and xrally_kubernetes)

**Any contribution is more than welcome!**
