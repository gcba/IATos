secret:
	envsubst < secret.yaml | kubectl apply -f -

config:
	kubectl apply -f config.yaml

deployment:
	envsubst < deployment.yaml | kubectl apply -f -

service:
	kubectl apply -f service.yaml

all: secret config deployment service