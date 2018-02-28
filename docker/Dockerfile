FROM alpine:3.7

ARG BRANCH=master
ARG OPENSTACK_TAG=stable/pike

RUN apk --no-cache add --update \
        python libffi libssl1.0 libjpeg-turbo py-pip bash \
        grep sed wget ca-certificates git && \
    apk --no-cache add --virtual .build-deps --update \
        python-dev build-base linux-headers libffi-dev \
        openssl-dev libjpeg-turbo-dev && \
    git clone https://gerrit.opnfv.org/gerrit/functest-xtesting /src/functest-xtesting && \
    (cd /src/functest-xtesting && git fetch origin $BRANCH && git checkout FETCH_HEAD) && \
    pip install --no-cache-dir --src /src \
        -chttps://git.openstack.org/cgit/openstack/requirements/plain/upper-constraints.txt?h=$OPENSTACK_TAG \
        -chttps://git.opnfv.org/functest-xtesting/plain/upper-constraints.txt?h=$BRANCH \
        /src/functest-xtesting && \
    rm -r /src/functest-xtesting && \
    bash -c "mkdir -p /home/opnfv/xtesting/results/robot" && \
    apk del .build-deps
