window.DEMO = {
  repo: "product-matcher",
  title: "product-matcher",
  tagline: "Drop in two product lists, such as a supplier price list and your store catalog. Get the matching pairs with a score, a review list of close calls, and what is left unmatched on each side.",
  pkg: "product_matcher",
  packages: ["openpyxl", "numpy"],
  inputs: [
    { id: "a", label: "First list (CSV or XLSX)", accept: ".csv,.xlsx", sample: "samples/supplier.csv" },
    { id: "b", label: "Second list (CSV or XLSX)", accept: ".csv,.xlsx", sample: "samples/store.xlsx" },
  ],
  options: [
    { id: "auto", label: "Match without review at", type: "text", value: "0.92" },
    { id: "review", label: "Send to review from", type: "text", value: "0.75" },
  ],
  sampleNote: 'The sample is <a href="samples/supplier.csv">supplier.csv</a> and <a href="samples/store.xlsx">store.xlsx</a>: 40 synthetic products from invented brands, named differently in each list.<br>Matching uses rapidfuzz\'s own pure-Python implementation here, because rapidfuzz has no WebAssembly build. Same algorithms and scores, just slower than on a desktop.',
  python: `
import os
os.environ["RAPIDFUZZ_IMPL"] = "python"  # the C extension has no Pyodide build
from pathlib import Path
from product_matcher.cli import main as cli_main

def run(paths, opts):
    out = "/work/matches.xlsx"
    argv = [paths["a"][0], paths["b"][0], "-o", out]
    for k in ("auto", "review"):
        if opts.get(k, "").strip():
            argv += ["--" + k, opts[k].strip()]
    code, log = run_cli(cli_main, argv)
    if code != 0 or not Path(out).exists():
        return {"ok": False, "log": log, "sheets": [], "download": None}
    return {"ok": True, "log": log, "sheets": sheets_from_xlsx(out), "download": out}
`,
};
