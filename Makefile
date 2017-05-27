TEST_PATH=./popular

.PHONY: clean
clean:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '__pycache__' -exec rm -rf {} +
	rm -rf .cache

.PHONY: tests
tests: clean
	py.test $(TEST_PATH)
