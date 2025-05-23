import re
from typing import List, Tuple, Optional, Dict
from epigraph.model import Node, Edge


def parse_attrs(style: Optional[str]) -> dict:
    """Parse Graphviz-style [key=value, key2=value2] string into dict."""
    if not style:
        return {}
    attrs = {}
    for part in style.split(","):
        if "=" in part:
            key, val = part.strip().split("=", 1)
            val = val.strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            attrs[key.strip()] = val
    return attrs


def parse_dsl(
    text: str,
) -> Tuple[
    List[Node],
    List[Edge],
    Dict[str, List[str]],  # groups
    Dict[str, Dict[str, str]],  # styles
]:
    nodes: List[Node] = []
    edges: List[Edge] = []
    groups: Dict[str, List[str]] = {"core": []}
    styles: Dict[str, Dict[str, str]] = {}
    node_ids = set()

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # style block
        match = re.match(r"style\s+(\w+)\s+\[(.+?)\]", line)
        if match:
            style_name, attr_str = match.groups()
            styles[style_name] = parse_attrs(attr_str)
            continue

        # state declaration
        match = re.match(r"state\s+(\w+)(?:\s+\[(.+?)\])?", line)
        if match:
            node_id, attr_str = match.groups()
            attrs = parse_attrs(attr_str)
            label = attrs.pop("label", node_id)
            if label.startswith('"') and label.endswith('"'):
                label = label[1:-1]
            group = attrs.pop("group", "core")
            groups.setdefault(group, []).append(node_id)
            if group != "core":
                groups["core"].append(node_id)  # also add to default core group
            nodes.append(Node(id=node_id, label=label, style=attrs))
            node_ids.add(node_id)
            continue

        # labeled edge
        match = re.match(r"(\w+)\s+--(.+?)-->\s+(\w+)(?:\s+\[(.+?)\])?", line)
        if match:
            src, label, tgt, attr_str = match.groups()
            style = parse_attrs(attr_str)
            edges.append(Edge(source=src, target=tgt, label=label.strip(), style=style))
            continue

        # plain edge
        match = re.match(r"(\w+)\s+-->\s+(\w+)", line)
        if match:
            src, tgt = match.groups()
            edges.append(Edge(source=src, target=tgt))
            continue

    return nodes, edges, groups, styles
