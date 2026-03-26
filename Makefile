clean:
	rm -rf build/*
	rm -rf dist/*

build: clean
    uv build

dist: build
	twine upload dist/*

.PHONY: clean build dist
