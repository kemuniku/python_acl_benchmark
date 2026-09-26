SOURCE = 'shakayami'
LABEL = 'shakayami/ACL-for-python'

from acl_string import String

def run(data):
    return String(data).suffix_array()
