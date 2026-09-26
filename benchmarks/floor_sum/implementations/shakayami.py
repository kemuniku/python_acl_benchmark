SOURCE = 'shakayami'
LABEL = 'shakayami/ACL-for-python'

from acl_math import floor_sum

def run(data):
    return [floor_sum(n, m, a, b) for n, m, a, b in data]
