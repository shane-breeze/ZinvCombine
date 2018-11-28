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
    parser.add_argument("--poi", type=str, default="r", help="POI")
    parser.add_argument("-o", "--output", type=str, default="ll1dscan.pdf",
                        help="Output file")

    return parser.parse_args()

def main():
    options = parse_args()
    poi_name = options.poi

    # expected
    rfile_exp = uproot.open(options.scan_exp)
    scan_exp = rfile_exp["limit"]
    arrays_exp = scan_exp.arrays([poi_name, "deltaNLL"])
    poi_exp = arrays_exp[poi_name][1:]
    nll_exp = 2*arrays_exp["deltaNLL"][1:]

    fig, ax = plt.subplots(
        nrows=1, ncols=1,
        figsize = (4.8, 4.8),
    )
    #ax.set_xlabel(r'$\Gamma(\mathrm{Z}\rightarrow\nu\nu)$', fontsize=12)
    ax.set_xlabel(r'$r$', fontsize=12)
    ax.set_ylabel(r'$-2\Delta \ln \mathcal{L}$', fontsize=12)

    # expected
    ax.plot(poi_exp, nll_exp, marker='o', markersize=1.5, color='black',
            label="Exp.", lw=1.2, zorder=2)

    # observed
    obs_min, obs_max = None, None
    if options.scan_obs:
        rfile_obs = uproot.open(options.scan_obs)
        scan_obs = rfile_obs["limit"]
        arrays_obs = scan_obs.arrays([poi_name, "deltaNLL"])
        poi_obs = arrays_obs[poi_name][1:]
        nll_obs = 2*arrays_obs["deltaNLL"][1:]
        ax.plot(poi_obs, nll_obs, marker='o', markersize=1.5, color='red',
                label="Obs.", lw=1.2, zorder=2)

        obs_min = poi_obs.min()
        obs_max = poi_obs.max()

    xmin = poi_exp.min() if obs_min is None else min(poi_exp.min(), obs_min)
    xmax = poi_exp.max() if obs_max is None else max(poi_exp.max(), obs_max)

    ax.set_xlim((xmin, xmax))
    ax.set_ylim((0., 8.))

    handles, labels = ax.get_legend_handles_labels()
    if options.singles_exp:
        rfile_exp = uproot.open(options.singles_exp)
        singles_exp = rfile_exp["limit"]
        poi_exp = singles_exp.array(poi_name)

        poi = poi_exp[0]
        poi_up = poi_exp.max()-poi
        poi_down = poi-poi_exp.min()

        exp_text = r'{:.3f}^{{+{:.3f}}}_{{-{:.3f}}}$'.format(poi, poi_up, poi_down)
        labels[0] += " " + r'$r=' + exp_text
        #labels[0] = r'$\Gamma_{\mathrm{exp.}}(\mathrm{Z}\rightarrow\nu\nu) = ' + exp_text

    if options.singles_obs:
        rfile_obs = uproot.open(options.singles_obs)
        singles_obs = rfile_obs["limit"]
        poi_obs = singles_obs.array(poi_name)

        poi = poi_obs[0]
        poi_up = poi_obs.max()-poi
        poi_down = poi-poi_obs.min()

        obs_text = r'$r={:.3f}^{{+{:.3f}}}_{{-{:.3f}}}$'.format(poi, poi_up, poi_down)
        labels[1] += " " + obs_text

    xmin, xmax = ax.get_xlim()
    ax.axhline(1, ls='--', lw=1.2, color='gray', zorder=1)
    ax.text(0.99*xmin+0.01*xmax, 1, r'$1\sigma$', ha='left', va='bottom',
            color='gray', zorder=1)
    ax.axhline(4, ls='--', lw=1.2, color='gray', zorder=1)
    ax.text(0.99*xmin+0.01*xmax, 4, r'$2\sigma$', ha='left', va='bottom',
            color='gray', zorder=1)

    ax.legend(handles, labels)
    ax.text(0.01, 1, r'$\mathbf{CMS}\ \mathit{Preliminary}$',
            ha='left', va='bottom', transform=ax.transAxes,
            fontsize=12)
    ax.text(0.99, 1, r'$35.9\ \mathrm{fb}^{-1}(13\ \mathrm{TeV})$',
            ha='right', va='bottom', transform=ax.transAxes,
            fontsize=12)

    fig.savefig(options.output, format="pdf", bbox_inches="tight")
    plt.close(fig)
    print("Created {}".format(options.output))

if __name__ == "__main__":
    main()
