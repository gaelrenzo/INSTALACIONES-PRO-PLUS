PYTHON ?= python3

.PHONY: install test test-tools test-renzo aquiles renzo clean

install:
	$(PYTHON) -m pip install -r requirements.txt

test:
	$(PYTHON) -m pytest -q herramientas/cotizacion/tests proyectos/renzo/tests

test-tools:
	$(PYTHON) -m pytest -q herramientas/cotizacion/tests

test-renzo:
	$(PYTHON) -m pytest -q proyectos/renzo/tests

aquiles:
	$(PYTHON) herramientas/pipeline_automatizado.py --proyecto aquiles

renzo:
	$(PYTHON) herramientas/pipeline_automatizado.py --proyecto renzo

clean:
	rm -rf build
