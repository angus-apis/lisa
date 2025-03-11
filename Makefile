.PHONY: install main dummy_a dummy_b

# Target to install all requirements
install:
	@echo "Installing requirements..."
	poetry install

# Target to run the main FastAPI app
main: install
	@echo "Starting FastAPI main app..."
	poetry run uvicorn app.main:app --reload

# Target to run the first dummy server
dummy_a: install
	@echo "Starting Service A..."
	poetry run python tests/dummies/service_a.py

# Target to run the second dummy server
dummy_b: install
	@echo "Starting Service B..."
	poetry run python tests/dummies/service_b.py