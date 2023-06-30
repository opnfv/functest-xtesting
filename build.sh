#!/bin/sh

# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

set -xe

repo=${REPO:-opnfv}
arch=${arch-"\
amd64 \
arm64 \
arm"}
amd64_dirs=${amd64_dirs-"\
docker/core \
docker/mts"}
arm_dirs=${arm_dirs-${amd64_dirs}}
arm64_dirs=${arm64_dirs-${amd64_dirs}}
tag=${BRANCH:-latest}
image="xtesting"
build_opts="--pull=true --no-cache --force-rm=true"

if [ `which podman` ];then
    DOCKER_CMD=podman
else
    if [ ! `which $DOCKER_CMD` ];then
        echo "no docker command available" >&2
        exit 1
    fi
    #if "docker ps" cannot be run without error, prepend sudo
    if ( ! $DOCKER_CMD ps >/dev/null 2>&1 );then
        echo "docker command only usable as root, using sudo" >&2
        DOCKER_CMD="sudo docker"
    fi
fi

for arch in ${arch}; do
    if [ "${arch}" = "arm64" ]; then
        find . -name Dockerfile -exec sed -i \
            -e "s|alpine:3.15|arm64v8/alpine:3.15|g" {} +
        find . -name Dockerfile -exec sed -i \
            -e "s|opnfv/xtesting|${repo}/xtesting:arm64-${tag}|g" {} +
    elif [ "${arch}" = "arm" ]; then
        find . -name Dockerfile -exec sed -i \
            -e "s|alpine:3.15|arm32v6/alpine:3.15|g" {} +
        find . -name Dockerfile -exec sed -i \
            -e "s|opnfv/xtesting|${repo}/xtesting:arm-${tag}|g" {} +
    else
        find . -name Dockerfile -exec sed -i \
            -e "s|opnfv/xtesting|${repo}/xtesting:amd64-${tag}|g" {} +
    fi
    dirs=${arch}_dirs
    # eval presents no security issue here if possible values of ${arch} are constrained
    eval dirlist=\$$dirs
    for dir in $dirlist; do
        if [ "${dir}" = "docker/core" ]; then
            image=xtesting
        else
            image=xtesting-${dir##**/}
        fi
        (cd "${dir}" &&
            $DOCKER_CMD build $build_opts \
                -t "${repo}/${image}:${arch}-${tag}" . &&
            $DOCKER_CMD push "${repo}/${image}:${arch}-${tag}")
        [ "${dir}" != "docker/core" ] &&
            ($DOCKER_CMD rmi \
                "${repo}/${image}:${arch}-${tag}" || true)
    done
    [ "$?" = "0" ] &&
        ($DOCKER_CMD rmi "${repo}/xtesting:${arch}-${tag}"|| true)
    find . -name Dockerfile -exec git checkout \{\} +;
done
exit $?
