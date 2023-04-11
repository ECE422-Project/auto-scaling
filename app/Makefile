deploy:
	docker stack deploy --compose-file docker-compose.yaml ping-app
tear:
	docker stack rm ping-app
build:
	docker build -t n0tdekr0/ping .
push:
	docker build -t n0tdekr0/ping .
	docker image tag n0tdekr0/ping n0tdekr0/ping:latest
	docker image push n0tdekr0/ping:latest
clean:
	docker image rm n0tdekr0/ping:latest 
