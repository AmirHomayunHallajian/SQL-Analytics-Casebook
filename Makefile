install:
	pip install -r requirements.txt

data:
	python scripts/generate_synthetic_data.py

db:
	python scripts/build_sqlite_db.py

queries:
	python scripts/run_all_queries.py

validate:
	python scripts/validate_outputs.py

test:
	pytest

all: data db queries validate

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
