FROM alpine:3.9

ARG BRANCH=stable/iruya
ARG OPENSTACK_TAG=stable/stein

RUN apk --no-cache add --update python3 py3-pip bash git mailcap libxml2 libxslt && \
    apk --no-cache add --virtual .build-deps --update \
        python3-dev build-base libxml2-dev libxslt-dev && \
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
COPY testcases.yaml /usr/lib/python3.6/site-packages/xtesting/ci/testcases.yaml
CMD ["run_tests", "-t", "all"]
