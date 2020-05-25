#!/bin/bash

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
build_opts=(--pull=true --no-cache --force-rm=true)

for arch in ${arch}; do
    if [[ ${arch} == arm64 ]]; then
        find . -name Dockerfile -exec sed -i \
            -e "s|alpine:3.12|arm64v8/alpine:3.12|g" {} +
        find . -name Dockerfile -exec sed -i \
            -e "s|opnfv/xtesting|${repo}/xtesting:arm64-${tag}|g" {} +
    elif [[ ${arch} == arm ]]; then
        find . -name Dockerfile -exec sed -i \
            -e "s|alpine:3.12|arm32v6/alpine:3.12|g" {} +
        find . -name Dockerfile -exec sed -i \
            -e "s|opnfv/xtesting|${repo}/xtesting:arm-${tag}|g" {} +
    else
        find . -name Dockerfile -exec sed -i \
            -e "s|opnfv/xtesting|${repo}/xtesting:amd64-${tag}|g" {} +
    fi
    dirs=${arch}_dirs
    for dir in ${!dirs}; do
        if [[ ${dir} == docker/core ]]; then
            image=xtesting
        else
            image=xtesting-${dir##**/}
        fi
        (cd "${dir}" &&
            docker build "${build_opts[@]}" \
                -t "${repo}/${image}:${arch}-${tag}" . &&
            docker push "${repo}/${image}:${arch}-${tag}")
        [ "${dir}" != "docker/core" ] &&
            (docker rmi \
                "${repo}/${image}:${arch}-${tag}" || true)
    done
    [ "$?" == "0" ] &&
        (sudo docker rmi "${repo}/xtesting:${arch}-${tag}"|| true)
    find . -name Dockerfile -exec git checkout \{\} +;
done
exit $?
