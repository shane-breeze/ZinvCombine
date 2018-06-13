#!/usr/bin/env python
import json
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs='*',
                        help="List of json files to merge")
    parser.add_argument("-o", "--outfile", action='store',
                        help="Output json file")
    return parser.parse_args()

def merge_jsons(paths):
    merged_dict = {"POIs": [], "params": []}
    for path in paths:
        with open(path, 'r') as f:
            d = json.load(f)
        for attr in ["POIs", "params"]:
            merged_dict[attr].extend(d[attr])
    return merged_dict

def create_json(outdict, outfile="test.json"):
    with open(outfile, 'w') as f:
        json.dump(outdict, f, indent=4)

if __name__ == "__main__":
    options = parse_args()
    outdict = merge_jsons(options.paths)
    create_json(outdict, outfile=options.outfile)
