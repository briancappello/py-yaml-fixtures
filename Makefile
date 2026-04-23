clean:
	rm -rf build/*
	rm -rf dist/*

build: clean
    poetry run build

dist: build
	twine upload dist/*

.PHONY: clean build dist
