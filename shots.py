# Utility script that grabs Animation Metadata from shotpieces
# python <script> <maya-file>

import sys, re, json, pprint

if len(sys.argv) is 2:
    path = sys.argv[1]
    obj = {}
    try:
        f = open(path, "r")
        data = f.read()
        for match in re.findall("fileInfo\\s+(\"|')(shot_piece_[\\d]+)\\1\\s+(\"|')({.*?})\\3\\s*;", data):
            obj[match[1]] = json.loads(match[3].decode("unicode_escape"))
        f.close()
        pprint.pprint(obj)
    except IOError as e:
        print e
