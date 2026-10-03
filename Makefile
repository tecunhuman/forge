-include .env

up:
	docker compose up -d

down:
	docker compose down

init:
	mkdir -p $(FORGE_DATA)/forgejo-data $(FORGE_DATA)/runner
	docker run --rm --user root -v $(FORGE_DATA)/runner:/data data.forgejo.org/forgejo/runner:13 chown -R 1001:1001 /data

server:
	docker compose up -d server

RUNNER = docker run --rm --user 1001:1001 -v $(FORGE_DATA)/runner:/data -w /data \
	--network forge_forgejo data.forgejo.org/forgejo/runner:13

runner-config:
	$(RUNNER) sh -c 'forgejo-runner generate-config | \
		sed -e "s|^  network: \"\"$$|  network: host|" -e "s|^  capacity: 1$$|  capacity: $(RUNNER_CAPACITY)|" > runner-config.yml'

register:
	$(RUNNER) forgejo-runner register --no-interactive \
		--instance http://$(FORGE_HOST):3000 --name local --labels docker:docker://node:20-bookworm \
		--token $$(docker exec -u git forgejo forgejo forgejo-cli actions generate-runner-token)

backup:
	./backup.sh

logs:
	docker compose logs -f
