import argparse
import glob
import matplotlib.pyplot as plt
import pandas as pd
import re

from impacts import get_fit_results

nuis_col = {
    "jer": "#1f78b4",
    "jes": "#33a02c",
    "metTrigSF": "#e31a1c",
    "muonId": "#ff7f00",
    "muonIso": "#cab2d6",
    "muonTrack": "#6a3d9a",
    "pileup": "#ffff99",
    "unclust": "#fb9a99",
    "lumi": "#fdbf6f",
    "total": "black",
}

nuis_lab = {
    "jer": "JER",
    "jes": "JES",
    "metTrigSF": "MET Trig. SF",
    "muonId": "Muon ID",
    "muonIso": "Muon Iso.",
    "muonTrack": "Muon Track.",
    "pileup": "Pileup",
    "unclust": "Unclust. En.",
    "lumi": "Lumi.",
    "total": "Total",
}

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("results_dir", type=str,
                        help="Directory with the desired results")
    parser.add_argument("-n", "--name", type=str, default="Exp",
                        help="String to add to regex")
    parser.add_argument("-o", "--output", type=str, default="impacts.pdf",
                        help="Output file")

    return parser.parse_args()

def draw_impact_vs_metnox(df_up, df_down, output):
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(5.4, 4.8))

    columns = df_up.columns
    binning = list(df_up.index.get_level_values("METnoX"))
    binning.append(2*binning[-1]-binning[-2])
    for c in columns:
        ax.step(
            binning,
            list(df_up[c])+[0.],
            where = 'post',
            color = nuis_col[c],
            label = nuis_lab[c],
        )
        ax.step(
            binning,
            list(df_down[c])+[0.],
            where = 'post',
            color = nuis_col[c],
        )
        ax.axhline(0., lw=1.5, ls='--', color='black')

    ax.set_xlim((binning[0], binning[-1]))
    ax.set_ylim((-0.2, 0.2))
    ax.set_xlabel(r'$E_{T}^{miss}$ Threshold (GeV)', fontsize='large')
    ax.set_ylabel(r'Impact', fontsize='large')

    leg_sort_df = pd.concat([df_down.mean(axis=0), df_up.mean(axis=0)], axis=1)
    leg_sort = leg_sort_df.max(axis=1).sort_values().index.values

    handles, labels = ax.get_legend_handles_labels()
    argsort = [labels.index(nuis_lab[l]) for l in leg_sort][::-1]
    handles = [handles[idx] for idx in argsort]
    labels = [labels[idx] for idx in argsort]
    ax.legend(handles, labels, ncol=2)

    ax.text(0, 1, r'$\mathbf{CMS}\ \mathit{Preliminary}$',
            ha='left', va='bottom', transform=ax.transAxes,
            fontsize='large')
    ax.text(1, 1, r'$35.9\ \mathrm{fb}^{-1}(13\ \mathrm{TeV})$',
            ha='right', va='bottom', transform=ax.transAxes,
            fontsize='large')

    plt.tight_layout()
    fig.savefig(output, format="pdf", bbox_inches="tight")
    plt.close(fig)
    print("Created {}".format(output))

def main():
    options = parse_args()

    regex_initial_fit = re.compile("higgsCombineNominalFit{}\.MultiDimFit\.mH120\.root".format(options.name))
    regex_param_fit = re.compile("higgsCombineNuisFit{}_(?P<param>[^_^.]*)\.MultiDimFit\.mH120\.root".format(options.name))
    regex_bins = re.compile("Zinv_METnoX-(?P<bin>[0-9]+)ToInf")

    data_up = []
    data_down = []
    binning = []
    for direc in glob.glob(options.results_dir):
        binning.append(int(regex_bins.search(direc).group("bin")))
        names, nuisances, impacts, bestfit = get_fit_results(
            direc,
            regex_initial_fit,
            regex_param_fit,
        )
        data_up.append(dict(zip(names, impacts[:,0])))
        data_down.append(dict(zip(names, impacts[:,1])))
        data_up[-1].update({"total": bestfit[2]-bestfit[0]})
        data_down[-1].update({"total": bestfit[1]-bestfit[0]})
    df_up = pd.DataFrame(data_up)
    df_down = pd.DataFrame(data_down)

    df_up["METnoX"] = binning
    df_up = df_up.set_index("METnoX")

    df_down["METnoX"] = binning
    df_down = df_down.set_index("METnoX")

    draw_impact_vs_metnox(df_up, df_down, options.output)

if __name__ == "__main__":
    main()
