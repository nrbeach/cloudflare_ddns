image_tag = docker.i860.cc/cloudflare_ddns

build-image:
	@docker build -t $(image_tag) .

push-image:
	@docker push $(image_tag):latest

build: build-image push-image

test: 
	@pytest

