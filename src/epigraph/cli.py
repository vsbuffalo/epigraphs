import typer
from pathlib import Path
from graphviz import Source
from epigraph.parser import parse_dsl
from epigraph.render_dot import to_dot

app = typer.Typer()


@app.command()
def render(
    spec: Path = typer.Argument(..., help="Path to DSL model file"),
    out: Path = typer.Option("diagram.svg", "--out", "-o", help="Output SVG file"),
    engine: str = typer.Option("dot", help="Graphviz engine to use"),
    view: bool = typer.Option(False, "--view", help="Open SVG after rendering"),
    rankdir: str = typer.Option("LR", "--rankdir", help="Graphviz rank direction"),
    nodesep: float = typer.Option(0.25, "--nodesep", help="Graphviz nodesep"),
    ranksep: float = typer.Option(0.2, "--ranksep", help="Graphviz ranksep"),
    rounded: bool = typer.Option(True, "--rounded", help="Use rounded corners"),
):
    """Render a flow diagram from a DSL spec."""
    text = spec.read_text()

    # Unpack full parser result (includes groups and styles)
    nodes, edges, groups, styles = parse_dsl(text)

    # Pass groups and styles to to_dot
    dot_source = to_dot(
        nodes,
        edges,
        groups,
        styles,
        rankdir=rankdir,
        nodesep=nodesep,
        ranksep=ranksep,
        rounded=rounded,
    )

    src = Source(dot_source, format="svg", engine=engine)
    output_path = src.render(outfile=str(out), cleanup=True)

    typer.echo(f"✅ Diagram written to {output_path}")
    if view:
        import webbrowser

        webbrowser.open(str(out.resolve()))


if __name__ == "__main__":
    app()
