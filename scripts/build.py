"""Validate a diagram timeline and build an offline editable SVG animation."""
import argparse
import copy
import json
import math
from pathlib import Path


def validate(data):
    if not isinstance(data, dict):
        raise ValueError('输入必须是 JSON 对象')
    if not isinstance(data.get('title'), str) or not data['title'].strip():
        raise ValueError('需要 title')
    nodes, edges, steps = data.get('nodes'), data.get('edges'), data.get('steps')
    if not isinstance(nodes, list) or not 1 <= len(nodes) <= 100:
        raise ValueError('nodes 必须包含 1–100 个节点')
    if not isinstance(edges, list) or len(edges) > 200:
        raise ValueError('edges 最多 200 条')
    if not isinstance(steps, list) or not 1 <= len(steps) <= 100:
        raise ValueError('steps 必须包含 1–100 个步骤')
    ids = set()
    for node in nodes:
        if not isinstance(node.get('id'), str) or not node['id'] or node['id'] in ids:
            raise ValueError('节点 id 必须唯一且非空')
        ids.add(node['id'])
        if not isinstance(node.get('label'), str):
            raise ValueError('节点需要 label')
        for key, maximum in [('x', 940), ('y', 560)]:
            v = node.get(key)
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or not 0 <= v <= maximum:
                raise ValueError(f'节点 {key} 超出画布范围')
    edge_ids = set()
    for edge in edges:
        if not isinstance(edge.get('id'), str) or not edge['id'] or edge['id'] in edge_ids:
            raise ValueError('连线 id 必须唯一且非空')
        edge_ids.add(edge['id'])
        if edge.get('from') not in ids or edge.get('to') not in ids:
            raise ValueError('连线指向不存在的节点')
        if edge['from'] == edge['to']:
            raise ValueError('首版不支持自环；多个节点之间可以成环')
    total = 0
    for step in steps:
        d = step.get('duration')
        if isinstance(d, bool) or not isinstance(d, (int, float)) or not math.isfinite(d) or not .2 <= d <= 60:
            raise ValueError('步骤时长必须在 0.2–60 秒')
        total += d
        if not isinstance(step.get('caption'), str):
            raise ValueError('步骤需要 caption')
        for key, valid in [('nodes', ids), ('edges', edge_ids)]:
            if not isinstance(step.get(key), list) or any(x not in valid for x in step[key]):
                raise ValueError(f'步骤引用不存在的 {key}')
    if total > 1800:
        raise ValueError('总时长不能超过 30 分钟')
    return copy.deepcopy(data)


def step_at(data, seconds):
    """Return step index at a clamped timeline position; boundaries enter next step."""
    elapsed = 0
    for i, step in enumerate(data['steps']):
        elapsed += step['duration']
        if seconds < elapsed:
            return i
    return len(data['steps']) - 1


def build(data):
    data = validate(data)
    assets = Path(__file__).resolve().parents[1] / 'assets'
    payload = json.dumps(data, ensure_ascii=False, allow_nan=False).replace('<', '\\u003c')
    return (assets / 'template.html').read_text().replace('/*__STYLE__*/', (assets / 'style.css').read_text()).replace('/*__SCRIPT__*/', (assets / 'app.js').read_text()).replace('__DATA__', payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        html = build(json.loads(args.input.read_text()))
    except (ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html)
    print(args.output.resolve())


if __name__ == '__main__':
    main()
