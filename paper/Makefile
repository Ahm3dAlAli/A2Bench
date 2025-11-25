# Makefile for A²-Bench NeurIPS paper

PAPER = a2bench_neurips
LATEX = pdflatex
BIBTEX = bibtex

.PHONY: all clean figures

all: $(PAPER).pdf

$(PAPER).pdf: $(PAPER).tex references.bib
	$(LATEX) $(PAPER)
	$(BIBTEX) $(PAPER)
	$(LATEX) $(PAPER)
	$(LATEX) $(PAPER)

figures:
	cd ../experiments && python generate_mock_results.py
	cd ../experiments && python generate_figures.py
	@echo "Figures generated in ../experiments/figures/"

clean:
	rm -f $(PAPER).aux $(PAPER).bbl $(PAPER).blg $(PAPER).log $(PAPER).out $(PAPER).pdf

view: $(PAPER).pdf
	@if command -v open > /dev/null; then \
		open $(PAPER).pdf; \
	elif command -v xdg-open > /dev/null; then \
		xdg-open $(PAPER).pdf; \
	elif command -v evince > /dev/null; then \
		evince $(PAPER).pdf; \
	else \
		echo "PDF viewer not found. Please open $(PAPER).pdf manually."; \
	fi

help:
	@echo "Available targets:"
	@echo "  all      - Build the paper (default)"
	@echo "  figures  - Generate all figures"
	@echo "  clean    - Remove generated files"
	@echo "  view     - Open the PDF"
	@echo "  help     - Show this help"
