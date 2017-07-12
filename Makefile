.PHONY: run build sync run8 build8

CONTAINER=ddsfl
CONTAINERJDK8=ddsfljdk8
DOCKERFILEJDK8=Dockerfile_jdk8
DDSFL=`pwd`/../data-sfl

build: sync
	docker build -t ${CONTAINER} .

build8: sync
	docker build -f ${DOCKERFILEJDK8} -t ${CONTAINERJDK8} .

sync:
	rsync -avzh  --exclude '.git' --exclude '**/target/' ${DDSFL} .

run:
	docker run -it -v `pwd`/data:/data ${CONTAINER}

run8:
	docker run -it -v `pwd`/data:/data ${CONTAINERJDK8}
