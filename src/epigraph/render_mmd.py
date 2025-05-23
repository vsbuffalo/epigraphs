"""
Render Mermaid flowchart from parsed epigraph structures.
"""

from __future__ import annotations
from typing import List, Dict
import json
from epigraph.parser import Node, Edge


def _q(text: str) -> str:
    """Quote a label if it contains whitespace."""
    return f'"{text}"' if any(c.isspace() for c in text) else text


def render_mmd(
    nodes: List[Node],
    edges: List[Edge],
    groups: Dict[str, List[str]],
    style: Dict,
    rankdir: str = "LR",
) -> str:
    out: list[str] = []

    # --- init block ---
    g = style.get("global", {})
    init = {"theme": g.get("theme", "neutral")}
    if g.get("math") == "katex":
        init["math"] = {"inlineMath": [["$", "$"]]}
    out.append(f"%%{{init: {json.dumps(init)} }}%%")
    out.append(f"flowchart {rankdir}")

    # --- classDef for node classes ---
    for cname, attrs in style.get("classes", {}).items():
        if attrs:
            kv = ",".join(f"{k}:{v}" for k, v in attrs.items() if k not in ("width"))
            if kv:
                out.append(f"classDef {cname} {kv};")

    # --- nodes --- 
    rounded = str(g.get("node.round", "")).lower() in ("true", "1", "yes")
    for n in nodes:
        shape = f"({_q(n.label)})" if rounded else f"[{_q(n.label)}]"
        out.append(f"{n.id}{shape}")
        if n.cls:
            out.append(f"class {n.id} {n.cls};")

    # --- edges and linkStyle ---
    edge_idx = 0
    for e in edges:
        label = f" -- {_q(e.label)} --> " if e.label else " --> "
        out.append(f"{e.source}{label}{e.target}")

        if e.cls and e.cls in style["classes"]:
            st = style["classes"][e.cls]
            kv = []
            if "stroke" in st:
                kv.append(f"stroke:{st['stroke']}")
            if "width" in st:
                kv.append(f"stroke-width:{st['width']}")
            if kv:
                out.append(f"linkStyle {edge_idx} {' '.join(kv)}")
        edge_idx += 1

    return "\n".join(out)
