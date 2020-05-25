# Docker image for MTS built from source code

MTS (Multi-protocol Test Suite) is a multi-protocol testing tool specially designed for telecom IP-based architectures (see above "Features" section for more details).

It uses the MTS source codes located at <https://github.com/ericsson-mts/mts/> to build an MTS installer and use it to install the software into `/opt/mts` inside the container.

## To build the image

Set the version of the `opnfv/xtesting` base image you want to use (`latest`, `hunter`, `jerma`, ...):

```bash
export XTESTING_TAG=latest
```

To build a version `6.6.3` of the MTS software, launch the following command:

```bash
docker build --build-arg MTS_TAG="6.6.3" --build-arg XTESTING_TAG=$XTESTING_TAG -t opnfv/xtesting-mts:6.6.3-$XTESTING_TAG .
```

With proxies :
```bash
docker build --build-arg MTS_TAG="6.6.3" --build-arg XTESTING_TAG=$XTESTING_TAG --build-arg http_proxy=$HTTP_PROXY --build-arg https_proxy=$HTTPS_PROXY --build-arg no_proxy=$NO_PROXY -t opnfv/xtesting-mts:6.6.3-$XTESTING_TAG .
```

## To run the container

To launch the image :

```bash
docker run -it opnfv/xtesting-mts:6.6.3-$XTESTING_TAG
```

Note: during the build, Maven generates :
- the mts package in folder `/root/.m2/repository/com/ericsson/mts`
- and a `mts-${MTS_TAG}-installer.jar` file inside the `target` subdir of the cloned git project,
but all this is purged after using the installer to install MTS.

## To launch MTS inside the container

Inside the container, go to folder `/opt/mts/bin` and launch this command:

```bash
./startCmd.sh test/test.xml -sequential -levelLog:DEBUG -stor:file
```
