prog = icebox

# colours
RED = \033[0;31m
NC  = \033[0m

all: tests build install clean

tests: FORCE
	python -m unittest tests/test_*

build: 
	pyinstaller $(prog).py --hidden-import coolname.data --onefile

install: dist/$(prog)
	sudo cp dist/$(prog) /usr/local/bin/$(prog)

clean:
	rm -rf build dist $(prog).spec

FORCE:
