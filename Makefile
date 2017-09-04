.PHONY: build build8 mvn-package

CONTAINER=qsfl
CONTAINERJDK8=qsfljdk8
DOCKERFILEJDK8=Dockerfile_jdk8
QSFL=`pwd`/../data-sfl
FLDATA=https://bitbucket.org/rjust/fault-localization-data.git

all: build build8 q-sfl fault-localization-data mvn-package

build: q-sfl
	docker build -t ${CONTAINER} .

build8: q-sfl
	docker build -f ${DOCKERFILEJDK8} -t ${CONTAINERJDK8} .

q-sfl:
	git clone ${QSFL} q-sfl

fault-localization-data:
	git clone ${FLDATA} fault-localization-data

mvn-package: q-sfl
	cd q-sfl && mvn package
