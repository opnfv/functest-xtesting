FROM alpine:3.9

ARG BRANCH=stable/hunter
ARG OPENSTACK_TAG=stable/rocky

RUN apk --no-cache add --update python py-pip bash git mailcap && \
    apk --no-cache add --virtual .build-deps --update \
        python-dev build-base && \
    git init /src/functest-xtesting && \
    (cd /src/functest-xtesting && \
        git fetch --tags https://gerrit.opnfv.org/gerrit/functest-xtesting $BRANCH && \
        git checkout FETCH_HEAD) && \
    pip install --no-cache-dir --src /src \
        -chttps://opendev.org/openstack/requirements/raw/branch/$OPENSTACK_TAG/upper-constraints.txt \
        -chttps://git.opnfv.org/functest-xtesting/plain/upper-constraints.txt?h=$BRANCH \
        /src/functest-xtesting && \
    rm -r /src/functest-xtesting && \
    apk del .build-deps
COPY testcases.yaml /usr/lib/python2.7/site-packages/xtesting/ci/testcases.yaml
CMD ["run_tests", "-t", "all"]
