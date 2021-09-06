.ONESHELL:
.PHONY: docker pyenv clean-pyc clean-test clean-env

docker:
	docker build --tag tosia-api-algos:0.1 .
	docker run -it --rm tosia-api-algos:0.1

pyenv:
	virtualenv .venv
	.venv/bin/pip install -r requirements.txt
	.venv/bin/python example.py

test:
	python -m pytest

clean: clean-pyc clean-test clean-env

clean-pyc:
	find . -name '__pycache__' -exec rm -fr {} +
	
clean-test:	
	rm -rf .pytest_cache/
	
clean-env:
	rm -rf .venv/
	rm -rf .vscode/
	