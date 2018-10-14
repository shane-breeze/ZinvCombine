import argparse
import matplotlib.pyplot as plt
import numpy as np
import uproot

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
    parser.add_argument("-o", "--output", type=str, default="ll1dscan.pdf",
                        help="Output file")

    return parser.parse_args()

def main():
    options = parse_args()

    # expected
    rfile_exp = uproot.open(options.scan_exp)
    scan_exp = rfile_exp["limit"]
    arrays_exp = scan_exp.arrays(["r", "deltaNLL"])
    poi_exp = arrays_exp["r"][1:]
    nll_exp = 2*arrays_exp["deltaNLL"][1:]

    fig, ax = plt.subplots(
        nrows=1, ncols=1,
        figsize = (4.8, 4.8),
    )
    ax.set_xlabel(r'$r$', fontsize='large')
    ax.set_ylabel(r'$-2\Delta \ln \mathcal{L}$', fontsize='large')

    # expected
    ax.plot(poi_exp, nll_exp, marker='o', markersize=1.5, color='black', label="Exp", lw=1.2)

    # observed
    if options.scan_obs:
        rfile_obs = uproot.open(options.scan_obs)
        scan_obs = rfile_obs["limit"]
        arrays_obs = scan_obs.arrays(["r", "deltaNLL"])
        poi_obs = arrays_obs["r"][1:]
        nll_obs = 2*arrays_obs["deltaNLL"][1:]
        ax.plot(poi_obs, nll_obs, marker='o', markersize=1.5, color='red', label="Obs", lw=1.2)

    ax.set_xlim((min(poi_exp.min(), poi_obs.min()), max(poi_exp.max(), poi_exp.max())))
    ax.set_ylim((0., 8.))

    handles, labels = ax.get_legend_handles_labels()
    if options.singles_exp:
        rfile_exp = uproot.open(options.singles_exp)
        singles_exp = rfile_exp["limit"]
        poi_exp = singles_exp.array("r")

        poi = poi_exp[0]
        poi_up = poi_exp.max()-poi
        poi_down = poi-poi_exp.min()

        exp_text = r'$r={:.3f}^{{+{:.3f}}}_{{-{:.3f}}}$'.format(poi, poi_up, poi_down)
        labels[0] += " " + exp_text

    if options.singles_obs:
        rfile_obs = uproot.open(options.singles_obs)
        singles_obs = rfile_obs["limit"]
        poi_obs = singles_obs.array("r")

        poi = poi_obs[0]
        poi_up = poi_obs.max()-poi
        poi_down = poi-poi_obs.min()

        obs_text = r'$r={:.3f}^{{+{:.3f}}}_{{-{:.3f}}}$'.format(poi, poi_up, poi_down)
        labels[1] += " " + obs_text

    xmin, xmax = ax.get_xlim()
    ax.axhline(1, ls='--', lw=1.2, color='gray')
    ax.text(0.99*xmin+0.01*xmax, 1, r'$1\sigma$', ha='left', va='bottom', color='gray')
    ax.axhline(4, ls='--', lw=1.2, color='gray')
    ax.text(0.99*xmin+0.01*xmax, 4, r'$2\sigma$', ha='left', va='bottom', color='gray')

    ax.legend(handles, labels)
    ax.text(0, 1, r'$\mathbf{CMS}\ \mathit{Preliminary}$',
            ha='left', va='bottom', transform=ax.transAxes,
            fontsize='large')
    ax.text(1, 1, r'$35.9\ \mathrm{fb}^{-1}(13\ \mathrm{TeV})$',
            ha='right', va='bottom', transform=ax.transAxes,
            fontsize='large')

    plt.tight_layout()
    fig.savefig(options.output, format="pdf", bbox_inches="tight")
    plt.close(fig)
    print("Created {}".format(options.output))

if __name__ == "__main__":
    main()
