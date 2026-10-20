# Chart-01 first failing evidence

The new Chart structural command returned `1 file / 2 failed`: safe bounded bar JSON had no `canvas[data-poc-chart="rendered"]`, while a `formatter`-bearing JSON value remained `inert` rather than exact `local-fallback`.

The corresponding Playwright SSR command failed before hydration because the output contained only `code[data-poc-inert="chart"]`, not the required Canvas marker. Its screenshot, error context and trace are retained under `playwright-test-results/chart-isolated-Chart-01-re-83fe5-network-download-or-residue/`.

No ECharts, production consumer, Canvas drawing, external request, navigation or download was invoked by this failing path.
