#!/usr/bin/env python
from core.DataCard import DataCard
from rootpy.io import root_open
from collections import namedtuple
from collections import OrderedDict as odict
import os
import yaml
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="e.g. python generate_datacards -i input.yaml -o datacards/")

    parser.add_argument('-i', '--input-yaml', action='store',
                        help="Input yaml file with the input root file structure")
    parser.add_argument('-o', '--outdir', action='store',
                        help="Output directory for the datacards")

    return parser.parse_args()

def setup_regions(config_path):
    Inputs = namedtuple('Inputs', ['regions'])
    Region = namedtuple('Region', ['processes'])
    Process = namedtuple('Process', ['content', 'stats', 'systs'])
    Systematic = namedtuple('Systematic', ['up', 'down'])

    indir = os.path.dirname(config_path)
    def get_hist(path):
        filepath, histpath = os.path.join(indir, path).split(":")
        with root_open(filepath, 'read') as f:
            hist = f.get(histpath)
            hist.set_directory(None)
        return hist

    def hist_to_value(hist, stats=False):
        if stats:
            return hist.integral(overflow=True, error=True)[1]
        else:
            return hist.integral(overflow=True)

    def get(*args):
        return hist_to_value(get_hist(*args))

    def get_stats(*args):
        return hist_to_value(get_hist(*args), stats=True)

    with open(config_path, 'r') as f:
        input_config = yaml.load(f)

    # {region: {...}}
    regions = {}
    for region, process_dict in input_config.items():
        processes = {}

        # {process: {content: path, systs: ...}}
        for process, content_dict in process_dict.items():
            central_path = content_dict["content"]

            # Data doesn't normally have any systematics
            if "systs" not in content_dict:
                content_dict["systs"] = {}

            # {syst: {up: path, down: path}}
            systs = {
                syst: Systematic(
                    up = get(variation_dict["up"]),
                    down = get(variation_dict["down"]),
                )
                for syst, variation_dict in content_dict["systs"].items()
            }

            processes[process] = Process(
                content = get(central_path),
                stats = get_stats(central_path),
                systs = systs,
            )

        regions[region] = Region(processes = processes)
    return Inputs(regions = regions)

if __name__ == "__main__":
    options = parse_args()
    inputs = setup_regions(options.input_yaml)
    outdir = options.outdir

    # Monojet
    dc = DataCard(os.path.join(outdir, "zinv.txt"))
    dc.add_region("monojet", inputs.regions["monojet"].processes["data"].content)
    for idx, proc in enumerate(["znunu", "wlnu", "qcd", "bkg"]):
        nominal = inputs.regions["monojet"].processes[proc].content
        stats = inputs.regions["monojet"].processes[proc].stats
        neff = int((stats / nominal)**2)+1 if nominal>0. else 0
        alpha = nominal / neff if neff>0 else 0.
        dc.add_process("monojet", proc, idx, nominal)

        # lumi
        if proc in ["znunu", "bkg"]:
            dc.add_systematic("monojet", proc, "CMS_lumi", "lnN", 1.025)
        if proc in ["qcd"]:
            dc.add_systematic("monojet", proc, "CMS_qcd", "lnN", 1.20)
            #dc.add_systematic("monojet", proc, "CMS_mcstat_qcd", "gmN {}".format(neff), alpha)
            if nominal == 0.:
                continue

        # PU
        pu_up = inputs.regions["monojet"].processes[proc].systs["pu"].up / nominal
        pu_down = inputs.regions["monojet"].processes[proc].systs["pu"].down / nominal
        dc.add_systematic("monojet", proc, "CMS_puReweight", "lnN", 1+(abs(pu_up-1)+abs(1-pu_down))/2)

        # MET trigger
        met_up = inputs.regions["monojet"].processes[proc].systs["metTrig0muSF"].up / nominal
        met_down = inputs.regions["monojet"].processes[proc].systs["metTrig0muSF"].down / nominal
        dc.add_systematic("monojet", proc, "CMS_metTrigSF", "lnN", 1+(abs(met_up-1)+abs(1-met_down))/2)

        # JECs
        jec_up = inputs.regions["monojet"].processes[proc].systs["jec"].up / nominal
        jec_down = inputs.regions["monojet"].processes[proc].systs["jec"].down / nominal
        dc.add_systematic("monojet", proc, "CMS_jec", "lnN", 1+(abs(jec_up-1)+abs(1-jec_down))/2)
    dc.add_rateparam("tf_wlnu", "monojet", "wlnu", 1)

    # Single Muon
    dc.add_region("singlemu", inputs.regions["singlemu"].processes["data"].content)
    for idx, proc in odict([(1, "wlnu"), (2, "qcd"), (3, "bkg")]).items():
        nominal = inputs.regions["singlemu"].processes[proc].content
        stats = inputs.regions["singlemu"].processes[proc].stats
        neff = int((stats / nominal)**2)+1 if nominal>0. else 0
        alpha = nominal / neff if neff>0 else 0.
        dc.add_process("singlemu", proc, idx, nominal)

        # lumi
        if proc in ["bkg"]:
            dc.add_systematic("singlemu", proc, "CMS_lumi", "lnN", 1.025)
        if proc in ["qcd"]:
            dc.add_systematic("singlemu", proc, "CMS_qcd", "lnN", 1.20)
            if nominal == 0.:
                continue
        # PU
        pu_up = inputs.regions["singlemu"].processes[proc].systs["pu"].up / nominal
        pu_down = inputs.regions["singlemu"].processes[proc].systs["pu"].down / nominal
        dc.add_systematic("singlemu", proc, "CMS_puReweight", "lnN", 1+(abs(pu_up-1)+abs(1-pu_down))/2)

        # Muon SF
        muon_up = inputs.regions["singlemu"].processes[proc].systs["muonIsoSF"].up / nominal
        muon_down = inputs.regions["singlemu"].processes[proc].systs["muonIsoSF"].down / nominal
        dc.add_systematic("singlemu", proc, "CMS_muonIsoSF", "lnN", 1+(abs(muon_up-1)+abs(1-muon_down))/2)

        muon_up = inputs.regions["singlemu"].processes[proc].systs["muonIdSF"].up / nominal
        muon_down = inputs.regions["singlemu"].processes[proc].systs["muonIdSF"].down / nominal
        dc.add_systematic("singlemu", proc, "CMS_muonIdSF", "lnN", 1+(abs(muon_up-1)+abs(1-muon_down))/2)

        muon_up = inputs.regions["singlemu"].processes[proc].systs["muonTrackSF"].up / nominal
        muon_down = inputs.regions["singlemu"].processes[proc].systs["muonTrackSF"].down / nominal
        dc.add_systematic("singlemu", proc, "CMS_muonTrackSF", "lnN", 1+(abs(muon_up-1)+abs(1-muon_down))/2)

        # MET trigger
        met_up = inputs.regions["singlemu"].processes[proc].systs["metTrig1muSF"].up / nominal
        met_down = inputs.regions["singlemu"].processes[proc].systs["metTrig1muSF"].down / nominal
        dc.add_systematic("singlemu", proc, "CMS_metTrigMuSF", "lnN", 1+(abs(met_up-1)+abs(1-met_down))/2)

        # JECs
        jec_up = inputs.regions["singlemu"].processes[proc].systs["jec"].up / nominal
        jec_down = inputs.regions["singlemu"].processes[proc].systs["jec"].down / nominal
        dc.add_systematic("singlemu", proc, "CMS_jec", "lnN", 1+(abs(jec_up-1)+abs(1-jec_down))/2)
    dc.add_rateparam("tf_wlnu", "singlemu", "wlnu", 1)

    # Double Muon
    dc.add_region("doublemu", inputs.regions["doublemu"].processes["data"].content)
    for idx, proc in odict([(0, "dymumu"), (1, "qcd"), (2, "bkg")]).items():
        nominal = inputs.regions["doublemu"].processes[proc].content
        stats = inputs.regions["doublemu"].processes[proc].stats
        neff = int((stats / nominal)**2)+1 if nominal>0. else 0.
        alpha = nominal / neff if neff>0 else 0.
        dc.add_process("doublemu", proc, idx, nominal)

        # lumi
        if proc in ["dymumu", "bkg"]:
            dc.add_systematic("doublemu", proc, "CMS_lumi", "lnN", 1.025)
        if proc in ["qcd"]:
            dc.add_systematic("doublemu", proc, "CMS_qcd", "lnN", 1.20)
            #dc.add_systematic("doublemu", proc, "CMS_mcstat_qcd", "gmN {}".format(neff), alpha)
            if nominal == 0.:
                continue

        # PU
        pu_up = inputs.regions["doublemu"].processes[proc].systs["pu"].up / nominal
        pu_down = inputs.regions["doublemu"].processes[proc].systs["pu"].down / nominal
        dc.add_systematic("doublemu", proc, "CMS_puReweight", "lnN", 1+(abs(pu_up-1)+abs(1-pu_down))/2)

        # Muon SF
        muon_up = inputs.regions["doublemu"].processes[proc].systs["muonIsoSF"].up / nominal
        muon_down = inputs.regions["doublemu"].processes[proc].systs["muonIsoSF"].down / nominal
        dc.add_systematic("doublemu", proc, "CMS_muonIsoSF", "lnN", 1+(abs(muon_up-1)+abs(1-muon_down))/2)

        muon_up = inputs.regions["doublemu"].processes[proc].systs["muonIdSF"].up / nominal
        muon_down = inputs.regions["doublemu"].processes[proc].systs["muonIdSF"].down / nominal
        dc.add_systematic("doublemu", proc, "CMS_muonIdSF", "lnN", 1+(abs(muon_up-1)+abs(1-muon_down))/2)

        muon_up = inputs.regions["doublemu"].processes[proc].systs["muonTrackSF"].up / nominal
        muon_down = inputs.regions["doublemu"].processes[proc].systs["muonTrackSF"].down / nominal
        dc.add_systematic("doublemu", proc, "CMS_muonTrackSF", "lnN", 1+(abs(muon_up-1)+abs(1-muon_down))/2)

        # MET trigger
        met_up = inputs.regions["doublemu"].processes[proc].systs["metTrig2muSF"].up / nominal
        met_down = inputs.regions["doublemu"].processes[proc].systs["metTrig2muSF"].down / nominal
        dc.add_systematic("doublemu", proc, "CMS_metTrigMuSF", "lnN", 1+(abs(met_up-1)+abs(1-met_down))/2)

        # JECs
        jec_up = inputs.regions["doublemu"].processes[proc].systs["jec"].up / nominal
        jec_down = inputs.regions["doublemu"].processes[proc].systs["jec"].down / nominal
        dc.add_systematic("doublemu", proc, "CMS_jec", "lnN", 1+(abs(jec_up-1)+abs(1-jec_down))/2)

    # rate params
    dc.add_rateparam("r_mumu", "doublemu", "dymumu", 1)
    dc.add_rateparam("r_nunu", "monojet", "znunu", "(@0*@1) r,r_mumu")

    dc.sort_systematics([
        "CMS_lumi", "CMS_puReweight", "CMS_jec", "CMS_metTrigSF",
        "CMS_metTrigMuSF", "CMS_muonIdSF", "CMS_muonIsoSF", "CMS_muonTrackSF",
        "CMS_qcd",
    ])
    dc.write()
