-include .env

up:
	docker compose up -d

down:
	docker compose down

init:
	mkdir -p $(FORGE_DATA)/forgejo-data $(FORGE_DATA)/runner
	docker compose run --rm --no-deps --user root --entrypoint chown runner -R 1001:1001 /data

server:
	docker compose up -d server

runner-config:
	docker compose run --rm --no-deps --entrypoint sh runner -c 'forgejo-runner generate-config > /data/runner-config.yml'

register:
	docker compose run --rm runner forgejo-runner register --no-interactive \
		--instance http://forgejo:3000 --token $$(docker exec -u git forgejo forgejo forgejo-cli actions generate-runner-token) --name local \
		--labels docker:docker://node:20-bookworm

backup:
	./backup.sh

logs:
	docker compose logs -f
