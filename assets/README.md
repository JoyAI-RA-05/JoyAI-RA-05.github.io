# Asset provenance

## Brand asset

- `joyai-wordmark.png` is the JoyAI wordmark used by the public JoyAI-RA 0.1
  project page (`https://joyra.s3.cn-north-1.jdcloud-oss.com/assets/logo.f0f088d3.png`),
  downloaded on 2026-08-05 and retained at its original dimensions. Its bytes
  exactly match `ppt/media/image1.png` in the desktop source deck
  `JoyRA05_teaser_final.pptx`; the hero crops its rainbow mark using the crop
  recorded in that deck.
- `joyra05-ppt-mascot-source.png` is `ppt/media/image2.png` from
  `JoyRA05_teaser_final.pptx`. The hero uses the deck's original crop to show
  only the mascot portion of the source lockup.
- `joyai-ra-reference-title.png` is the transparent title lockup from the same
  public project page (`https://joyra.s3.cn-north-1.jdcloud-oss.com/assets/logo2.png`).
  It is retained as a legacy source asset but is no longer used by the 0.5
  page after switching the hero to the supplied PowerPoint assets.

## Paper figures

The paper-derived PNGs below were refreshed on 2026-08-05 from the latest
downloaded Overleaf archive, `JoyAI_RA_0_5 (2).zip` (SHA-256
`acafb9d8a11a6e59b734554960d133066b70285a2054422f868924418d074a14`).
Each PDF was rasterized as a single-page PNG at 144 DPI without changing its
content or aspect ratio.

For the web presentation, two rasterized figures were cropped on 2026-08-05 to
remove only their surrounding white page margins. `joyra05-overview.png` uses
the source rectangle `x=1, y=113, width=1871, height=792`, and
`experiment-setting.png` uses `x=81, y=86, width=1741, height=837`. Neither
figure was resized, reconstructed, or otherwise altered.

| Web asset | Overleaf source | Source SHA-256 |
| --- | --- | --- |
| `joyra05-overview.png` | `images/JoyRA05_teaser_final.pdf` | `509ea47c4bf8f67eaa346cc350c4651a6554f39e4f50a5bd12237289bb302043` |
| `data-composition.png` | `images/joyra05_Data.pdf` | `9c0ccc4491b468e22f25e040473a585bd321bd9ef3b711fcba16be82c592a682` |
| `data-pipeline.png` | `images/data_pipe.pdf` | `fbe85e4f169a30804deb67a4b78ba10608499686bae08e920240b5024da5ed5c` |
| `architecture.png` | `images/framework.pdf` | `5bdee18009e4a1ab512d34f1491d3ccfa1fd8b2957895d13cf8cc6508b7d5d1d` |
| `experiment-setting.png` | `images/exp-setting.pdf` | `0c1559dadfb0762c28694f2044b266be6d9ab9a79cf062f2c64dbc46b22ae697` |
| `embedding-visualization.png` | `images/emb_vis_overlay_with_frames.pdf` | `2963dd1da1b1536138d5a6ddb03f67b7df1b82464003a30b5a2903837fa22b04` |
| `rl-inner-outer-loop.png` | `images/RL_inner_outer_loop5.pdf` | `972450d22b0098905910a94ab952d0e2ee68173335cbae1a2fe070156180fa5a` |
| `human-scaling-lacwm.png` | `images/scaling_chart.pdf` | `cc699f960ad3d3c656f49f7427a10e210a1be86d3277f5a6f34c2fe632fd5ac8` |
| `human-scaling-policy.png` | `images/retarget5_pct_val_loss_success_combined_arial_shifted_desk_new.pdf` | `9bb90e895f4d142635857e5ad98d0d3c29a811ea8a35d8618c6499765c303eaf` |

`human-scaling-validation-loss.png` is a 288-DPI crop of the validation-loss
panel and its original legend from
`images/retarget5_pct_val_loss_success_combined_arial_shifted_desk_new.pdf`.
The curve geometry, markers, labels, and legend are unchanged; only the other
panel and surrounding page area were removed.

The matching final paper is `JoyAI_RA_0_5 (4).pdf` (SHA-256
`ae56e148691a3d0306e3d896f9cc95d955075b7f8d0c8e9118aa7e285056563b`).

## Generated result charts

- Files: `result-main-alignment.svg`, `result-human-scaling.svg`,
  `result-human-scaling-lacwm.svg`, `result-human-scaling-policy.svg`, and
  `result-rl.svg`
- Source values: the latest Overleaf archive and final paper listed above
- Generator: `scripts/generate_result_charts.py`
- Machine-readable source: `data/experiment-results.json`
- Audit notes: `data/README.md`
- Role: web-native redraws of the main, scaling, and reinforcement-learning
  results using the JoyAI-RA 0.1 project-page chart palette
- Output: editable vector SVG with text preserved as text
