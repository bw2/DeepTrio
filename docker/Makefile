TAG1 = weisburd/deepvariant:v1.1.0
TAG2 = weisburd/deepvariant:latest

all: build push

build:
	docker build -t $(TAG1) -t $(TAG2) .

push:
	docker push $(TAG1)
	docker push $(TAG2)
