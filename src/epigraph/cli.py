from __future__ import annotations
from pathlib import Path
import json5 as json
import tempfile, typer
import subprocess
from epigraph.parser import parse_dsl
from epigraph.render_mmd import render_mmd

app = typer.Typer()

def _merge_style(base: dict, extra: dict) -> dict:
    merged = {
        "global":  {**base.get("global",  {}), **extra.get("global",  {})},
        "classes": {**base.get("classes", {})}
    }
    for cls, attrs in extra.get("classes", {}).items():
        merged["classes"].setdefault(cls, {}).update(attrs)
    return merged


def assert_mmdc() -> None:
    """Check if mmdc is installed."""
    try:
        subprocess.run(["mmdc", "--version"], check=True, capture_output=True)
    except FileNotFoundError:
        raise RuntimeError("mmdc not found. Please install mermaid-cli: npm install -g @mermaid-js/mermaid-cli")

@app.command()
def render(
    spec: Path  = typer.Argument(..., help="Input .flow file"),
    style: Path | None = typer.Option(None, "--style", "-s", help="External .style.json"),
    out:   Path = typer.Option("diagram.mmd", "--out", "-o", help="Output .mmd or .pdf"),
    rankdir: str = typer.Option("LR", help="Layout direction"),
    pdf: bool = typer.Option(False, "--pdf", "-p", help="Export PDF via mmdc --pdfFit"),
    view: bool = typer.Option(False, help="Open result after rendering"),
) -> None:
    """Render Mermaid (.mmd) or directly to PDF."""
    nodes, edges, groups, internal_style = parse_dsl(spec)

    if style:
        internal_style = _merge_style(internal_style, json.loads(style.read_text()))

    mmd = render_mmd(nodes, edges, groups, internal_style, rankdir)

    # ── PDF path ────────────────────────────────────────────────────
    if pdf or out.suffix.lower() == ".pdf":
        assert_mmdc()
        with tempfile.NamedTemporaryFile("w+", suffix=".mmd", delete=False) as tmp:
            tmp.write(mmd); tmp.flush()
            pdf_path = out.with_suffix(".pdf")
            cmd = ["mmdc", "-i", tmp.name, "-o", str(pdf_path), "--pdfFit"]
            subprocess.run(cmd, check=True)
        typer.echo(f"✅ PDF written to {pdf_path}")
        if view:
            import webbrowser; webbrowser.open(pdf_path.resolve().as_uri())
        return

    # ── .mmd path ───────────────────────────────────────────────────
    out.write_text(mmd)
    typer.echo(f"✅ Mermaid written to {out}")
    if view:
        import webbrowser; webbrowser.open(out.resolve().as_uri())

if __name__ == "__main__":
    app()
