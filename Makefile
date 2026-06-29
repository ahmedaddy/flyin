PYTHON = python
MAIN = main.py
MAP = map.txt

install:
		pip install -r requirements.txt

run:
		$(PYTHON) $(MAIN) $(MAP)

run-visual:
		$(PYTHON) $(MAIN) $(MAP) --visual

debug:
		$(PYTHON) -m pdb $(MAIN) $(MAP)

clean:
		find . -type d -name "__pycache__" -exec rm -rf {} +
		rm -rf .mypy_cache
		rm -rf .pytest_cache

lint:
		flake8 .
		mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs