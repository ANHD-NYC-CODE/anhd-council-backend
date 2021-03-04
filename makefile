include .env
export

dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d;
