.PHONY: all check help clean clean-pyc clean-build clean-bak clean-docs lint \
		lint-flake8 link-pylint reindent unix2dos dos2unix test test-all \
		covertest build docs docs-release docs-all install release

DONT_CHECK  = -i build -i dist -i downloads -i docs/_build -i tests/path.py -i test/coverage.py -i .tox

RELEASE		= latest

default: clean install check

all: clean check build docs test

check:
	python utils/check_sources.py --linelength 120 $(DONT_CHECK) .

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-bak - remove backup files"
	@echo "clean-gen - remove viol generated files"
	@echo "clean-docs - remove doc build artifacts"
	@echo "lint - check style with flake8 and pylint"
	@echo "lint-flake8 - check style with flake8"
	@echo "lint-pylint - check style with pylint"
	@echo "reindent - reindent all python files to four space tabs"
	@echo "unix2dos - convert all files to dos style line termination"
	@echo "dos2unix - convert all files to unix style line termination"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "docs-release - generate HTML, PDF, and EPUB documentation"
	@echo "install - invoke setup.py install to perform a developer installation"
	@echo "release - package up a release into the ./downloads directory"
	@echo "dist - package"

clean: clean-pyc clean-build clean-docs clean-gen clean-bak

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr downloads/
	rm -fr *.egg-info
	rm -f utils/*3.py*
	rm -fr htmlcov/

clean-bak:
	find . -name '*.bak' -exec rm -f {} +

clean-gen:

clean-docs:
	$(MAKE) -C docs clean

lint: lint-flake8 lint-pylint

lint-flake8:
	@echo "FLAKE 8 Results"
	@echo "==============="
	-@flake8 viol tests

lint-pylint:
	@echo "PYLINT Results"
	@echo "==============="
	@pylint --rcfile=utils/pylint.rc --disable=W viol tests

reindent:
	python utils/reindent.py -r -n .

unix2dos:
	python utils/unix2dos.py -r -n .

dos2unix:
	python utils/dos2unix.py -r -n .

test: build
	python -m unittest discover tests

test-all:
	tox

covertest: build
	coverage run --source viol setup.py test
	coverage report -m
	coverage html
	open htmlcov/index.html

build:
	@python setup.py build

install: build
	@python setup.py install

docs:
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

docs-release:
	$(MAKE) -C docs clean
	$(MAKE) -C docs RELEASE=$(RELEASE) html singlehtml latexpdf epub

dist: clean install docs-all
	python setup.py sdist
	python setup.py bdist_wheel
	pip install --download ./dist -r requirements.txt 
	mkdir -p downloads/downloads/htmlzip/$(RELEASE) downloads/downloads/pdf/$(RELEASE) downloads/downloads/epub/$(RELEASE) \
		downloads/downloads/src/$(RELEASE) downloads/docs/$(RELEASE)
	(cd docs/_build; tar cvf ../../downloads/downloads/htmlzip/$(RELEASE)/viol.html.tar ./html)
	gzip -f downloads/downloads/htmlzip/$(RELEASE)/viol.html.tar
	cp -prf docs/_build/html/* downloads/docs/$(RELEASE)
	tar cvf downloads/downloads/src/$(RELEASE)/viol.tar --exclude .svn --exclude .git --exclude build --exclude downloads \
		--exclude _build --exclude dist --exclude pre_install --exclude "*.pyc" .
	gzip -f downloads/downloads/src/$(RELEASE)/viol.tar
	cp -pf docs/_build/latex/viol.pdf downloads/downloads/pdf/$(RELEASE)/viol.pdf
	cp -pf docs/_build/epub/viol.epub downloads/downloads/epub/$(RELEASE)/viol.epub
	(cd downloads; tar cvf viol_pub_$(RELEASE).tar --exclude "viol_pub_*.tar" .)
	@echo "Local install:"
	@echo "-> pip install --no-index --find-links=./dist viol"

release-package: dist
	$(error Releasing to google sites not supported yet.)
	cp -pf dist/* /Volumes/ev_devops/packages
	rm -fr /Volumes/ev_devops/packages/simple
	(cd /Volumes/ev_devops; dir2pi -S packages)
	@echo "Public install:"
	@echo "-> pip install --allow-unverified --allow-all-external --no-index --find-links http://xxx/devops/packages viol"

release-pub: dist
	$(error Releasing to google sites not supported yet.)
	find /Volumes/ev_devops/viol -type d -name "$(RELEASE)" -print
	tar xvf downloads/viol_pub_$(RELEASE).tar -C /Volumes/ev_devops/viol

release-pypi: dist
	$(error Releasing to PyPi is not permitted.)
	python setup.py sdist upload
	python setup.py bdist_wheel upload

release: release-pub
	@echo "viol $(RELEASE) package uploaded to http://xxx/devops/packages."
	@echo "viol $(RELEASE) documentation and downloads uploaded to http://xxx/devops/viol/docs."
