APP=pipo_transmuter_spotify
CONFIG_PATH=pyproject.toml
POETRY=poetry
POETRY_VERSION=1.8.4
PRINT=python -c "import sys; print(str(sys.argv[1]))"
DOCUMENTATION=docs
DIAGRAMS_FORMAT=plantuml
TEST_FOLDER=./tests

-include .env

TEST_SECRETS:=$(shell realpath $(TEST_FOLDER)/.secrets.*)
SECRETS_JSON=$(shell echo '{"TEST_RABBITMQ_URL": "$(TEST_RABBITMQ_URL)", "TEST_SPOTIFY_CLIENT": "$(TEST_SPOTIFY_CLIENT)", "TEST_SPOTIFY_SECRET": "$(TEST_SPOTIFY_SECRET)"}')

.PHONY: help
help:
	$(PRINT) "Usage:"
	$(PRINT) "    help          show this message"
	$(PRINT) "    poetry_setup  install poetry to manage python envs and workflows"
	$(PRINT) "    setup         build virtual environment and install dependencies"
	$(PRINT) "    test_setup    build virtual environment and install test dependencies"
	$(PRINT) "    dev_setup     build virtual environment and install dev dependencies"
	$(PRINT) "    lint          run dev utilities for code quality assurance"
	$(PRINT) "    format        run dev utilities for code format assurance"
	$(PRINT) "    docs          generate code documentation"
	$(PRINT) "    metrics       evaluate source code quality"
	$(PRINT) "    test          run test suite"
	$(PRINT) "    coverage      run coverage analysis"
	$(PRINT) "    set_version   set program version"
	$(PRINT) "    dist          package application for distribution"
	$(PRINT) "    image         build app docker image"
	$(PRINT) "    test_image    run test suite in a container"
	$(PRINT) "    run_image     run app docker image in a container"

.PHONY: poetry_setup
poetry_setup:
	curl -sSL https://install.python-poetry.org | python - --version $(POETRY_VERSION)
	$(POETRY) config virtualenvs.in-project true --local

.PHONY: setup
setup:
	$(POETRY) install -n --all-extras --without dev

.PHONY: test_setup
test_setup:
	$(POETRY) install -n --all-extras

.PHONY: dev_setup
dev_setup:
	$(POETRY) install -n --all-extras --with docs

.PHONY: update_deps
update_deps:
	$(POETRY) update

.PHONY: check
check:
	-$(POETRY) run ruff check .

.PHONY: format
format:
	-$(POETRY) run ruff format .

.PHONY: vulture
vulture:
	-$(POETRY) run vulture

.PHONY: metrics
metrics:
	$(POETRY) run radon cc -a -s -o SCORE $(APP)
	$(POETRY) run radon raw -s $(APP)
	$(POETRY) run radon mi -s $(APP)

.PHONY: lint
lint: check vulture

.PHONY: test_secrets_file
test_secrets_file:
	$(POETRY) run dynaconf write yaml -y -e test -p "$(TEST_FOLDER)/" -s queue_broker_url="${TEST_RABBITMQ_URL}" -s spotify_client="${TEST_SPOTIFY_CLIENT}" -s spotify_secret="${TEST_SPOTIFY_SECRET}"
	@echo $(TEST_SECRETS)

.PHONY: test
test:
	if [ -f $(TEST_SECRETS) ]; then \
		export SECRETS_FOR_DYNACONF=$(TEST_SECRETS) && $(POETRY) run pytest; \
	else \
		$(POETRY) run pytest; \
	fi

.PHONY: coverage
coverage:
	$(POETRY) run coverage report -m

.PHONY: docs
docs:
	mkdir -p $(DOCUMENTATION)/_static $(DOCUMENTATION)/_diagrams/src
	$(POETRY) run pyreverse -p $(APP) \
		--colorized \
		-o $(DIAGRAMS_FORMAT) \
		-d $(DOCUMENTATION)/_diagrams/src $(APP)
	$(POETRY) run make -C $(DOCUMENTATION) html

.PHONY: set_version
set_version:
	$(POETRY) version $$VERSION

.PHONY: dist
dist:
	$(POETRY) dist

.PHONY: image
image: docs
	docker buildx bake image-local

.PHONY: test_image
test_image:
	docker buildx bake test

.PHONY: run_image
run_image: image
	docker run -d --name $(APP) --env-file .env $(APP):latest
