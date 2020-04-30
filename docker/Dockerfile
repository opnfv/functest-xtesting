FROM alpine:3.11

ARG BRANCH=stable/kali
ARG OPENSTACK_TAG=stable/ussuri

RUN apk --no-cache add --update python3 bash git mailcap && \
    apk --no-cache add --virtual .build-deps --update \
        python3-dev build-base && \
    git init /src/functest-xtesting && \
    (cd /src/functest-xtesting && \
        git fetch --tags https://gerrit.opnfv.org/gerrit/functest-xtesting $BRANCH && \
        git checkout FETCH_HEAD) && \
    pip3 install --no-cache-dir --src /src \
        -chttps://opendev.org/openstack/requirements/raw/branch/$OPENSTACK_TAG/upper-constraints.txt \
        -chttps://git.opnfv.org/functest-xtesting/plain/upper-constraints.txt?h=$BRANCH \
        /src/functest-xtesting && \
    rm -r /src/functest-xtesting && \
    apk del .build-deps
COPY testcases.yaml /usr/lib/python3.8/site-packages/xtesting/ci/testcases.yaml
CMD ["run_tests", "-t", "all"]
