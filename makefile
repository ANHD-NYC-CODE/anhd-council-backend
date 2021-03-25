include .env
export

build_dev:
	sh build.dev.sh;

dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --force-recreate -d;
