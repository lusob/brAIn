.PHONY: run
run:
	uvicorn main:app --reload --port 9000

.PHONY: format
format:
	black .
	isort .

.PHONY: ingest
ingest:
	python3 ingest.py

.PHONY: help
help:
	@echo "Available targets:"
	@echo " run: Start the server"
	@echo " format: Format the code"
	@echo " ingest: Run the ingest script"
	@echo " help: Show this help message"
