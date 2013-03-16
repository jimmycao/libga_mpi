libga_mpi.pdf: libga_mpi.tex
	pdflatex libga_mpi.tex
	bibtex libga_mpi
	pdflatex libga_mpi.tex
	pdflatex libga_mpi.tex
clean: 
	-@rm -rf *.pdf 2>/dev/null || true
	-@rm -rf *.aux 2>/dev/null || true
	-@rm -rf *.log 2>/dev/null || true
	-@rm -rf *.bbl 2>/dev/null || true
	-@rm -rf *.blg 2>/dev/null || true
	-@rm -rf *.toc 2>/dev/null || true
	-@find . -name "*~" -delete
	@echo "clean done."