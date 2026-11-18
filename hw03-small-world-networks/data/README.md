# Reference figure data

These extracts support the figures in the recorded small-world analysis.
`python hw03-small-world-networks/render_reference_figures.py` renders them
without rerunning the 10,000-node simulations.

- `ws_reference_crop_edges.csv` contains the 1,340 edges whose endpoints both
  lie in the 20 x 20 interior region of the recorded WS network. Coordinates
  are shifted to the range 0-19. The edges were extracted from the archived
  interactive Plotly export, whose SHA-256 is
  `c0c47f4c63df1b7c13f4b13c9aea57dd8ed9bfe4051c5a50a3d49a769f8b50b6`.
- `ws_reference_distance.csv` preserves the recorded, six-decimal shortest-
  path proportions, including the original self-pair normalization.
- `wsk_reference_rank_counts.csv` contains link-incidence counts recovered
  from the recorded six-decimal bin proportions. The counts sum to twice the
  recorded 27,598 edges, and each reconstructed proportion rounds back to the
  recorded value. The source results document has SHA-256
  `088d4ebe2723202d863ddb16116f39d656f3b4d0bdb711a9133f85a67e03f05f`.
