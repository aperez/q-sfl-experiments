.PHONY: run build sync

CONTAINER=ddsfl
DDSFL=/Users/aperez/Work/TQRG/data-sfl

build: sync
	docker build -t ${CONTAINER} .

sync:
	rsync -avzh  --exclude '.git' --exclude '**/target/' ${DDSFL} .

run:
	docker run -it -v `pwd`/data:/data ${CONTAINER}
