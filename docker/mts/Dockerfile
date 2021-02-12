FROM opnfv/xtesting

ARG MTS_TAG=6.6.21
ARG APP_FOLDER=/opt/mts
ARG MAVEN_OPTS=
ENV JAVA_HOME=/usr/lib/jvm/java-1.8-openjdk
ENV NGN_JAVA_HOME=${JAVA_HOME}/bin
ENV MAVEN_OPTS=$MAVEN_OPTS

COPY mts-installer.properties /src/mts-installer.properties
RUN case $(uname -m) in x86_64) \
        apk --no-cache add --update openjdk8-jre && \
        apk --no-cache add --virtual .build-deps --update \
            openjdk8 maven git && \
        git init /src/git-mts && \
        (cd /src/git-mts && \
            git fetch --tags https://github.com/ericsson-mts/mts $MTS_TAG && \
            git checkout FETCH_HEAD && \
            echo ${NGN_JAVA_HOME} > src/main/bin/java_home.release && \
            mvn versions:set -DnewVersion=${MTS_TAG} && mvn package && mvn install && \
            java -jar target/mts-${MTS_TAG}-installer.jar -options /src/mts-installer.properties) && \
        rm -rf /root/.m2/ ${APP_FOLDER}/tutorial /src/mts-installer.properties /src/git-mts && \
        apk del .build-deps;; esac
COPY testcases.yaml /usr/lib/python3.8/site-packages/xtesting/ci/testcases.yaml
CMD ["run_tests", "-t", "all"]
