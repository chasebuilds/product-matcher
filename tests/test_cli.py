from pathlib import Path

from openpyxl import load_workbook

from benchmark.generate import generate, write
from product_matcher.cli import main


def test_cli_writes_sheets(tmp_path: Path, capsys: object) -> None:
    a, b = generate(5, 40)
    write(a, b, tmp_path / "a.csv", tmp_path / "b.xlsx")
    out = tmp_path / "m.xlsx"
    assert main([str(tmp_path / "a.csv"), str(tmp_path / "b.xlsx"), "-o", str(out)]) == 0
    wb = load_workbook(out)
    assert wb.sheetnames == ["Matched", "Review", "Unmatched a", "Unmatched b"]
    head = [c.value for c in wb["Matched"][1]]
    assert "price diff" in head and "reason" in head
    assert wb["Matched"].max_row > 10


def test_cli_errors(tmp_path: Path) -> None:
    assert main([str(tmp_path / "nope.csv"), str(tmp_path / "nope.csv")]) == 2
    (tmp_path / "x.csv").write_text("foo,bar\n1,2\n")
    assert main([str(tmp_path / "x.csv"), str(tmp_path / "x.csv")]) == 2
    assert main([str(tmp_path / "x.csv"), str(tmp_path / "x.csv"), "--name", "foo",
                 "--auto", "0.5", "--review", "0.9"]) == 2
