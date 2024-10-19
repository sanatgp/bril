import json
from collections import defaultdict

def build_cfg(func):
    cfg = defaultdict(list)
    blocks = []
    current_block = []
    label_to_block = {}

    for instr in func['instrs']:
        if isinstance(instr, dict) and 'label' in instr:
            if current_block:
                blocks.append(current_block)
            current_block = [instr]
            label_to_block[instr['label']] = len(blocks)
        else:
            current_block.append(instr)

        if isinstance(instr, dict) and instr.get('op') in ['jmp', 'br']:
            blocks.append(current_block)
            current_block = []

    if current_block:
        blocks.append(current_block)

    for i, block in enumerate(blocks):
        last_instr = block[-1]
        if isinstance(last_instr, dict):
            if last_instr.get('op') in ['jmp', 'br']:
                for label in last_instr['labels']:
                    if label in label_to_block:
                        cfg[i].append(label_to_block[label])
            elif last_instr.get('op') != 'ret' and i + 1 < len(blocks):
                cfg[i].append(i + 1)
        cfg[i] 

    return cfg

def compute_dominators(cfg):
    entry = 0
    all_nodes = set(cfg.keys())
    dom = {node: all_nodes.copy() for node in all_nodes}
    dom[entry] = {entry}

    changed = True
    while changed:
        changed = False
        for node in cfg:
            predecessors = get_predecessors(cfg, node)
            if predecessors:
                new_dom = set.intersection(*(dom[pred] for pred in predecessors))
                new_dom.add(node)
            else:
                new_dom = {node}
            if new_dom != dom[node]:
                dom[node] = new_dom
                changed = True

    return dom

def get_predecessors(cfg, node):
    return [pred for pred, succs in cfg.items() if node in succs]

def build_dominator_tree(dom):
    idom = {}
    for node in dom:
        if node == 0:  
            idom[node] = None
        else:
            # Sort dominators by the size of their dominator sets in descending order
            sorted_doms = sorted(dom[node] - {node}, key=lambda x: len(dom[x]), reverse=True)
            idom[node] = next(d for d in sorted_doms if d != node)
    return idom

def compute_dominance_frontier(cfg, dom):
    df = defaultdict(set)
    for node in cfg:
        for succ in cfg[node]:
            runner = node
            while runner not in dom[succ]:
                df[runner].add(succ)
                runner = next(d for d in sorted(dom[runner] - {runner}) if d != runner)
    return df

def test_dominance(cfg, dom):
    entry = 0
    for node in cfg:
        if node == entry:
            continue
        for d in dom[node] - {node}:
            if d == entry:
                continue  # Do not remove the entry node
            #Temporarily remove dominator 'd' from the CFG
            modified_cfg = remove_node_from_cfg(cfg, d)
            # Check if node is still reachable from 'entry'
            if is_reachable(modified_cfg, entry, node):
                #if node is still reachable without d, then d does not dominate 'node'
                return False
    return True


def remove_node_from_cfg(cfg, node_to_remove):
    modified_cfg = {node: succs.copy() for node, succs in cfg.items() if node != node_to_remove}
    for succs in modified_cfg.values():
        if node_to_remove in succs:
            succs.remove(node_to_remove)
    return modified_cfg

def is_reachable(cfg, start, target):
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node == target:
            return True
        if node not in visited:
            visited.add(node)
            successors = cfg.get(node, [])
            stack.extend(successors)
    return False



def main():
    with open('input.json', 'r') as f:
        data = json.load(f)

    for func in data['functions']:
        print(f"Function: {func['name']}")

        cfg = build_cfg(func)
        print("\nControl Flow Graph:")
        print(json.dumps(cfg, indent=2))

        dom = compute_dominators(cfg)
        print("\nDominators:")
        print(json.dumps({k: sorted(list(v)) for k, v in dom.items()}, indent=2))

        idom = build_dominator_tree(dom)
        print("\nImmediate Dominators (Dominator Tree):")
        print(json.dumps(idom, indent=2))

        df = compute_dominance_frontier(cfg, dom)
        print("\nDominance Frontier:")
        print(json.dumps({k: sorted(list(v)) for k, v in df.items()}, indent=2))

        test_result = test_dominance(cfg, dom)
        print("\nDominance Test Result:")
        print(test_result)

if __name__ == "__main__":
    main()
