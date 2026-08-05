# Experiment result data

`experiment-results.json` is the source of truth for every quantitative result
shown on the JoyAI-RA 0.5 project page.

The values were extracted from the latest Overleaf archive, checked against the
individual source figures, and checked again against the final compiled paper.
The archive and final-paper SHA-256 hashes are stored with the data.

`scripts/generate_result_charts.py` validates reported averages before rendering
the SVG charts. Validation-loss curves are not reconstructed because the paper
does not provide their underlying numeric point series.
