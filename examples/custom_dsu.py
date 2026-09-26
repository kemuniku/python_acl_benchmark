"""Copy to benchmarks/dsu/implementations/local.py, then run the benchmark.

LABEL is displayed in the chart. Omit SOURCE for local implementations without
an external checkout. Input is (n, operations): (0, a, b) merges components and
(1, a, b) asks whether two vertices are connected. Return the query booleans.
"""

LABEL = "Local DSU (union by size + path compression)"


class DisjointSetUnion:
    def __init__(self, n):
        # A root stores minus its component size; other entries store a parent.
        self.parent_or_size = [-1] * n

    def leader(self, vertex):
        parents = self.parent_or_size
        root = vertex
        while parents[root] >= 0:
            root = parents[root]
        while vertex != root:
            parent = parents[vertex]
            parents[vertex] = root
            vertex = parent
        return root

    def merge(self, left, right):
        left, right = self.leader(left), self.leader(right)
        if left == right:
            return
        parents = self.parent_or_size
        if parents[left] > parents[right]:
            left, right = right, left
        parents[left] += parents[right]
        parents[right] = left

    def same(self, left, right):
        return self.leader(left) == self.leader(right)


def run(data):
    n, operations = data
    tree = DisjointSetUnion(n)
    answers = []
    for kind, left, right in operations:
        if kind == 0:
            tree.merge(left, right)
        else:
            answers.append(tree.same(left, right))
    return answers
