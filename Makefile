
@PHONY: format
format:
	@black .
	@isort .

@PHONY: lint
lint:
	@pflake8 .