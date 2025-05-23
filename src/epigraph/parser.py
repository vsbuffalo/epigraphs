import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

@dataclass
class Node:
    id: str
    label: str
    cls: Optional[str] = None
    attrs: Dict[str, str] = field(default_factory=dict)

@dataclass
class Edge:
    source: str
    target: str
    label: Optional[str] = None
    cls: Optional[str] = None
    attrs: Dict[str, str] = field(default_factory=dict)

def parse_dsl(text_or_path: str | Path) -> Tuple[List[Node], List[Edge], Dict[str, List[str]], Dict]:
    if isinstance(text_or_path, Path):
        text = text_or_path.read_text()
    else:
        text = text_or_path

    nodes = []
    edges = []
    groups = {}
    style_lines = []
    in_style = False
    depth = 0

    _attr = re.compile(r'(\w+)\s*=\s*("[^"]*"|\S+)')
    _state = re.compile(r"state\s+(\w+)(?:\s+\[(.+?)\])?")
    _edge_lbl = re.compile(r"(\w+)\s+--\s*(.+?)\s*-->\s*(\w+)(?:\s+\[(.+?)\])?")
    _edge_plain = re.compile(r"(\w+)\s*-->\s*(\w+)(?:\s+\[(.+?)\])?")

    for raw in text.splitlines():
        line = raw.rstrip()
        if not in_style and line.lstrip().startswith("style"):
            after = line.split("{", 1)[1] if "{" in line else ""
            style_lines.append(after)
            in_style = True
            depth = 1
            continue
        if in_style:
            depth += line.count("{") - line.count("}")
            if depth == 0:
                in_style = False
                continue
            style_lines.append(line)
            continue
        code = line.split("#", 1)[0].strip()
        if not code:
            continue
        if m := _state.match(code):
            nid, attr_str = m.groups()
            attrs = {k: v.strip('"') for k, v in _attr.findall(attr_str or "")}
            label = attrs.pop("label", nid)
            cls = attrs.pop("class", None)
            grp = attrs.pop("group", None)
            if grp:
                groups.setdefault(grp, []).append(nid)
            nodes.append(Node(nid, label, cls, attrs))
            continue
        if m := _edge_lbl.match(code):
            s, lbl, t, attr_str = m.groups()
            attrs = {k: v.strip('"') for k, v in _attr.findall(attr_str or "")}
            edges.append(Edge(s, t, lbl, attrs.pop("class", None), attrs))
            continue
        if m := _edge_plain.match(code):
            s, t, attr_str = m.groups()
            attrs = {k: v.strip('"') for k, v in _attr.findall(attr_str or "")}
            edges.append(Edge(s, t, None, attrs.pop("class", None), attrs))
            continue
        raise ValueError(f"bad line: {code}")

    for n in nodes:
        groups.setdefault("core", []).append(n.id)

    style = {"global": {}, "classes": {}}
    if style_lines:
        cleaned = []
        for ln in style_lines:
            ln = ln.strip()
            if "#" in ln:
                ln = ln.split("#", 1)[0].rstrip()
            if ln:
                cleaned.append(ln)
        s = "\n".join(cleaned)
        if not s.startswith("{"): s = "{" + s
        if not s.endswith("}"): s += "}"
        style = json.loads(s)

    return nodes, edges, groups, style
