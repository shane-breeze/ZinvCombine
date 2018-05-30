from rootpy.io import root_open
from collections import namedtuple
from collections import OrderedDict as odict
import os
import yaml

from core.DataCard import DataCard

def setup_regions(config_path):
    Inputs = namedtuple('Inputs', ['regions'])
    Region = namedtuple('Region', ['processes'])
    Process = namedtuple('Process', ['content', 'systs'])
    Systematic = namedtuple('Systematic', ['up', 'down'])

    indir = os.path.dirname(config_path)
    def get_hist(path):
        filepath, histpath = os.path.join(indir, path).split(":")
        with root_open(filepath, 'read') as f:
            hist = f.get(histpath)
            hist.set_directory(None)
        return hist

    def hist_to_value(hist):
        return hist.integral(overflow=True)

    def get(*args):
        return hist_to_value(get_hist(*args))

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
                systs = systs,
            )

        regions[region] = Region(processes = processes)
    return Inputs(regions = regions)

if __name__ == "__main__":
    inputs = setup_regions("/vols/build/cms/sdb15/ZinvWidth/HiggsCombine/ZinvCombine/data/inputs.yaml")

    # Monojet
    dc = DataCard("test_monojet.txt")
    dc.add_region("monojet", inputs.regions["monojet"].processes["data"].content)
    for idx, proc in enumerate(["znunu", "wlnu", "bkg"]):
        nominal = inputs.regions["monojet"].processes[proc].content
        dc.add_process("monojet", proc, idx, nominal)

        # lumi
        if proc != "wlnu":
            dc.add_systematic("monojet", proc, "CMS_lumi", "lnN", 1.025)

        # PU
        pu_up = inputs.regions["monojet"].processes[proc].systs["pu"].up / nominal
        pu_down = inputs.regions["monojet"].processes[proc].systs["pu"].down / nominal
        dc.add_systematic("monojet", proc, "CMS_puReweight", "lnN", 1+(abs(pu_up-1)+abs(1-pu_down))/2)

        # MET trigger
        met_up = inputs.regions["monojet"].processes[proc].systs["metTrig0muSF"].up / nominal
        met_down = inputs.regions["monojet"].processes[proc].systs["metTrig0muSF"].down / nominal
        dc.add_systematic("monojet", proc, "CMS_metTrig0muSF", "lnN", 1+(abs(met_up-1)+abs(1-met_down))/2)

        # JECs
        jec_up = inputs.regions["monojet"].processes[proc].systs["jec"].up / nominal
        jec_down = inputs.regions["monojet"].processes[proc].systs["jec"].down / nominal
        dc.add_systematic("monojet", proc, "CMS_jec", "lnN", 1+(abs(jec_up-1)+abs(1-jec_down))/2)
    dc.add_rateparam("tf_wlnu", "monojet", "wlnu", 1)
    dc.write()

    # Single Muon
    dc = DataCard("test_singlemu.txt")
    dc.add_region("singlemu", inputs.regions["singlemu"].processes["data"].content)
    for idx, proc in odict([(1, "wlnu"), (2, "bkg")]).items():
        nominal = inputs.regions["singlemu"].processes[proc].content
        dc.add_process("singlemu", proc, idx, nominal)

        # lumi
        if proc != "wlnu":
            dc.add_systematic("singlemu", proc, "CMS_lumi", "lnN", 1.025)

        # PU
        pu_up = inputs.regions["singlemu"].processes[proc].systs["pu"].up / nominal
        pu_down = inputs.regions["singlemu"].processes[proc].systs["pu"].down / nominal
        dc.add_systematic("singlemu", proc, "CMS_puReweight", "lnN", 1+(abs(pu_up-1)+abs(1-pu_down))/2)

        # Muon SF
        muon_up = inputs.regions["singlemu"].processes[proc].systs["muonSF"].up / nominal
        muon_down = inputs.regions["singlemu"].processes[proc].systs["muonSF"].down / nominal
        dc.add_systematic("singlemu", proc, "CMS_muonSF", "lnN", 1+(abs(muon_up-1)+abs(1-muon_down))/2)

        # MET trigger
        met_up = inputs.regions["singlemu"].processes[proc].systs["metTrig1muSF"].up / nominal
        met_down = inputs.regions["singlemu"].processes[proc].systs["metTrig1muSF"].down / nominal
        dc.add_systematic("singlemu", proc, "CMS_metTrig1muSF", "lnN", 1+(abs(met_up-1)+abs(1-met_down))/2)

        # JECs
        jec_up = inputs.regions["singlemu"].processes[proc].systs["jec"].up / nominal
        jec_down = inputs.regions["singlemu"].processes[proc].systs["jec"].down / nominal
        dc.add_systematic("singlemu", proc, "CMS_jec", "lnN", 1+(abs(jec_up-1)+abs(1-jec_down))/2)
    dc.add_rateparam("tf_wlnu", "singlemu", "wlnu", 1)
    dc.write()

    # Double Muon
    dc = DataCard("test_doublemu.txt")
    dc.add_region("doublemu", inputs.regions["doublemu"].processes["data"].content)
    for idx, proc in odict([(0, "dymumu"), (1, "bkg")]).items():
        nominal = inputs.regions["doublemu"].processes[proc].content
        dc.add_process("doublemu", proc, idx, nominal)

        # lumi
        dc.add_systematic("doublemu", proc, "CMS_lumi", "lnN", 1.025)

        # PU
        pu_up = inputs.regions["doublemu"].processes[proc].systs["pu"].up / nominal
        pu_down = inputs.regions["doublemu"].processes[proc].systs["pu"].down / nominal
        dc.add_systematic("doublemu", proc, "CMS_puReweight", "lnN", 1+(abs(pu_up-1)+abs(1-pu_down))/2)

        # Muon SF
        muon_up = inputs.regions["doublemu"].processes[proc].systs["muonSF"].up / nominal
        muon_down = inputs.regions["doublemu"].processes[proc].systs["muonSF"].down / nominal
        dc.add_systematic("doublemu", proc, "CMS_muonSF", "lnN", 1+(abs(muon_up-1)+abs(1-muon_down))/2)

        # MET trigger
        met_up = inputs.regions["doublemu"].processes[proc].systs["metTrig2muSF"].up / nominal
        met_down = inputs.regions["doublemu"].processes[proc].systs["metTrig2muSF"].down / nominal
        dc.add_systematic("doublemu", proc, "CMS_metTrig2muSF", "lnN", 1+(abs(met_up-1)+abs(1-met_down))/2)

        # JECs
        jec_up = inputs.regions["doublemu"].processes[proc].systs["jec"].up / nominal
        jec_down = inputs.regions["doublemu"].processes[proc].systs["jec"].down / nominal
        dc.add_systematic("doublemu", proc, "CMS_jec", "lnN", 1+(abs(jec_up-1)+abs(1-jec_down))/2)
    dc.write()
