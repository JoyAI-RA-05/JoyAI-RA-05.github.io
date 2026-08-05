# Experiment result data

`experiment-results.json` is the source of truth for every quantitative result
shown on the JoyAI-RA 0.5 project page.

The values were extracted from the latest Overleaf archive, checked against the
individual source figures, and checked again against the final compiled paper.
The archive and final-paper SHA-256 hashes are stored with the data.

`scripts/generate_result_charts.py` validates reported averages before rendering
the SVG charts. Validation-loss curves are not reconstructed because the paper
does not provide their underlying numeric point series.

## Known source-figure discrepancy

The latest teaser source (`images/JoyRA05_teaser_final.pdf`) labels the LAC-WM
fractions as 15%, 20%, and 100%. The experiment section, the dedicated
`images/scaling_chart.pdf`, and the underlying reported values consistently use
10%, 25%, and 100%. Web-native result charts therefore use 10%, 25%, and 100%;
the teaser remains an unmodified export of the latest paper figure.
