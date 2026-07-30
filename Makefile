# SwissTeX -- Bauen und Pruefen
# Herkunft: Makefile-Gerippe aus SwissTeX 1.3.1 (Produktionsfork), auf v2.0
# angepasst -- DOCS sind die drei versionierten Referenzdokumente (kein
# Produktionsinhalt), TESTS die drei portierten Regressionsvorlagen unter
# tests/fixtures/. `check` deckt zusaetzlich den pytest-Baum und die harten
# sprachcheck-Pruefungen (S1/S7/S8) auf DOCS ab, nicht nur swisscheck.
DOCS  = swisstex-manual swisstex-demo acme-demo
TESTS = tests/fixtures/stress tests/fixtures/figure tests/fixtures/display
ALL   = $(DOCS) $(TESTS)

.PHONY: all check report clean dist

all: $(addsuffix .pdf,$(ALL))

# -output-directory haelt Vorlagen aus tests/fixtures/ dort, statt Baureste
# im Projektwurzelverzeichnis zu verstreuen. swisstex.cls als Abhaengigkeit
# gilt fuer beide Gruppen: eine Klassenaenderung macht auch die Fixtures neu.
%.pdf: %.tex swisstex.cls
	@xelatex -interaction=batchmode -output-directory=$(dir $@) $< > /dev/null 2>&1 || true
	@xelatex -interaction=batchmode -output-directory=$(dir $@) $< > /dev/null 2>&1 || true

check: all
	@fail=0; for f in $(ALL); do \
	  printf '  %-30s' $$f; \
	  if python3 swisscheck.py $$f.pdf --tex $$f.tex > /dev/null 2>&1; \
	    then echo 'bestanden'; else echo 'FEHLER'; fail=1; fi; \
	done; \
	echo; \
	fonts/.venv/bin/pytest tests/ -q || fail=1; \
	echo; \
	for f in $(DOCS); do \
	  printf '  sprachcheck %-24s' $$f; \
	  if python3 sprachcheck.py $$f.tex > /dev/null 2>&1; \
	    then echo 'bestanden'; else echo 'FEHLER'; fail=1; fi; \
	done; \
	if [ $$fail -eq 0 ]; then echo '\nalle Pruefungen bestanden'; \
	  else echo '\nPruefung fehlgeschlagen'; fi; exit $$fail

report: all
	@for f in $(ALL); do python3 swisscheck.py $$f.pdf --tex $$f.tex; done
	@for f in $(DOCS); do python3 sprachcheck.py $$f.tex -v; done

clean:
	@rm -f *.aux *.log *.out *.toc
	@rm -f tests/fixtures/*.aux tests/fixtures/*.log tests/fixtures/*.out \
	  tests/fixtures/*.pdf tests/fixtures/*.swisscheck

# Kein Produktionsinhalt: nur Klasse, Pruefwerkzeuge, die drei versionierten
# Referenzdokumente (samt PDF, vorgebaut) und die Referenzidentitaet acme.
dist: check clean
	@tar czf swisstex-dist.tar.gz swisstex.cls swisscheck.py sprachcheck.py \
	  Makefile README.md LICENSE swissidentity-acme.sty \
	  acme-logo.tex acme-logo.pdf \
	  $(addsuffix .tex,$(DOCS)) $(addsuffix .pdf,$(DOCS)) \
	  $(addsuffix .tex,$(TESTS))
	@echo 'swisstex-dist.tar.gz'
