from epigraph.model import Node, Edge


def attr_str(attrs: dict) -> str:
    def fmt_val(v: str) -> str:
        return v if v.startswith("<") and v.endswith(">") else f'"{v}"'

    return " [" + ", ".join(f"{k}={fmt_val(v)}" for k, v in attrs.items()) + "]"


def to_dot(
    nodes: list[Node],
    edges: list[Edge],
    groups: dict[str, list[str]],
    styles: dict[str, dict[str, str]],
    nodesep: float,
    ranksep: float,
    rounded: bool = True,
    rankdir: str = "LR",
    labeldistance: float = 1.5,
    labelangle: float = 0.0,
) -> str:
    global_style = "filled"
    if rounded:
        global_style += ",rounded"
    lines = [
        "digraph G {",
        f"  rankdir={rankdir};",
        f"  nodesep={nodesep};",
        f"  ranksep={ranksep};",
        f'  node [shape=box, style="{global_style}", fontname="CMU Serif", fontsize=12];',
    ]

    node_dict = {node.id: node for node in nodes}
    assigned_nodes = set()

    for group_name, node_ids in groups.items():
        style = styles.get(group_name, {}).copy()
        rank = style.pop("rank", None)
        cluster = style.pop("cluster", "false").lower() in ("true", "yes", "1")

        if cluster:
            lines.append(f"  subgraph cluster_{group_name} {{")
            lines.append(f'    label="{group_name}";')
            lines.append("    style=dashed;")
        else:
            lines.append("  {")

        if rank:
            lines.append(f"    rank={rank};")

        for node_id in node_ids:
            if node_id not in node_dict:
                continue
            node = node_dict[node_id]
            assigned_nodes.add(node_id)
            node_attrs = {"label": node.label} | style | node.style

            style_val = node_attrs.get("style")

            if style_val is None:
                node_attrs["style"] = "filled,rounded" if rounded else "filled"
            elif isinstance(style_val, str) and rounded and "rounded" not in style_val:
                assert node_attrs["style"] is not None
                node_attrs["style"] += ",rounded"

            lines.append(f"    {node_id}{attr_str(node_attrs)};")

        lines.append("  }")

    for node in nodes:
        if node.id in assigned_nodes:
            continue
        attrs = {"label": node.label} | node.style
        lines.append(f"  {node.id}{attr_str(attrs)};")

    for edge in edges:
        attrs = {}
        if edge.label:
            attrs["label"] = edge.label
        attrs["labeldistance"] = str(labeldistance)
        attrs["labelangle"] = str(labelangle)
        if edge.style:
            attrs |= edge.style
        lines.append(f"  {edge.source} -> {edge.target}{attr_str(attrs)};")

    lines.append("}")
    return "\n".join(lines)
