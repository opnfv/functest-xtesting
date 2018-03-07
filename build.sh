#!/bin/bash

set -e

repo=${REPO:-opnfv}
tag=${BRANCH:-latest}
arch=${ARCH_TAG:-'x86_64'}
image="functest-xtesting"

build_opts=(--pull=true --no-cache --force-rm=true)

build() {
    if [[ ${arch} == 'aarch64' ]]; then
        find . -name Dockerfile -exec sed -i -e "s|alpine:3.7|multiarch/alpine:arm64-v3.7|g" {} +
    fi
    cd ./docker  && sudo  docker build "${build_opts[@]}" -t "${repo}/${image}:${arch}-${tag}" .
    sudo docker push "${repo}/${image}:${arch}-${tag}"
    sudo docker rmi "${repo}/${image}:${arch}-${tag}"
    exit $?
}
clean () {
    find . -name Dockerfile -exec git checkout \{\} +;
    exit $?
}
manifest() {
    sudo manifest-tool push from-args \
    --platforms linux/amd64,linux/arm64 \
    --template ${repo}/${image}:ARCH-${tag} \
    --target ${repo}/${image}:${tag}
    exit $?
}

"$@"
