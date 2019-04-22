import uproot
import numpy as np
import pandas as pd
import argparse
from uproot_methods.classes.TH1 import Methods

import matplotlib.pyplot as plt
import seaborn as sns

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("path", type=str, help="Path to shapes file")
    parser.add_argument("-o", "--output", type=str, default="shapes_{}.pdf",
                        help="Output file names")
    parser.add_argument("-r", "--region", type=str, default="monojet",
                        help="Region to select")
    parser.add_argument("-p", "--process", type=str, default="znunu",
                        help="Process to select")
    parser.add_argument("-n", "--nuisance", type=str, default="jer",
                        help="Nuisance to select")

    return parser.parse_args()

def draw(df, output):
    df["syst"] = np.array([s.replace("_", " ") for s in df["syst"].values])

    #print(df[(df["syst"]=="metTrigStat") & (df["variation"]=="up") & (df["process"]=="zmumu")])

    #plt.rcParams['xtick.top'] = False
    #plt.rcParams['ytick.right'] = False
    #with sns.plotting_context(context='paper', font_scale=1.8):
    #    g = sns.FacetGrid(
    #        df, row='syst', col='process', hue='variation',
    #        margin_titles=True, legend_out=True,
    #    )
    #    g.map(plt.step, "bins", "count", where='post').add_legend()
    #    #g.set(ylim=(0.5, 1.5))

    #    #g.fig.text(0.0, 1, r'$\mathbf{CMS}\ \mathit{Preliminary}$',
    #    #           ha='left', va='bottom', fontsize='large')
    #    #g.fig.text(0.9, 1, r'$35.9\ \mathrm{fb}^{-1}(13\ \mathrm{TeV})$',
    #    #           ha='right', va='bottom', fontsize='large')

    #    # Report
    #    print("Creating {}".format(output))

    #    # Actually save the figure
    #    g.fig.savefig(output, format="pdf", bbox_inches="tight")
    #    plt.close(g.fig)

    #plt.rcParams['xtick.top'] = True
    #plt.rcParams['ytick.right'] = True

    dfup = df.loc[df["variation"]=="up"]
    dfdown = df.loc[df["variation"]=="down"]

    fig, ax = plt.subplots()

    bins = list(dfup["bins"].values)
    bins.append(2*bins[-1]-bins[-2])
    bins = np.array(bins)
    ax.hist(
        dfup["bins"],
        weights = dfup["count"],
        bins = bins,
        histtype = 'step',
    )
    ax.hist(
        dfdown["bins"],
        weights = dfdown["count"],
        bins = bins,
        histtype = 'step',
    )
    ax.set_xlim(bins.min(), bins.max())
    ymin = min(dfdown["count"].min(), dfup["count"].min())
    ymax = max(dfdown["count"].max(), dfup["count"].max())
    ax.set_ylim(
        ymin - 0.1*(ymax-ymin),
        ymax + 0.1*(ymax-ymin),
    )

    fig.savefig(output, format="pdf", bbox_inches="tight")
    print(output)

def create_df(path, chosen_regions, chosen_processes, chosen_nuisances):
    with uproot.open(path) as f:
        regions = f.keys()

        for region in regions:
            if region.replace(";1", "") not in chosen_regions:
                continue
            processes = list(set([
                process
                for process in f[region].keys()
                if isinstance(f[region][process], Methods)\
                and process not in ["data_obs;1"]
            ]))

            systnames = list(set([
                systname.replace("Up", "").replace("Down", "")
                for systname in f[region].keys()
                if isinstance(f[region][systname], uproot.rootio.ROOTDirectory)
            ]))

            df = None
            for process in processes:

                if process.replace(";1", "") not in chosen_processes:
                    continue

                nominal = f[region][process].pandas()
                bins = nominal.index.get_level_values(process.replace(";1", "")).values

                for systname in systnames:

                    if systname.replace(";1", "Up;1") not in f[region].keys()\
                       or systname.replace(";1", "Down;1") not in f[region].keys():
                        continue

                    if process not in f[region][systname.replace(";1", "Up;1")].keys()\
                       or process not in f[region][systname.replace(";1", "Down;1")].keys():
                        continue

                    variation_up = f[region][systname.replace(";1", "Up;1")][process].pandas() / nominal
                    variation_down = f[region][systname.replace(";1", "Down;1")][process].pandas() / nominal

                    variation_up = variation_up.reset_index()
                    variation_down = variation_down.reset_index()
                    variation_up = variation_up.rename({process.replace(";1", ""): "bins"}, axis=1)
                    variation_down = variation_down.rename({process.replace(";1", ""): "bins"}, axis=1)

                    variation_up["syst"] = systname.replace(";1", "")
                    variation_up["variation"] = "up"
                    variation_up["bins"] = variation_up["bins"].apply(lambda b: b.left)
                    variation_up["process"] = process
                    variation_down["syst"] = systname.replace(";1", "")
                    variation_down["variation"] = "down"
                    variation_down["bins"] = variation_down["bins"].apply(lambda b: b.left)
                    variation_down["process"] = process

                    if systname.replace(";1", "") not in chosen_nuisances:
                        continue

                    df = pd.concat([variation_up, variation_down], sort=False)
                    df = df.reset_index(drop=True)
                    draw(df, "alternative_tempaltes_{}_{}_{}.pdf".format(region.replace(";1", ""), process.replace(";1", ""), systname.replace(";1", "")))

        pass
    pass

def main():
    options = parse_args()
    create_df(
        options.path, options.region.split(","), options.process.split(","),
        options.nuisance.split(","),
    )

if __name__ == "__main__":
    main()
