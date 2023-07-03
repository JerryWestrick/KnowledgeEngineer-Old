import argparse

import graphviz as graphviz


def make_graph(process: dict, edges: dict):
    dot = graphviz.Digraph('ProcDataflow', comment='Dataflow of the process')
    dot.attr(rankdir='LR')

    with dot.subgraph(name='cluster_manual') as u:
        u.attr(style='filled', color='lightgrey')
        u.node_attr.update(style='filled', color='white', shape='record')
        u.attr(label='Manual Files')
        for e in (edges):
            edge = edges[e]
            if not edge['Dynamic']:
                u.node(edge['Name'], label=edge['Label'])

    with dot.subgraph(name='cluster_dynamic') as d:
        d.attr(style='filled', color='lightgrey')
        d.node_attr.update(style='filled', color='white', shape='record')
        d.attr(label='Dynamic Files')
        for e in sorted(edges):
            edge = edges[e]
            if edge['Dynamic']:
                d.node(edge['Name'], label=edge['Label'])

    # with dot.subgraph(name='cluster_steps') as s:
    #     s.attr(style='filled', color='lightgrey')
    #     s.node_attr.update(style='filled', color='white')
    #     s.attr(label='Steps')
    for name in process:
        step = process[name]
        dot.node(step['Name'], label=step['Label'])

    for name in process:
        step = process[name]
        for e in step['Reading']:
            dot.edge(e, step['Name'])

        for e in step['Writing']:
            dot.edge(step['Name'], e)

    dot.render('ProcDataflow.dot', view=True,  format='svg')


def main():
    parser = argparse.ArgumentParser(
        prog='main.py',
        description='Draw a Graph of the Dataflow of the process',
        epilog='good luck'
    )
    parser.add_argument('--skip_document', nargs='+', help='Do not draw Document')
    parser.add_argument('--step', type='str', help='Draw diagram for this step')

    args = parser.parse_args()

    step_no = 0
    edge_no = 0
    nodes = {}
    edges = {}

    with open('Flow.txt') as f:
        lines = f.readlines()

    last = None
    for line in lines:
        front_len = len('[2023-06-28 15:50:07] STEP ')
        (action, name) = line[front_len:].strip().split('>>')
        doc_label = name.split('/')[-1]
        step_label = doc_label.split('.')[-2]  # Drop extension
        dynamic = name.startswith('Dynamic')

        # New Step?
        if action == 'Starting':
            # We are finished with last one...
            if last:
                nodes[last['Name']] = last
                last = None

            # okay start with new one
            step_name = f"Step_{step_no}"
            step_no += 1
            last = {'Name': step_name,
                    'Label': step_label,
                    'Writing': set(),
                    'Reading': set(),
                    }
        else:
            # inputs and outputs
            if name in args.skip_document:
                continue

            if doc_label not in edges:
                doc_name = f"Doc_{edge_no}"
                edge_no += 1
                edges[doc_label] = {'Name': doc_name, 'Label': doc_label, 'Dynamic': dynamic}
            else:
                doc_name = edges[doc_label]['Name']

            last[action].add(doc_name)

    # We are finished with last one...
    if last:
        nodes[last['Name']] = last
    make_graph(nodes, edges)


if __name__ == '__main__':
    main()
