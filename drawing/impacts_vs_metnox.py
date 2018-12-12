import argparse
import glob
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import re

from impacts import get_fit_result

nuis_col = {
    "r":         "black",
    "jer":       "#1f78b4",
    "jesTotal":  "#33a02c",
    "metTrigSF": "#e31a1c",
    "muonId":    "#ff7f00",
    "muonIso":   "#cab2d6",
    "muonTrack": "#6a3d9a",
    "pileup":    "#ffff99",
    "unclust":   "#fb9a99",
    "lumi":      "#fdbf6f",
    "stat":      "#a6cee3",
}

nuis_lab = {
    "r":         "Total",
    "jer":       "JER",
    "jesTotal":  "JES",
    "metTrigSF": r'$p_{\mathrm{T}}^{\mathrm{miss}}$ trig.',
    "muonId":    r'$\mu$ id.',
    "muonIso":   r'$\mu$ iso.',
    "muonTrack": r'$\mu$ track.',
    "pileup":    "Pileup",
    "unclust":   "Unclust. En.",
    "lumi":      "Lumi.",
    "stat":      "Stat.",
}

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("results_dir", type=str,
                        help="Directory with the desired results")
    parser.add_argument("-n", "--name", type=str, default="Exp",
                        help="String to add to regex")
    parser.add_argument("-o", "--output", type=str, default="impacts.pdf",
                        help="Output file")
    parser.add_argument("--poi", type=str, default='r',
                        help="Parameter of interest")

    return parser.parse_args()

def draw_impact_vs_metnox(df, poi, output):
    df[poi+"_av"] = df.eval("0.5*(abs({0}_up) + abs({0}_down))".format(poi))
    df_av = df.pivot_table(index="bin", columns="parameter", values=poi+"_av")

    leg_sort = df_av.max(axis=0).sort_values().index.values[-6:]
    #df = df[df.index.get_level_values("parameter").isin(leg_sort)]

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(5.4, 4.8))

    binning = sorted(list(df.index.get_level_values("bin").unique().values))
    #binning.append(2*binning[-1]-binning[-2])
    binning = np.array(binning)
    params = df.index.get_level_values("parameter").unique().values
    for p in params:
        ax.step(
            binning,
            list(df[df.index.get_level_values("parameter")==p][poi+"_up"]),
            where = 'pre',
            color = nuis_col.get(p, "gray"),
            label = nuis_lab.get(p, p),
        )
        ax.step(
            binning,
            list(df[df.index.get_level_values("parameter")==p][poi+"_down"]),
            where = 'pre',
            color = nuis_col.get(p, "gray"),
        )
        ax.axhline(0., lw=1.5, ls='--', color='black')

    ax.set_xlim((binning[0], binning[-1]))
    ax.set_ylim((-0.2, 0.2))
    ax.set_xlabel(r'$p_{\mathrm{T}}^{\mathrm{miss}}$ Threshold (GeV)', fontsize=12)
    ax.set_ylabel(r'Impact', fontsize=12)

    handles, labels = ax.get_legend_handles_labels()
    argsort = [labels.index(nuis_lab[l]) for l in leg_sort][::-1]
    handles = [handles[idx] for idx in argsort]
    labels = [labels[idx] for idx in argsort]
    ax.legend(handles, labels, ncol=2)

    ax.text(0, 1, r'$\mathbf{CMS}\ \mathit{Preliminary}$',
            ha='left', va='bottom', transform=ax.transAxes,
            fontsize=12)
    ax.text(1, 1, r'$35.9\ \mathrm{fb}^{-1}(13\ \mathrm{TeV})$',
            ha='right', va='bottom', transform=ax.transAxes,
            fontsize=12)

    #plt.tight_layout()
    fig.savefig(output, format="pdf", bbox_inches="tight")
    plt.close(fig)
    print("Created {}".format(output))

def main():
    options = parse_args()
    poi_name = options.poi

    regex_initial_fit = re.compile("higgsCombineNominalFit.*{}\.MultiDimFit\.mH120\.root".format(options.name))
    regex_param_fit = re.compile("higgsCombineNuisFit.*{}_(?P<param>[^_^.]*)\.MultiDimFit\.mH120\.root".format(options.name))
    regex_bins = re.compile("METnoX-(?P<bin>[0-9]+)ToInf")

    data = []
    for path in glob.glob(options.results_dir):
        match = regex_bins.search(path)
        if not match:
            continue
        bin = match.group("bin")

        match_nuis = regex_param_fit.search(path)
        if match_nuis:
            param = match_nuis.group("param")

        match_poi = regex_initial_fit.search(path)
        if match_poi:
            param = poi_name

        if not match_nuis and not match_poi:
            continue

        fit_result = get_fit_result(path, poi_name)
        data.append({
            "bin": int(bin),
            "parameter": param,
            poi_name: fit_result[0],
            poi_name+"_up": fit_result[0] - fit_result[1],
            poi_name+"_down": fit_result[0] - fit_result[2],
        })

    df = pd.DataFrame(data).set_index(["bin", "parameter"])
    draw_impact_vs_metnox(df, poi_name, options.output)

if __name__ == "__main__":
    main()
