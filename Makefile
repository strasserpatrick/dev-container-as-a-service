
@PHONY: format
format:
	@black .
	@blacken-docs README.md
	@isort .

@PHONY: lint
lint:
	@pflake8 .