.DEFAULT_GOAL := help
UV ?= uv

.PHONY: help sync fonts test cov lint fix check hooks run gen stand clean

GEN_FONT ?= fonts/Sniglet-ExtraBold.ttf
GEN_CHARS ?= AÁBCDÐEÉFGHIÍJKLMNOÓPQRSTUÚVWXYÝZÞÆÖ
STAND_SIZE ?= 80

help: ## list available targets
	@grep -hE '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  %-6s %s\n", $$1, $$2}'

sync: ## create .venv and install dev dependencies
	$(UV) sync

fonts: ## download heavy display fonts into fonts/ (gitignored)
	$(UV) run python scripts/fetch_fonts.py

test: ## run the test suite
	$(UV) run pytest

cov: ## run the test suite with a coverage report
	$(UV) run pytest --cov --cov-report=term-missing

lint: ## ruff check, format check and mypy
	$(UV) run ruff check .
	$(UV) run ruff format --check .
	$(UV) run mypy

fix: ## apply ruff formatting and safe lint fixes
	$(UV) run ruff format .
	$(UV) run ruff check --fix .

check: lint test ## run everything required before committing

hooks: ## install the pre-commit hooks
	$(UV) run pre-commit install

run: ## generate letters, e.g. make run FONT=Inter.ttf CHARS=ABC
	$(UV) run bubblegen --font $(FONT) --chars $(CHARS)

$(GEN_FONT): ## fetched on demand: gen needs its font present
	$(UV) run python scripts/fetch_fonts.py

gen: $(GEN_FONT) ## the reference alphabet: Sniglet, Icelandic + English chars, default balloon parameters
	$(UV) run bubblegen --font $(GEN_FONT) --chars "$(GEN_CHARS)"

stand: ## painting stand, e.g. make stand STAND_SIZE=110
	$(UV) run bubblegen-stand --size $(STAND_SIZE)

clean: ## remove caches, build artifacts and generated meshes
	rm -rf .mypy_cache .ruff_cache .pytest_cache .coverage build dist out
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
