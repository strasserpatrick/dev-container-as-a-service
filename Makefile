@PHONY: format
format:
	@black .
	@blacken-docs README.md
	@isort .

@PHONY: lint
lint:
	@pflake8 .

@PHONY: synth
synth:
	@cdktf synth

@PHONY: deploy
deploy:
	@cdktf deploy --outputs-file .terraform/output.json '*'


@PHONY: destroy
destroy:
	@cdktf destroy '*'