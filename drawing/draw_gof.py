import argparse
import uproot
import numpy as np
import matplotlib.pyplot as plt

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("fobs", type=str, help="File for observed result")
    parser.add_argument("ftoy", type=str, help="File with toy result")
    parser.add_argument("--xlabel", type=str, default=r'$-2\ln\lambda$',
                        help="X-axis label")
    parser.add_argument("-o", "--output", type=str, default="gof.pdf",
                        help="Output file")

    return parser.parse_args()

def read_limit(filename):
    with uproot.open(filename) as f:
        tree = f["limit"]
        limits = tree.array("limit")
    return limits

def draw_test_stat(toys, gof_obs, pvalue, xlabel, output):
    nbins = 50
    width = gof_obs / int(50 * gof_obs / toys.max())
    bins = np.arange(0., toys.max(), width)

    fig, ax = plt.subplots()

    ax.hist(toys[toys>gof_obs], bins=bins, color='red', label='1p-value = {:.3f}'.format(pvalue))
    ax.hist(toys, bins=bins, histtype='step', color='black', label='2Toys')
    ax.axvline(gof_obs, ls='--', lw=1, color='black', label='3Obs. = {:.3f}'.format(gof_obs))

    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(r'N toys', fontsize=12)

    ax.text(0.01, 1, r'$\mathbf{CMS}\ \mathit{Preliminary}$',
            ha='left', va='bottom', transform=ax.transAxes, fontsize=12)
    ax.text(0.99, 1, r'$35.9\ \mathrm{fb}^{-1}(13\ \mathrm{TeV})$',
            ha='right', va='bottom', transform=ax.transAxes, fontsize=12)

    handles, labels = ax.get_legend_handles_labels()
    idx, labels = zip(*[(int(label[0]), label[1:]) for label in labels])
    handles = [h for _, h in sorted(zip(idx, handles))]
    labels = [l for _, l in sorted(zip(idx, labels))]
    ax.legend(handles, labels)

    print("Creating {}".format(output))
    fig.savefig(output, format="pdf", bbox_inches="tight")
    plt.close(fig)

def main():
    options = parse_args()

    gof_obs = read_limit(options.fobs)[0]
    toys = read_limit(options.ftoy)

    nabove = toys[toys > gof_obs].shape[0]
    ntotal = toys.shape[0]
    pvalue = float(nabove) / ntotal

    draw_test_stat(toys, gof_obs, pvalue, options.xlabel, options.output)

if __name__ == "__main__":
    main()
