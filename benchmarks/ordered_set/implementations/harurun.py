SOURCE = 'harurun'
LABEL = 'lif4635/harurun-s-library (library_codex / TreapSet)'

from library_codex.ordered_set.TreapSet import TreapSet

def run(data):
    initial, queries = data
    tree = TreapSet(initial)
    output = []
    for kind, x in queries:
        if kind == 0:
            tree.add(x)
        elif kind == 1:
            tree.discard(x)
        elif kind == 2:
            output.append(tree.kth(x - 1) if x <= len(tree) else -1)
        elif kind == 3:
            output.append(tree.bisect_right(x))
        elif kind == 4:
            output.append(tree.le(x, -1))
        else:
            output.append(tree.ge(x, -1))
    return output
