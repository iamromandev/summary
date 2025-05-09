# system
.PHONY: clean-system
clean-system:
	docker system prune -a --force

.PHONY: clean-db
clean-db:
	docker volume prune --all --force

.PHONY: clean
clean:
	make clean-system
	make clean-db

.PHONY: ps
ps:
	docker compose ps -a

# local
.PHONY: build
build:
	COMPOSE_BAKE=true docker compose -f docker-compose.yml build

.PHONY: up
up:
	docker compose -f docker-compose.yml up -d

.PHONY: stop
stop:
	docker compose -f docker-compose.yml stop

.PHONY: down
down:
	docker compose -f docker-compose.yml down

.PHONY: restart
restart:
	make stop
	make build
	make up

.PHONY: uv install
install:
	uv pip install -r pyproject.toml
	uv lock

.PHONY: ruff
ruff:
	make install
	uvx ruff check --fix

.PHONY: run
run:
	make ruff
	uv run uvicorn src.main:app --reload

.PHONY: export
export:
	make ruff
	uv export --format requirements-txt > requirements.txt
