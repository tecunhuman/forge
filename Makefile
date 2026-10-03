-include .env

up:
	docker compose up -d

down:
	docker compose down

init:
	mkdir -p $(FORGE_DATA)/forgejo-data $(FORGE_DATA)/runner
	sudo chown -R 1001:1001 $(FORGE_DATA)/runner

server:
	docker compose up -d server

runner-config:
	docker compose run --rm runner forgejo-runner generate-config > $(FORGE_DATA)/runner/runner-config.yml

register:
	docker compose run --rm runner forgejo-runner register --no-interactive \
		--instance http://forgejo:3000 --token $(TOKEN) --name local \
		--labels docker:docker://node:20-bookworm

backup:
	./backup.sh

logs:
	docker compose logs -f
