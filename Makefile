.PHONY: install data db queries validate test all clean

install:
	pip install -r requirements.txt

data:
	python scripts/generate_synthetic_data.py

db: data
	python scripts/build_sqlite_db.py

queries: db
	python scripts/run_all_queries.py

validate: queries
	python scripts/validate_outputs.py

test: validate
	pytest

all: validate

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
