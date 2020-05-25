ARG XTESTING_TAG=latest
FROM opnfv/xtesting:${XTESTING_TAG}
LABEL name="xtesting-mts"
LABEL version=${XTESTING_TAG}
LABEL description="MTS (Multi-protocol Test Suite) is a multi-protocol testing tool specially designed for telecom IP-based architectures"
LABEL maintainer=""
LABEL url="https://github.com/ericsson-mts/mts"

################################################################################
# Get build arguments
ARG MTS_TAG="6.6.3"
RUN if [ -z "$MTS_TAG" ]; then echo "ERROR: MTS_TAG NOT SET" >&2; exit 1; fi

# Prepare environment
ARG APP_FOLDER=/opt/mts
RUN apk add --no-cache --update bash libstdc++ curl zip libpcap-dev
RUN ln -s /usr/lib/libpcap.so /usr/lib/libpcap.so.0.8
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

################################################################################
# Install Git
RUN apk add git

################################################################################
# Install Java
RUN apk add --no-cache openjdk8 maven
ENV JAVA_HOME=/usr/lib/jvm/java-1.8-openjdk

# Env var used by MTS
ENV NGN_JAVA_HOME ${JAVA_HOME}/bin

COPY mts-installer.properties mts-installer.properties

################################################################################
# Generate MTS installer
RUN git clone -c advice.detachedHead=false --depth 1 --branch ${MTS_TAG} https://github.com/ericsson-mts/mts git-mts && \
    cd git-mts && \
    echo ${NGN_JAVA_HOME} > src/main/bin/java_home.release && \
    mvn versions:set -DnewVersion=${MTS_TAG} && mvn package && mvn install && \
    apk del openjdk8 maven && \
    apk add --no-cache openjdk8-jre && \
    java -jar target/mts-${MTS_TAG}-installer.jar -options ../mts-installer.properties && cd .. && rm mts-installer.properties && rm -rf git-mts && \
    rm -rf /root/.m2/ && rm -rf /var/cache/apk/* >/dev/null 2>&1

################################################################################
# Install MTS using the installer
#COPY mts-installer.properties git-mts/target/mts-installer.properties
## RUN java -jar git-mts/target/mts-${MTS_TAG}-installer.jar -options mts-installer.properties && rm -rf git-mts
#RUN echo ${JAVA_HOME}/bin > ${APP_FOLDER}/bin/java_home
COPY sample ${APP_FOLDER}/bin/test

################################################################################
# Remove build dependencies and any leftover apk cache (space optimization)
RUN rm -rf /var/cache/apk/* >/dev/null 2>&1 && \
    rm -rf /tmp/* >/dev/null 2>&1 && \
    rm -rf ${APP_FOLDER}/tutorial

################################################################################
# Set the dockerworker default command
COPY testcases.yaml /usr/lib/python3.8/site-packages/xtesting/ci/testcases.yaml

CMD ["run_tests", "-t", "all"]
#CMD ["/bin/bash"]
#ENTRYPOINT [""]
