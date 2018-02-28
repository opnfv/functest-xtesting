FROM alpine:3.7

ARG BRANCH=master
ARG OPENSTACK_TAG=stable/pike

RUN apk --no-cache add --update python py-pip bash git && \
    git clone https://gerrit.opnfv.org/gerrit/functest-xtesting /src/functest-xtesting && \
    (cd /src/functest-xtesting && git fetch origin $BRANCH && git checkout FETCH_HEAD) && \
    pip install --no-cache-dir --src /src \
        -chttps://git.openstack.org/cgit/openstack/requirements/plain/upper-constraints.txt?h=$OPENSTACK_TAG \
        -chttps://git.opnfv.org/functest-xtesting/plain/upper-constraints.txt?h=$BRANCH \
        /src/functest-xtesting && \
    rm -r /src/functest-xtesting
CMD ["run_tests", "-t", "all"]
