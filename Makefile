PY = $(wildcard velat/*.py)
SCORIA = install_stamp test_buffer_velat

install_stamp: $(PY)
	python setup.py install
	touch install_stamp

install: install_stamp
.PHONY: install

test_buffer_%: %
	nosetests  --with-doctest --with-coverage --cover-package=$< $< 2> $@
.IGNORE: test_buffer_velat

test: install test_buffer_velat
	cat test_buffer_velat
.PHONY: test

clean:
	rm $(SCORIA)
.PHONY: clean
.IGNORE: clean
