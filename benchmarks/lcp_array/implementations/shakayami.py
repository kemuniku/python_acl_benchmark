SOURCE = 'shakayami'
LABEL = 'shakayami/ACL-for-python'

from acl_string import String

def run(data):
    s, sa = data
    return String(s).lcp_array(sa)
