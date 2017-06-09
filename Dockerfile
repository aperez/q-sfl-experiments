FROM maven:3-jdk-7

RUN \
    apt-get update && \
    apt-get install -y wget python3-pip python3-yaml git subversion && \
    rm -rf /var/lib/apt/lists/*

RUN \
    wget https://github.com/rjust/defects4j/archive/v1.1.0.tar.gz && \
    tar xf v1.1.0.tar.gz && \
    cd defects4j-1.1.0 && \
    ./init.sh

ENV PATH="/defects4j-1.1.0/framework/bin/:${PATH}"
ENV TZ="America/Los_Angeles"

COPY data-sfl/ /data-sfl/
RUN \
    cd /data-sfl/ && \
    mvn -q package

RUN mkdir /data

WORKDIR /home/
COPY run_experiment.py /home/
COPY experiment.yml /home/

CMD ["bash"]
