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
	@scripts/terraform-output-to-env.sh
	@scripts/generate-dev-env.sh


@PHONY: destroy
destroy:
	@cdktf destroy '*'