'''
mayaPersist - namespace for functions related to storing data in fileInfo objects inside the current Maya file

I've tested this (a little) with as many as 100,000 integers - it works but it's slooow at that size
< 1000 values seems imperceptible
'''

import json
import base64
from  maya.cmds import fileInfo
import itertools

def save(key, value):
    '''
    save the specified value as a base64 encoded yaml dunp at key 'key'
    '''
    encoded =encode(value)
    fileInfo(key, encoded)

def load(key):
    '''
    return the value stored at 'key', or None if the value can't be found

    @note it is possible to store a 'None' in the value, so this doesn't prove that the key does not exist !
    '''
    answer = fileInfo(key, q=True)
    if not answer:
        return None
    return decode(answer[0])

def exists(key):
    '''
    returns true if the specified key exists
    '''
    answer = fileInfo(key, q=True)
    return len(answer) != 0

def ls():
    '''
    a generator that returns all of the key-value pairs in this file's fileInfo

    @note:  these are not decoded, because they contain a mix of native stirngs and b64 values
    '''
    all_values = fileInfo(q=True)
    keys = itertools.islice(all_values, 0, None, 2)
    values = itertools.islice(all_values, 1, None, 2)
    return itertools.izip(keys, values)


def delete(key):
    '''
    remove the key and any data stored with it from this file
    '''
    fileInfo(rm=key)

def decode(value):
    '''
    convert a base64'ed yaml object back into a maya object

    if the object is not encoded (eg, one of the default string values) return it untouched
    '''
    try:
        val = base64.b64decode(value)
        return json.loads(val)
    except TypeError:  
        return value



def encode (value):
    '''
    return the supplied value encoded into base64-packed YAML dump
    '''
    return  base64.b64encode(json.dumps(value))