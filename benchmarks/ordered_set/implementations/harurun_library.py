SOURCE = 'harurun'
LABEL = 'lif4635/harurun-s-library (library / BinaryTrie)'

from library.SegTree.BinaryTrie import BinaryTrie

def run(data):
    initial, queries = data
    tree = BinaryTrie()
    for value in initial:
        tree.add(value)
    output = []
    for kind, x in queries:
        if kind == 0:
            if not tree.find(x):
                tree.add(x)
        elif kind == 1:
            tree.delete(x)
        elif kind == 2:
            answer = tree.get_kth(x)
            output.append(answer if answer is not None else -1)
        elif kind == 3:
            output.append(tree.count_leq(x))
        elif kind == 4:
            answer = tree.get_kth(tree.count_leq(x))
            output.append(answer if answer is not None else -1)
        else:
            answer = tree.get_kth(tree.count_leq(x - 1) + 1) if x else tree.get_kth(1)
            output.append(answer if answer is not None else -1)
    return output
