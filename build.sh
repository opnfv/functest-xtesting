#!/bin/bash

# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
# http://www.apache.org/licenses/LICENSE-2.0

set -xe

repo=${REPO:-opnfv}
tag=${BRANCH:-kali}
arch=${arch-"\
amd64 \
arm64 \
arm"}
image="xtesting"
build_opts=(--pull=true --no-cache --force-rm=true)

for arch in ${arch};do
    if [[ ${arch} == arm64 ]]; then
        find . -name Dockerfile -exec sed -i \
            -e "s|alpine:3.11|arm64v8/alpine:3.11|g" {} +
    elif [[ ${arch} == arm ]]; then
        find . -name Dockerfile -exec sed -i \
            -e "s|alpine:3.11|arm32v6/alpine:3.11|g" {} +
    fi
    (cd docker &&   docker build "${build_opts[@]}" \
        -t "${repo}/${image}:${arch}-${tag}" .)
    docker push "${repo}/${image}:${arch}-${tag}"
    [ "$?" == "0" ] &&
        (sudo docker rmi "${repo}/${image}:${arch}-${tag}"|| true)
    find . -name Dockerfile -exec git checkout \{\} +;
done
exit $?
