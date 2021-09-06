VERSION = v1.0.0

.PHONY: local-docker-image

local-docker-image:
	docker build --tag tosia-api:${VERSION} .

azure-docker-image:
	docker tag tosia-api:${VERSION} tosia.azurecr.io/api:${VERSION}
	docker push tosia.azurecr.io/api:${VERSION}