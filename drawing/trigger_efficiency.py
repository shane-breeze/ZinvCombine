import argparse
import glob
import os
import re
import uproot
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.special import erf
from scipy.optimize import curve_fit

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
        print(path)
        f = uproot.open(path)
        t = f["limit"]
        if t.numentries == 0:
            continue
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
    if len(results)==0:
        return None
    df = pd.DataFrame(results).sort_values("xlow", ascending=True)\
            .reset_index(drop=True)\
            .set_index(["xlow", "xupp"])\
            .dropna()
    return df

def draw_efficiencies(df, pois, output, label_map, fit_params):
    df = df.iloc[:-1]
    print(df)
    for poi in pois:
        df.loc[:,poi+"_up"] = df.eval("{0}_up - {0}".format(poi))
        df.loc[:,poi+"_down"] = df.eval("{0} - {0}_down".format(poi))

        bin_low = df.index.get_level_values("xlow").values
        bin_upp = df.index.get_level_values("xupp").values
        bin_cent = (bin_low + bin_upp)/2

        fig, ax = plt.subplots(
            nrows=1, ncols=1,
            figsize = (5.6, 4.8),
        )
        ax.set_xlabel(r'$p_{\mathrm{T}}^{\mathrm{miss}}$ (GeV)', fontsize=12)
        ax.set_ylabel(label_map.get(poi, poi), fontsize=12)

        popt, pcov = curve_fit(erf_func, bin_cent[bin_cent>=150], df[poi].values[bin_cent>=150], p0=(1, 100, 50))
        popt = list(popt)
        print(popt)
        if popt[0]>1:
            popt[0] = 1

        ax.errorbar(
            bin_cent,
            df[poi].values,
            yerr = df[[poi+"_down", poi+"_up"]].values.T,
            fmt = 'o',
            markersize = 2,
            linewidth = 0.6,
            capsize = 1.8,
            color = 'black',
            zorder = 10,
        )

        #z = np.linspace(bin_low.min(), bin_upp.max(), 1000)
        z = np.linspace(100, bin_upp.max(), 1000)
        ax.plot(
            z,
            erf_func(z, *popt),
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

        #ax.set_xlim(bin_low.min(), bin_upp.max())
        ax.set_xlim(0, 1000)
        ax.set_ylim(0, 1.1)

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
    print(df)
    with open("trigger_df_fit.pkl", 'w') as f:
        pickle.dump(df, f)
    draw_efficiencies(df, pois, options.output, eval(options.labels), options.fitparams)

if __name__ == "__main__":
    main()
