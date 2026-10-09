include .env
export

build_dev:
	sh build.dev.sh;

dev:
	docker compose --env-file .env.dev -f docker-compose.yml -f docker-compose.dev.yml up --force-recreate -d;
