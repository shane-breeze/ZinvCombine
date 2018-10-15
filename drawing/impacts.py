import argparse
import glob
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import numpy as np
import os
import re
import uproot

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("results_dir", type=str,
                        help="Directory with the desired results")
    parser.add_argument("-n", "--name", type=str, default="Exp",
                        help="String to add to regex")
    parser.add_argument("-o", "--output", type=str, default="impacts.pdf",
                        help="Output file")

    return parser.parse_args()

def get_fit_result(path, param):
    limit = uproot.open(path)["limit"]
    if limit.numentries == 0:
        return np.array([1., 1., 1.])
    return limit.array(param)

def get_fit_results(results_dir, regex_initial_fit, regex_param_fit):
    names = []
    nuisances = []
    impacts = []

    for path in glob.glob(os.path.join(results_dir, "*.root")):
        if regex_initial_fit.search(path):
            poi_nominal_fit = get_fit_result(path, 'r')

        match = regex_param_fit.search(path)
        if match:
            param = match.group("param")
            poi_fit = get_fit_result(path, 'r')
            nuis_fit = get_fit_result(path, param)

            names.append(param)
            nuisances.append(list(nuis_fit))
            impacts.append([poi_fit[1]-poi_fit[0], poi_fit[2]-poi_fit[0]])

    nuisances = np.array(nuisances)
    impacts = np.array(impacts)

    sort = np.argsort(np.mean(np.abs(impacts), axis=1))
    nuisances = nuisances[sort]
    impacts = impacts[sort]
    names = list(np.array(names)[sort])

    return names, nuisances, impacts, poi_nominal_fit

def draw_labels(axis, names):
    for idx in range(len(names)):
        axis.text(0.05, idx+0.5, str(len(names)-idx),
                  weight='bold', va='center')
        axis.text(0.25, idx+0.5, names[idx], va='center')
    return axis

def draw_errorbar(axis, values):
    nvals = values.shape[0]
    xpos = values[:,0]
    xerr = values[:,1:].T-xpos
    xerr[0,:] *= -1
    axis.errorbar(
        xpos, np.linspace(0.5, nvals-0.5, nvals), xerr=xerr, yerr=None,
        fmt='o', color='black', markersize=4, lw=1.5, capsize=3,
        label='Pull',
    )
    return axis

def draw_barhs(axis, values):
    nvals = values.shape[0]
    axis.barh(range(nvals), width=values[:,0], height=1, color='#80b1d3',
              align='edge', label=r'$+1\sigma$ impact')
    axis.barh(range(nvals), width=values[:,1], height=1, color='#fb8072',
              align='edge', label=r'$-1\sigma$ impact')
    return axis

def draw_odd_boxes(axis):
    xlim = axis.get_xlim()
    ylim = axis.get_ylim()

    boxes = [Rectangle((xlim[0], ylim[1]-idx), xlim[1]-xlim[0], -1)
             for idx in range(int(ylim[1]))[1::2]]
    axis.add_collection(PatchCollection(boxes, facecolor='gray', alpha=0.25))
    return axis

def draw_impacts(names, nuisances, impacts, bestfit, output):
    nnuis = nuisances.shape[0]

    # Figure
    fig, (axl, axm, axr) = plt.subplots(
        nrows=1, ncols=3, sharey=True,
        figsize = (6.4, 4.8),
        gridspec_kw = {
            'width_ratios': [0.8,1,1],
            'wspace': 0.
        },
    )

    # Left axis
    axl.axis('off')
    axl.set_xlim((0., 1.))
    axl.set_ylim((0., nnuis))
    draw_labels(axl, names)

    # Middle axis
    draw_errorbar(axm, nuisances)
    axm.set_xlim((-2.9, 2.9))
    axm.set_xlabel(r'$(\hat{\theta}-\theta_0)/\Delta\theta$', fontsize='large')

    # Right axis
    draw_barhs(axr, impacts)
    xmax = np.abs(axr.get_xlim()).max()
    axr.set_xlim((-xmax, xmax))
    axr.set_xlabel(r'$\Delta\hat{r}$', fontsize='large')

    # Middle axis - Ticks
    axm.xaxis.set_major_locator(MultipleLocator(1))
    axm.xaxis.set_major_formatter(FormatStrFormatter('%d'))
    axm.xaxis.set_tick_params(which='major', direction='in',
                              top=True, bottom=True, labelsize=8)
    axm.yaxis.set_tick_params(which='both', left=False, right=False)
    axm.grid(True, axis='x', color='black', lw=1, ls=':')

    # Right axis - Ticks
    axr.xaxis.set_tick_params(which='both', direction='in',
                              top=True, bottom=True, labelsize=8)
    axr.yaxis.set_tick_params(which='both', left=False, right=False)
    axr.grid(True, axis='x', color='black', lw=1, ls=':')

    # Draw gray background boxes for each odd numbered nuisance (starting from
    # zero)
    draw_odd_boxes(axl)
    draw_odd_boxes(axm)
    draw_odd_boxes(axr)

    # Legend
    handles_m, labels_m = axm.get_legend_handles_labels()
    handles_r, labels_r = axr.get_legend_handles_labels()
    axl.legend(handles_m+handles_r, labels_m+labels_r,
               bbox_to_anchor=(0.9, 0.02), labelspacing=0.1,
               handlelength=1, handletextpad=0.2,
               columnspacing=0.8)

    # CMS stamp
    axm.text(0, 1, r'$\mathbf{CMS}\ \mathit{Preliminary}$',
             ha='left', va='bottom', transform=axm.transAxes,
             fontsize='large')

    # best fit stamp
    axr.text(1, 1,
             r'$\hat{{r}} = {:.3f}^{{+{:.3f}}}_{{-{:.3f}}}$'.format(
                 bestfit[0], bestfit[2]-bestfit[0], bestfit[0]-bestfit[1],
             ), ha='right', va='bottom', transform=axr.transAxes,
             fontsize='large')

    plt.tight_layout()
    fig.savefig(output, format="pdf", bbox_inches="tight")
    plt.close(fig)
    print("Created {}".format(output))

def main():
    options = parse_args()

    regex_initial_fit = re.compile("higgsCombineNominalFit{}\.MultiDimFit\.mH120\.root".format(options.name))
    regex_param_fit = re.compile("higgsCombineNuisFit{}_(?P<param>[^_^.]*)\.MultiDimFit\.mH120\.root".format(options.name))

    names, nuisances, impacts, bestfit = get_fit_results(
        options.results_dir,
        regex_initial_fit,
        regex_param_fit,
    )
    draw_impacts(names, nuisances, impacts, bestfit, options.output)

if __name__ == "__main__":
    main()
