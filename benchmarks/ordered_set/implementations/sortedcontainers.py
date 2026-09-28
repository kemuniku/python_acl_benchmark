SOURCE = 'sortedcontainers'
LABEL = 'sortedcontainers.SortedSet'

from sortedcontainers import SortedSet

def run(data):
    initial, queries = data
    tree = SortedSet(initial)
    output = []
    for kind, x in queries:
        if kind == 0:
            tree.add(x)
        elif kind == 1:
            tree.discard(x)
        elif kind == 2:
            output.append(tree[x - 1] if x <= len(tree) else -1)
        elif kind == 3:
            output.append(tree.bisect_right(x))
        elif kind == 4:
            i = tree.bisect_right(x)
            output.append(tree[i - 1] if i else -1)
        else:
            i = tree.bisect_left(x)
            output.append(tree[i] if i < len(tree) else -1)
    return output
