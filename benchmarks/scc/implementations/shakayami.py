SOURCE = 'shakayami'
LABEL = 'shakayami/ACL-for-python'

from scc import scc

def run(data):
    n, edges = data
    return sorted(sorted(group) for group in scc(n, edges))
