import argparse
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
import uproot

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("scan", type=str,
                        help="Input ROOT file with the NLL 2D scan")
    parser.add_argument("--onesigma", type=str, default=None,
                        help="Input ROOT file with the 68% contour")
    parser.add_argument("--twosigma", type=str, default=None,
                        help="Input ROOT file with the 95% contour")
    parser.add_argument("-n", "--nbins", type=int, default=100,
                        help="Number of points scanned across in each "\
                             "dimension")
    parser.add_argument("-o", "--output", type=str, default="ll2dscan.pdf",
                        help="Output file")

    return parser.parse_args()

def sort_phi(x, y, x0=1, y0=1):
    def calc_phi(p0, p1, c0=1, c1=1):
        phi = np.arctan(np.abs(np.divide((p1-c1), (p0-c0))))
        phi[(p0< c0) & (p1>=c1)] = np.pi   - phi[(p0< c0) & (p1>=c1)]
        phi[(p0< c0) & (p1< c1)] = np.pi   + phi[(p0< c0) & (p1< c1)]
        phi[(p0>=c0) & (p1< c1)] = 2*np.pi - phi[(p0>=c0) & (p1< c1)]
        return phi
    indices = np.argsort(calc_phi(x, y, x0, y0))
    return x[indices], y[indices]

def main():
    options = parse_args()

    rfile = uproot.open(options.scan)
    scan = rfile["limit"]
    arrays = scan.arrays(["r_mumu", "r_nunu", "deltaNLL"])

    # best fit points
    rmumu_bf = 1. #arrays["r_mumu"][0]
    rnunu_bf = 1. #arrays["r_nunu"][0]
    rmumu_sm = 1.
    rnunu_sm = 1.

    # scan
    rmumu = arrays["r_mumu"][1:]
    rnunu = arrays["r_nunu"][1:]
    nll = 2*arrays["deltaNLL"][1:]
    #rmumu = rmumu[nll>0]
    #rnunu = rnunu[nll>0]
    #nll = nll[nll>0]
    nll[nll>10.] = 10.

    x = np.unique(rmumu)
    y = np.unique(rnunu)
    X, Y = np.meshgrid(x, y)

    z_ix = np.vectorize({v: k for k, v in enumerate(x)}.get)(rmumu)
    z_iy = np.vectorize({v: k for k, v in enumerate(y)}.get)(rnunu)

    Z = -1*np.ones_like(X)
    for idx, (ix, iy) in enumerate(zip(z_ix, z_iy)):
        Z[iy, ix] = nll[idx]
    Z[Z<0.] = np.nan

    Z = np.ma.masked_invalid(Z)
    X1 = X[~Z.mask]
    Y1 = Y[~Z.mask]
    Z1 = Z[~Z.mask]
    gd1 = griddata((X1, Y1), Z1.ravel(), (X, Y), method='linear')

    fig, ax = plt.subplots(
        nrows=1, ncols=1,
        figsize = (5.06, 4.32),
    )

    xrange = (0.705, 1.295)
    yrange = (0.705, 1.295)

    X = X.ravel()
    Y = Y.ravel()
    X_new = X[(xrange[0] < X) & (X < xrange[1]) & (yrange[0] < Y) & (Y < yrange[1])]
    Y_new = Y[(xrange[0] < X) & (X < xrange[1]) & (yrange[0] < Y) & (Y < yrange[1])]
    W_new = gd1.ravel()[(xrange[0] < X) & (X < xrange[1]) & (yrange[0] < Y) & (Y < yrange[1])]

    nbinsx = (xrange[1] - xrange[0]) / (X.max() - X.min()) * options.nbins
    nbinsy = (yrange[1] - yrange[0]) / (Y.max() - Y.min()) * options.nbins

    _, _, _, im  = ax.hist2d(
        X_new, Y_new,
        bins = (nbinsx, nbinsy),
        weights = W_new,
        cmap = 'Blues',
    )
    im.set_clim((0., 10))

    ax.set_xlabel(r'$r_{\mu\mu}$', fontsize=12)
    ax.set_ylabel(r'$r_{\nu\nu}$', fontsize=12)

    cb = fig.colorbar(im)
    cb.set_label(r'$q(r_{\mu\mu},r_{\nu\nu})$', fontsize=12)

    if (rmumu_bf-1) > 1e-5 or (rnunu_bf-1) > 1e-5:
        ax.plot(rmumu_bf, rnunu_bf, marker='*', color='red', label="Best fit", lw=0.)
        pass
    ax.plot(rmumu_sm, rnunu_sm, marker='P', color='black', label="SM", lw=0.)
    #ax.text(rmumu_sm, rnunu_sm, "SM", fontsize=10, ha='center', va='center')

    if options.onesigma:
        rfile = uproot.open(options.onesigma)
        scan = rfile["limit"]
        arrays = scan.arrays(["r_mumu", "r_nunu", "deltaNLL"])

        rmumu_bf = arrays["r_mumu"][0]
        rnunu_bf = arrays["r_nunu"][0]

        rmumu = arrays["r_mumu"][1:]
        rnunu = arrays["r_nunu"][1:]
        nll = 2*arrays["deltaNLL"][1:]

        rmumu, rnunu = sort_phi(rmumu, rnunu, rmumu_bf, rnunu_bf)
        rmumu = np.append(rmumu, rmumu[0])
        rnunu = np.append(rnunu, rnunu[0])
        t = ax.plot(rmumu, rnunu, label="68\% CL", lw=1.2, color='black')
        #xy = t[0].get_xydata()

        #for x, y in xy[::10]:
        #    ax.text(x, y, "68\%", va='center', ha='center', fontsize=10)

    if options.twosigma:
        rfile = uproot.open(options.twosigma)
        scan = rfile["limit"]
        arrays = scan.arrays(["r_mumu", "r_nunu", "deltaNLL"])

        rmumu_bf = arrays["r_mumu"][0]
        rnunu_bf = arrays["r_nunu"][0]

        rmumu = arrays["r_mumu"][1:]
        rnunu = arrays["r_nunu"][1:]
        nll = 2*arrays["deltaNLL"][1:]

        rmumu, rnunu = sort_phi(rmumu, rnunu, rmumu_bf, rnunu_bf)
        rmumu = np.append(rmumu, rmumu[0])
        rnunu = np.append(rnunu, rnunu[0])
        t = ax.plot(rmumu, rnunu, label="95\% CL", lw=1.2, ls='--', color='black')
        #xy = t[0].get_xydata()

        #for x, y in xy[::8]:
        #    ax.text(x, y, "95\%", va='center', ha='center', fontsize=10)

    args = ax.get_legend_handles_labels()
    kwargs = {"fontsize": 12, "framealpha": 0.8, "labelspacing": 0.25}
    ax.legend(*args, **kwargs)
    ax.text(0.01, 1, r'$\mathbf{CMS}\ \mathit{Preliminary}$',
            ha='left', va='bottom', transform=ax.transAxes,
            fontsize=12)
    ax.text(0.99, 1, r'$35.9\ \mathrm{fb}^{-1}(13\ \mathrm{TeV})$',
            ha='right', va='bottom', transform=ax.transAxes,
            fontsize=12)

    #plt.tight_layout()
    fig.savefig(options.output, format="pdf", bbox_inches="tight")
    fig.savefig(options.output.replace("pdf", "png"), format="png", bbox_inches="tight")
    plt.close(fig)
    print("Created {}".format(options.output))

if __name__ == "__main__":
    main()
