import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import uproot

conv_names = {
    "r":                  r'$r$',
    "r_ggH":              r'$r_{gg\rm{H}}$',
    "tf_wlnu":            r'$t_{W,\mu}$',
    "d1k_ew":             r'$\delta^{(1)}\kappa_{EW}$',
    "d2k_ew_z":           r'$\delta^{(2)}\kappa_{EW}^{Z}$',
    "d2k_ew_w":           r'$\delta^{(2)}\kappa_{EW}^{W}$',
    "d3k_ew_z":           r'$\delta^{(3)}\kappa_{EW}^{Z}$',
    "d3k_ew_w":           r'$\delta^{(3)}\kappa_{EW}^{W}$',
    "eleIdIso":           r'Ele ID/Iso',
    "eleReco":            r'Ele Reco',
    "eleTrig":            r'Ele Trig',
    "jer":                r'JER',
    "jesTotal":           r'JES',
    "jesAbsoluteMPFBias": r'JES abs ISR+FSR bias',
    "jesAbsoluteScale":   r'JES abs scale',
    "jesAbsoluteStat":    r'JES abs stat',
    "jesFlavorQCD":       r'JES flavour QCD',
    "jesFragmentation":   r'JES frag',
    "jesPileUpDataMC":    r'JES PU Data/MC',
    "jesPileUpPtBB":      r'JES PU $p_{\rm{T}}$ BB',
    "jesPileUpPtEC1":     r'JES PU $p_{\rm{T}}$ EC1',
    "jesPileUpPtEC2":     r'JES PU $p_{\rm{T}}$ EC2',
    "jesPileUpPtHF":      r'JES PU $p_{\rm{T}}$ HF',
    "jesPileUpPtRef":     r'JES PU $p_{\rm{T}}$ ref',
    "jesRelativeBal":     r'JES Bal',
    "jesRelativeFSR":     r'JES ISR+FSR',
    "jesRelativeJEREC1":  r'JER EC1',
    "jesRelativeJEREC2":  r'JER EC2',
    "jesRelativeJERHF":   r'JER HF',
    "jesRelativePtBB":    r'JES $p_{\rm{T}}$ BB',
    "jesRelativePtEC1":   r'JES $p_{\rm{T}}$ EC1',
    "jesRelativePtEC2":   r'JES $p_{\rm{T}}$ EC2',
    "jesRelativePtHF":    r'JES $p_{\rm{T}}$ HF',
    "jesRelativeStatFSR": r'JES ISR+FSR stat',
    "jesRelativeStatEC":  r'JES EC stat',
    "jesRelativeStatHF":  r'JES HF stat',
    "jesSinglePionECAL":  r'JES single $\pi$ ECAL',
    "jesSinglePionHCAL":  r'JES single $\pi$ HCAL',
    "jesTimePtEta":       r'JES time $p_{\rm{T}}$--$\eta$',
    "lumi":               r'Lumi.',
    "metTrigSF":          r'$E_{T}^{miss}$ Trig',
    "muonId":             r'Muon ID',
    "muonIso":            r'Muon Iso',
    "muonTrack":          r'Muon Track',
    "muonTrig":           r'Muon Trig',
    "pileup":             r'Pileup',
    "unclust":            r'Unclust En',
    "deltaNLL":           r'$-\Delta \log \mathcal{L}$',
}


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("scan_exp", type=str,
                        help="input root file with the expected nll scan")
    parser.add_argument("--scan_obs", type=str, default=None,
                        help="input root file with the observed nll scan")
    parser.add_argument("--singles_exp", type=str, default=None,
                        help="input root file with the expected singles")
    parser.add_argument("--singles_obs", type=str, default=None,
                        help="input root file with the observed singles")
    parser.add_argument("--poi", type=str, default="r", help="POI")
    parser.add_argument("--nuisances", type=str, default="",
                        help="Space delimited nuisance list")
    parser.add_argument("-o", "--output", type=str, default="ll1dscan.pdf",
                        help="Output file")

    return parser.parse_args()

def main():
    plt.rcParams['xtick.top'] = False
    plt.rcParams['ytick.right'] = False
    with sns.plotting_context(context='paper', font_scale=1.8):
        options = parse_args()
        poi = options.poi
        nuisances = options.nuisances.split()

        # expected
        rfile_exp = uproot.open(options.scan_exp)
        scan_exp = rfile_exp["limit"]
        arrays_exp = scan_exp.arrays(nuisances+["deltaNLL", poi])
        poi_exp = arrays_exp[poi][1:]

        df = pd.DataFrame(arrays_exp)
        dnll = df["deltaNLL"].values
        df = df[[c for c in df.columns if "deltaNLL" not in c]]
        bf = df.iloc[0]
        df = df.iloc[1:]
        df = df.sort_values(poi)

        poi_series = df[poi]
        df = df.drop(poi, axis=1)
        df = pd.melt(df)
        df.columns = ["n", "Value"]
        df["deltaNLL"] = list(dnll)*len(df["n"].unique())
        df[conv_names[poi]] = list(poi_series)*len(df["n"].unique())

        def convert(name):
            try:
                return conv_names[name]
            except KeyError:
                return name.replace("_", " ")
        df["n"] = df["n"].apply(convert)

        g = sns.FacetGrid(df, col="n", margin_titles=True, col_wrap=5,
                          sharex=False, sharey=False)
        g.map(plt.plot, conv_names[poi], "Value")

        g.fig.text(0, 1.005, r'$\mathbf{CMS}\ \mathit{Preliminary}$',
                   ha='left', va='bottom', fontsize='large')
        g.fig.text(1, 1.005, r'$35.9\ \mathrm{fb}^{-1}(13\ \mathrm{TeV})$',
                   ha='right', va='bottom', fontsize='large')

        ##plt.tight_layout()
        g.fig.savefig(options.output, format="pdf", bbox_inches="tight")
        plt.close(g.fig)
        print("Created {}".format(options.output))

if __name__ == "__main__":
    main()
