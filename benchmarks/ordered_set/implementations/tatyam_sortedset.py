SOURCE = 'tatyam_sortedset'
LABEL = 'tatyam-prime/SortedSet'

from SortedSet import SortedSet

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
            output.append(tree.index_right(x))
        elif kind == 4:
            answer = tree.le(x)
            output.append(answer if answer is not None else -1)
        else:
            answer = tree.ge(x)
            output.append(answer if answer is not None else -1)
    return output
