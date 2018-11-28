import argparse
import glob
import matplotlib.pyplot as plt
import os
import pandas as pd
import re
import uproot

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("results_dir", type=str,
                        help="Directory with the desired results")
    parser.add_argument("-n", "--name", type=str, default="Exp",
                        help="String to add to regex")
    parser.add_argument("-o", "--output", type=str, default="tf.pdf",
                        help="Output file")

    return parser.parse_args()

def get_tf(path):
    fit_results = uproot.open(path)["fit_s"]
    fit_results.Print()

def draw_tf_vs_metnox(df_up, df_down, output):
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
    ax.set_ylim((-0.3, 0.3))
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
    regex_bins = re.compile("METnoX-(?P<bin>[0-9]+)ToInf")

    data_up = []
    data_down = []
    binning = []
    for direc in glob.glob(options.results_dir):
        binning.append(int(regex_bins.search(direc).group("bin")))

        path = os.path.join(direc, "fitDiagnosticsMLFitMasked{}.root".format(options.name))
        x = get_tf(path)

    #df_up = pd.DataFrame(data_up)
    #df_down = pd.DataFrame(data_down)

    #df_up["METnoX"] = binning
    #df_up = df_up.set_index("METnoX")

    #df_down["METnoX"] = binning
    #df_down = df_down.set_index("METnoX")

    #draw_impact_vs_metnox(df_up, df_down, options.output)

if __name__ == "__main__":
    main()
