#!/usr/bin/env python
import argparse
import json
from rootpy.io import root_open

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", action='store',
                        help="File and object path for the RooFit Fit result")
    parser.add_argument("-o", "--outfile", action='store', default="stats_impacts.json",
                        help="Output file for the result")
    parser.add_argument("--poi", action='store', default='r',
                        help="Name of the parameter of interest")
    parser.add_argument("-n", "--name", action='store', default='stats',
                        help="Name given to the impact source")
    return parser.parse_args()

def get_rootobj(path):
    filepath, objpath = path.split(":")
    with root_open(filepath, 'read') as f:
        obj = f.get(objpath)
        if hasattr(obj, 'SetDirectory'):
            obj.SetDirectory(None)
    return obj

def poi_fit(fit_result, poi='r'):
    poi_var = fit_result.final_params[poi]

    central = poi_var.getValV()
    var_up = poi_var.getErrorHi()
    var_do = poi_var.getErrorLo()

    return central, var_up, var_do

def create_json(outdict, outfile="test.json"):
    with open(outfile, 'w') as f:
        json.dump(outdict, f, indent=4)

if __name__ == "__main__":
    options = parse_args()

    poi_stats_only = poi_fit(
        get_rootobj(options.path+":fit_s"),
        poi = options.poi,
    )

    central = poi_stats_only[0]
    impacts = (poi_stats_only[1]/central, poi_stats_only[2]/central)

    results = {
        "POIs": [],
        "params" : [{
            "fit": [],
            "groups": [],
            "impact_r": max(impacts),
            "name": options.name,
            "prefit": [],
            "r": [
                central+poi_stats_only[2],
                central,
                central+poi_stats_only[1],
            ],
            "type": "Poisson",
        }],
    }
    create_json(results, outfile=options.outfile)
