import argparse
import glob
import os
import re
import uproot
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.special import erf

try:
    import cPickle as pickle
except ImportError:
    import pickle

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("inputdir", type=str,
                        help="input root file with the MultiDimFit results")
    parser.add_argument("regex", type=str,
                        help="Regex to match the files")
    parser.add_argument("--POIs", type=str, default="r",
                        help="Comma-delimited POIs")
    parser.add_argument("--labels", type=str, default="{}",
                        help="Dict map for labels")
    parser.add_argument("--fitparams", type=str, default=None,
                        help="Input pickle with fit parameters")
    parser.add_argument("-o", "--output", type=str, default="trigger_efficiency",
                        help="Output file")

    return parser.parse_args()

def erf_func(x, a, b, c):
    return a*0.5*(1 + erf((x-b)/(np.sqrt(2)*c)))

def get_trigger_efficiencies(inputdir, regex_string, pois):
    regex = re.compile(regex_string)

    results = []
    for path in glob.glob(os.path.join(inputdir, "*")):
        match = regex.search(path)
        if not match:
            continue
        xrange = list(match.groups())
        if xrange[0] == "Inf":
            xrange[0] = -np.inf
        if xrange[-1] == "Inf":
            xrange[-1] = np.inf
        xrange = map(float, match.groups())
        f = uproot.open(path)
        t = f["limit"]
        results_pois = t.arrays(pois, outputtype=tuple)

        if results_pois[0].shape[0] == 0:
            continue

        result = {
            "xlow": xrange[0],
            "xupp": xrange[1],
        }
        for results_poi, poi in zip(results_pois, pois):
            up = results_poi.max()
            down = results_poi.min()
            result[poi] = results_poi[0] # best fit
            result[poi+"_up"] = results_poi.max() # up
            result[poi+"_down"] = results_poi.min() # down
        results.append(result)
    df = pd.DataFrame(results).sort_values("xlow", ascending=True)\
            .reset_index(drop=True)\
            .set_index(["xlow", "xupp"])
    return df

def draw_efficiencies(df, pois, output, label_map, fit_params):
    for poi in pois:
        df[poi+"_up"] = df[poi+"_up"] - df[poi]
        df[poi+"_down"] = df[poi] - df[poi+"_down"]

        bin_low = df.index.get_level_values("xlow").values
        bin_upp = df.index.get_level_values("xupp").values
        bin_cent = (bin_low + bin_upp)/2

        fig, ax = plt.subplots(
            nrows=1, ncols=1,
            figsize = (5.6, 4.8),
        )
        ax.set_xlabel(r'$p_{\mathrm{T}}^{\mathrm{miss}}$ (GeV)', fontsize=12)
        ax.set_ylabel(label_map.get(poi, poi), fontsize=12)

        with open(output+"_"+poi+".pkl", 'w') as f:
            pickle.dump((bin_cent, df[poi].values, df[[poi+"_up", poi+"_down"]].values.T), f)

        from scipy.optimize import curve_fit
        from scipy.special import erf
        def func(z, a, b, c):
            return 0.5*a*(1+erf((z-b)/(np.sqrt(2)*c)))
        popt, pcov = curve_fit(func, bin_cent[10:], df[poi].values[10:], p0=(1, -1000, 5000))
        popt = list(popt)
        if popt[0]>1:
            popt[0] = 1
        print(popt)

        ax.errorbar(
            bin_cent,
            df[poi].values,
            yerr = df[[poi+"_up", poi+"_down"]].values.T,
            fmt = 'o',
            markersize = 2,
            linewidth = 0.6,
            capsize = 1.8,
            color = 'black',
            zorder = 10,
        )

        z = np.linspace(bin_low.min(), 500, 1000)
        ax.plot(
            z,
            func(z, *popt),
            color='red',
            zorder = 20,
        )

        if fit_params is not None:
            with open(fit_params, 'r') as f:
                popt = pickle.load(f)
            x = np.linspace(bin_low.min(), 500, 1000)
            ax.plot(
                x,
                erf_func(x, *popt),
                color='red',
            )

        ax.axhline(1, ls='--', color='gray', zorder=5)

        ax.set_xlim((bin_low.min(), 500))#bin_upp.max()))
        ax.set_ylim((0, 1.1))

        ax.text(0.01, 1, r'$\mathbf{CMS}\ \mathit{Preliminary}$',
                ha='left', va='bottom', transform=ax.transAxes, fontsize=12)
        ax.text(0.99, 1, r'$35.9\ \mathrm{fb}^{-1}(13\ \mathrm{TeV})$',
                ha='right', va='bottom', transform=ax.transAxes, fontsize=12)

        print("Creating {}".format(output+"_"+poi+".pdf"))
        fig.savefig(output+"_"+poi+".pdf", format="pdf", bbox_inches="tight")
        plt.close(fig)

def main():
    options = parse_args()
    pois = options.POIs.split(",")

    # Get trigger efficiencies
    df = get_trigger_efficiencies(options.inputdir, options.regex, pois)
    draw_efficiencies(df, pois, options.output, eval(options.labels), options.fitparams)

if __name__ == "__main__":
    main()
