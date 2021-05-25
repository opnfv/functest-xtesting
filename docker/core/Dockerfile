FROM alpine:3.13

ARG BRANCH=master
ARG OPENSTACK_TAG=master

RUN apk -U upgrade && \
    apk --no-cache add --update python3 py3-pip py3-wheel bash git mailcap libxml2 libxslt ansible && \
    apk --no-cache add --virtual .build-deps --update \
        python3-dev build-base libxml2-dev libxslt-dev linux-headers && \
    wget -q -O- https://opendev.org/openstack/requirements/raw/branch/$OPENSTACK_TAG/upper-constraints.txt > upper-constraints.txt && \
    sed -i -E /^PyYAML==+.*$/d upper-constraints.txt && \
    sed -i -E /^six==+.*$/d upper-constraints.txt && \
    case $(uname -m) in aarch*|arm*) CFLAGS="-O0" \
        pip3 install --no-cache-dir \
            -cupper-constraints.txt \
            -chttps://git.opnfv.org/functest-xtesting/plain/upper-constraints.txt?h=$BRANCH \
            lxml ;; esac && \
    git init /src/functest-xtesting && \
    (cd /src/functest-xtesting && \
        git fetch --tags https://gerrit.opnfv.org/gerrit/functest-xtesting $BRANCH && \
        git checkout FETCH_HEAD) && \
    pip3 install --no-cache-dir --src /src \
        -cupper-constraints.txt \
        -chttps://git.opnfv.org/functest-xtesting/plain/upper-constraints.txt?h=$BRANCH \
        /src/functest-xtesting && \
    rm -r /src/functest-xtesting upper-constraints.txt && \
    apk del .build-deps
COPY testcases.yaml /usr/lib/python3.8/site-packages/xtesting/ci/testcases.yaml
CMD ["run_tests", "-t", "all"]
