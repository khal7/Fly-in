

install:
	python3 -m venv .venv
	.venv/bin/pip install rich

run:
	.venv/bin/python main.py $(MAP)
debug:
	.venv/bin/python3 -m pdb main.py $(MAP)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

