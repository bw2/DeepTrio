TAG1 = weisburd/deepvariant:deeptrio-1.1.0-gpu

all: build push

build:
	docker build -t $(TAG1) .

push:
	docker push $(TAG1)
