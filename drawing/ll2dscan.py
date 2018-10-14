import argparse
import matplotlib.pyplot as plt
import numpy as np
import uproot

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("scan", type=str,
                        help="Input ROOT file with the NLL 2D scan")
    parser.add_argument("--onesigma", type=str, default=None,
                        help="Input ROOT file with the 68% contour")
    parser.add_argument("--twosigma", type=str, default=None,
                        help="Input ROOT file with the 68% contour")
    parser.add_argument("-o", "--output", type=str, default="ll2dscan.pdf",
                        help="Output file")

    return parser.parse_args()

def sort_phi(x, y):
    def calc_phi(p0, p1):
        phi = np.arctan(np.abs(np.divide((p1-1), (p0-1))))
        phi[(p0< 1) & (p1>=1)] = np.pi - phi[(p0< 1) & (p1>=1)]
        phi[(p0< 1) & (p1< 1)] = np.pi + phi[(p0< 1) & (p1< 1)]
        phi[(p0>=1) & (p1< 1)] = 2*np.pi - phi[(p0>=1) & (p1< 1)]
        return phi
    indices = np.argsort(calc_phi(x, y))
    return x[indices], y[indices]

def main():
    options = parse_args()

    rfile = uproot.open(options.scan)
    scan = rfile["limit"]
    arrays = scan.arrays(["r_mumu", "r_nunu", "deltaNLL"])

    # best fit points
    rmumu_bf = arrays["r_mumu"][0]
    rnunu_bf = arrays["r_nunu"][0]
    rmumu_sm = 1.
    rnunu_sm = 1.

    # scan
    rmumu = arrays["r_mumu"][1:]
    rnunu = arrays["r_nunu"][1:]
    nll = 2*arrays["deltaNLL"][1:]
    nll[nll>10.] = 10.

    fig, ax = plt.subplots(
        nrows=1, ncols=1,
        figsize = (5.6, 4.8),
    )

    _, _, _, im = ax.hist2d(
        rmumu,
        rnunu,
        bins = (60, 60),
        weights = nll,
        cmap = 'Blues',
    )

    ax.set_xlabel(r'$r_{\mu\mu}$', fontsize='large')
    ax.set_ylabel(r'$r_{\mathrm{inv.}}$', fontsize='large')

    cb = fig.colorbar(im)
    cb.set_label(r'$q(r_{\mu\mu},r_{\mathrm{inv.}})$', fontsize='large')

    if (rmumu_bf-1) > 1e-5 or (rnunu_bf-1) > 1e-5:
        ax.plot(rmumu_bf, rnunu_bf, marker='*', color='red', label="Best fit", lw=0.)
    ax.plot(rmumu_sm, rnunu_sm, marker='P', color='black', label="SM", lw=0.)

    if options.onesigma:
        rfile = uproot.open(options.onesigma)
        scan = rfile["limit"]
        arrays = scan.arrays(["r_mumu", "r_nunu", "deltaNLL"])

        rmumu = arrays["r_mumu"][1:]
        rnunu = arrays["r_nunu"][1:]
        nll = 2*arrays["deltaNLL"][1:]

        rmumu, rnunu = sort_phi(rmumu, rnunu)
        rmumu = np.append(rmumu, rmumu[0])
        rnunu = np.append(rnunu, rnunu[0])
        ax.plot(rmumu, rnunu, label="68% CL", lw=1.2, color='black')

    if options.twosigma:
        rfile = uproot.open(options.twosigma)
        scan = rfile["limit"]
        arrays = scan.arrays(["r_mumu", "r_nunu", "deltaNLL"])

        rmumu = arrays["r_mumu"][1:]
        rnunu = arrays["r_nunu"][1:]
        nll = 2*arrays["deltaNLL"][1:]

        rmumu, rnunu = sort_phi(rmumu, rnunu)
        rmumu = np.append(rmumu, rmumu[0])
        rnunu = np.append(rnunu, rnunu[0])
        ax.plot(rmumu, rnunu, label="95% CL", lw=1.2, ls='--', color='black')

    ax.legend(*ax.get_legend_handles_labels())
    ax.text(0, 1.005, r'$\mathbf{CMS}\ \mathit{Preliminary}$',
            ha='left', va='bottom', transform=ax.transAxes,
            fontsize='large')
    ax.text(1, 1.005, r'$35.9\ \mathrm{fb}^{-1}(13\ \mathrm{TeV})$',
            ha='right', va='bottom', transform=ax.transAxes,
            fontsize='large')

    plt.tight_layout()
    fig.savefig(options.output, format="pdf", bbox_inches="tight")
    plt.close(fig)
    print("Created {}".format(options.output))

if __name__ == "__main__":
    main()
