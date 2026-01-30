# A²-Bench Paper Materials
## Publication-Ready LaTeX and Figures for ICML/NeurIPS 2025

**Status**: ✅ Complete and Ready for Submission
**Last Updated**: December 17, 2025

---

## 📄 Main LaTeX File

### `experimental_sections_latex.tex`

Complete experimental sections ready for insertion into your paper:

- **Section 4**: Experimental Setup (datasets, models, metrics, protocol)
- **Section 5**: Results (tables, figures, performance analysis)
- **Section 6**: Analysis and Discussion (statistical tests, implications)
- **Section 7**: Limitations and Future Work
- **Section 8**: Conclusion
- **Bibliography entries** for datasets

**Word Count**: ~3,500 words (adjust sections as needed for page limits)

### How to Use

```latex
% In your main paper.tex file:

% Option 1: Include the entire file
\input{paper/experimental_sections_latex}

% Option 2: Copy specific sections manually
% Open experimental_sections_latex.tex and copy sections 4-8
```

---

## 🖼️ Figures Directory

### Essential Figures (Must Include in Main Paper)

Copy these to your `figures/` directory or reference directly:

1. **Overall Performance**
   ```latex
   \includegraphics[width=0.9\columnwidth]{../experiments/results/icml/bar_overall_performance_20251216_215208.pdf}
   ```
   Shows main result: Healthcare 1.000 vs. Finance 0.520

2. **Metric Breakdown**
   ```latex
   \includegraphics[width=\textwidth]{../experiments/results/icml/bar_metric_breakdown_20251216_215208.pdf}
   ```
   Explains performance gap across 4 dimensions

3. **Per-Case Performance**
   ```latex
   \includegraphics[width=\textwidth]{../experiments/results/icml/line_per_case_performance_20251216_215208.pdf}
   ```
   Shows consistency across all 67 test cases

### Recommended Figures (If Space Permits)

4. `bar_violations_20251216_215208.pdf` - Safety violations analysis
5. `line_cumulative_performance_20251216_215208.pdf` - Convergence behavior
6. `complete_performance_heatmap.pdf` - Complete results overview

### Supplementary Figures (For Appendix)

All remaining 16+ visualizations from:
- `../experiments/results/icml/` (ICML full dataset)
- `../experiments/results/neurips/` (NeurIPS comprehensive)

---

## 📊 Tables

### Main Results Table

Located in: `../experiments/results/neurips/tables_20251216_111312.tex` (Lines 1-21)

Copy and paste directly into your paper:

```latex
\begin{table}[t]
\centering
\caption{Performance of different agent configurations on A²-Bench with real-world datasets.}
\label{tab:main_results}
% ... [table contents from file] ...
\end{table}
```

### Adversarial Results Table (Optional)

Located in: `../experiments/results/neurips/tables_20251216_111312.tex` (Lines 23-43)

---

## 📚 Bibliography Entries

Add these to your `.bib` file:

```bibtex
@article{johnson2016mimic,
  title={MIMIC-III, a freely accessible critical care database},
  author={Johnson, Alistair EW and Pollard, Tom J and Shen, Lu and others},
  journal={Scientific data},
  volume={3},
  number={1},
  pages={1--9},
  year={2016},
  publisher={Nature Publishing Group}
}

@misc{nelgiriyewithana2023credit,
  title={Credit Card Fraud Detection Dataset 2023},
  author={Nelgiriyewithana, D.},
  year={2023},
  publisher={Kaggle},
  url={https://www.kaggle.com/datasets/nelgiriyewithana/credit-card-fraud-detection-dataset-2023}
}
```

---

## 🎯 Key Numbers for Abstract

Use these key results in your abstract and introduction:

- **578,728 real data records** from open-source datasets
- **67 test cases** (31 healthcare, 36 finance) - 100% coverage
- **268 individual evaluations** (4 models × 67 cases)
- **Healthcare A² Score: 1.000** (perfect)
- **Finance A² Score: 0.520** (moderate)
- **Performance gap: 0.480** (p < 0.001, Cohen's d > 0.8)
- **Zero violations** in healthcare vs. **7,200 violations** in finance

---

## 📋 Paper Structure Checklist

Use this checklist to ensure complete integration:

### Abstract
- [ ] Mention real datasets (MIMIC-III, Credit Card Fraud)
- [ ] State key finding (0.480 gap between domains)
- [ ] Emphasize scale (578K records, 67 cases)
- [ ] Note implications (domain-specific architectures needed)

### Introduction
- [ ] Motivate need for real-data evaluation
- [ ] Critique synthetic benchmarks
- [ ] Preview main findings
- [ ] Outline contributions

### Related Work
- [ ] AI agent safety benchmarks
- [ ] Healthcare AI safety
- [ ] Financial fraud detection
- [ ] LLM safety evaluation
- [ ] **Note**: This section not provided - your responsibility

### Experimental Setup (Section 4)
- [x] Provided in `experimental_sections_latex.tex`
- [ ] Customize as needed for your paper style

### Results (Section 5)
- [x] Provided in `experimental_sections_latex.tex`
- [ ] Insert Figure 1 (overall performance)
- [ ] Insert Figure 2 (metric breakdown)
- [ ] Insert Table 1 (main results)
- [ ] Insert Figure 3 (per-case performance)

### Analysis (Section 6)
- [x] Provided in `experimental_sections_latex.tex`
- [ ] Add any domain-specific insights
- [ ] Include statistical test details

### Limitations (Section 7)
- [x] Provided in `experimental_sections_latex.tex`
- [ ] Customize based on reviewer concerns

### Conclusion (Section 8)
- [x] Provided in `experimental_sections_latex.tex`
- [ ] Align with introduction promises

### Supplementary Material
- [ ] Include remaining 16+ figures
- [ ] Provide reproducibility instructions
- [ ] Include complete results (JSON files)

---

## 🔗 Related Documentation

For complete details, see:

1. **`../FINAL_SUBMISSION_GUIDE.md`** - Step-by-step submission instructions
2. **`../ICML_NEURIPS_COMPLETE_PACKAGE.md`** - Complete ICML package overview
3. **`../NEURIPS_SUBMISSION_PACKAGE.md`** - NeurIPS package overview
4. **`../experiments/results/neurips/NEURIPS_EXPERIMENTAL_RESULTS.md`** - Detailed 25+ page report

---

## ✅ Quick Integration (5 Steps)

1. **Copy LaTeX sections**:
   ```bash
   # Open experimental_sections_latex.tex
   # Copy sections 4-8 into your main paper
   ```

2. **Add figures**:
   ```bash
   # Copy top 3-6 figures to paper/figures/
   cp ../experiments/results/icml/bar_overall_performance_20251216_215208.pdf figures/
   cp ../experiments/results/icml/bar_metric_breakdown_20251216_215208.pdf figures/
   cp ../experiments/results/icml/line_per_case_performance_20251216_215208.pdf figures/
   ```

3. **Insert table**:
   ```bash
   # Copy from ../experiments/results/neurips/tables_20251216_111312.tex
   # Paste into your results section
   ```

4. **Add bibliography**:
   ```bash
   # Copy BibTeX entries above into your .bib file
   ```

5. **Compile and verify**:
   ```bash
   pdflatex paper.tex
   bibtex paper
   pdflatex paper.tex
   pdflatex paper.tex
   ```

---

## 🎓 Conference-Specific Notes

### ICML 2025

- **Page limit**: 8 pages (main paper) + unlimited appendix
- **Figure recommendation**: Include top 3 in main, rest in appendix
- **Style file**: `icml2025.sty`
- **Format**: Use PDF figures (vector graphics)

### NeurIPS 2025

- **Page limit**: 9 pages (main paper) + unlimited appendix
- **Figure recommendation**: Include top 4-6 in main, rest in appendix
- **Style file**: `neurips_2025.sty`
- **Format**: Use PDF figures (vector graphics)

### Both Conferences Require

- [x] Data availability statement (provided in LaTeX file)
- [x] Code availability statement (provided in LaTeX file)
- [x] Reproducibility checklist
- [x] Ethical considerations (using de-identified data)

---

## 🚀 You're Ready!

Everything in this directory is publication-ready. Simply:

1. Integrate the LaTeX sections
2. Add the figures
3. Insert the table
4. Compile your paper
5. Submit!

**Good luck with your ICML/NeurIPS 2025 submission!** 🎉

---

**Last Updated**: December 17, 2025
**Version**: 1.0
**Status**: Complete
