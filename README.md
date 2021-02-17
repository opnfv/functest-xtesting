# Xtesting in a nutshell

Xtesting is a simple framework to assemble sparse test cases and to accelerate
the adoption of continuous integration best practices. By managing all
the interactions with the components (test scheduler, test results database,
artifact repository), it allows the developer to work only on the test suites
without diving into CI/CD.

It asks for a few low constraints
[quickly achievable](https://www.sdxcentral.com/articles/news/opnfvs-6th-release-brings-testing-capabilities-that-orange-is-already-using/2018/05/)
to verify multiple components in the same CI/CD toolchain. Even more, it brings
the capability to run third-party test cases in our CI toolchains and then to
also rate network functions by the coverage.

Please see
[the Katacoda scenarios](https://www.katacoda.com/ollivier/courses/xtestingci)
to try Xtesting. You will love them!

## [Write your own Xtesting driver](https://www.katacoda.com/ollivier/courses/xtestingci/firstdriver)

### dump all the following files in an empty dir

weather.py

```python
#!/usr/bin/env python

# pylint: disable=missing-docstring

import json
import os
import sys
import time

import requests

from xtesting.core import testcase


class Weather(testcase.TestCase):

    url = "https://samples.openweathermap.org/data/2.5/weather"
    city_name = "London,uk"
    app_key = "439d4b804bc8187953eb36d2a8c26a02"

    def run(self, **kwargs):
        try:
            self.start_time = time.time()
            req = requests.get("{}?q={}&&appid={}".format(
                self.url, self.city_name, self.app_key))
            req.raise_for_status()
            data = req.json()
            os.makedirs(self.res_dir, exist_ok=True)
            with open('{}/dump.txt'.format(self.res_dir), 'w+') as report:
                json.dump(data, report, indent=4, sort_keys=True)
            for key in kwargs:
                if data["main"][key] > kwargs[key]:
                    self.result = self.result + 100/len(kwargs)
            self.stop_time = time.time()
        except Exception:  # pylint: disable=broad-except
            print("Unexpected error:", sys.exc_info()[0])
            self.result = 0
            self.stop_time = time.time()
```

setup.py

```python
#!/usr/bin/env python

# pylint: disable=missing-docstring

import setuptools

setuptools.setup(
    setup_requires=['pbr>=2.0.0'],
    pbr=True)
```

setup.cfg

```
[metadata]
name = weather
version = 1

[files]
packages = .

[entry_points]
xtesting.testcase =
    weather = weather:Weather
```

requirements.txt

```
xtesting
requests!=2.20.0,!=2.24.0 # Apache-2.0
```

testcases.yaml

```yaml
---
tiers:
    -
        name: simple
        order: 0
        description: ''
        testcases:
            -
                case_name: humidity
                project_name: weather
                criteria: 100
                blocking: true
                clean_flag: false
                description: ''
                run:
                    name: weather
                    args:
                        humidity: 80
            -
                case_name: pressure
                project_name: weather
                criteria: 100
                blocking: true
                clean_flag: false
                description: ''
                run:
                    name: weather
                    args:
                        pressure: 1000
            -
                case_name: temp
                project_name: weather
                criteria: 100
                blocking: true
                clean_flag: false
                description: ''
                run:
                    name: weather
                    args:
                        temp: 280
    -
        name: combined
        order: 1
        description: ''
        testcases:
            -
                case_name: half
                project_name: weather
                criteria: 50
                blocking: true
                clean_flag: false
                description: ''
                run:
                    name: weather
                    args:
                        humidity: 90
                        pressure: 1000
                        temp: 280
```

Dockerfile

```
FROM alpine:3.12

ADD . /src/
RUN apk --no-cache add --update python3 py3-pip py3-wheel git && \
    git init /src && pip3 install /src
COPY testcases.yaml /usr/lib/python3.8/site-packages/xtesting/ci/testcases.yaml
CMD ["run_tests", "-t", "all"]
```

### make world

Deploy your own Xtesting toolchain

```bash
virtualenv xtesting
. xtesting/bin/activate
pip install ansible
ansible-galaxy install collivier.xtesting
ansible-galaxy collection install ansible.posix community.general community.grafana community.kubernetes
ansible-playbook site.yml
deactivate
rm -r xtesting
```

Build your container

```bash
sudo docker build -t 127.0.0.1:5000/weather .
```

Publish your container on your local repository

```bash
sudo docker push 127.0.0.1:5000/weather
```

### That's all folks!
