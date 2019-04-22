import argparse
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
import uproot

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("scan", type=str,
                        help="Input ROOT file with the NLL 2D scan")
    parser.add_argument("singles", type=str,
                        help="Input ROOT file with the best fit values")
    parser.add_argument("--onesigma", type=str, default=None,
                        help="Input ROOT file with the 68% contour")
    parser.add_argument("--twosigma", type=str, default=None,
                        help="Input ROOT file with the 95% contour")
    parser.add_argument("--xpoi", type=str, default="rz_ll",
                        help="Name of the x-axis poi")
    parser.add_argument("--ypoi", type=str, default="rz_nunu",
                        help="Name of the y-axis poi")
    parser.add_argument("-n", "--nbins", type=int, default=100,
                        help="Number of points scanned across in each "\
                             "dimension")
    parser.add_argument("--xrange", default="0.5,1.5", help="X-axis range")
    parser.add_argument("--yrange", default="0.5,1.5", help="Y-axis range")
    parser.add_argument("-o", "--outpath", type=str, default="ll2dscan.pdf",
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

def process_bestfit(path, xpoi, ypoi):
    with uproot.open(path) as f:
        limit = f["limit"]
    xpoi_vals, ypoi_vals = limit.arrays([xpoi, ypoi], outputtype=tuple)
    return xpoi_vals[0], ypoi_vals[0]

def process_scans(path, xpoi, ypoi):
    with uproot.open(path) as f:
        limit = f["limit"]
    xpoi_vals, ypoi_vals, nll_vals = limit.arrays(
        [xpoi, ypoi, "deltaNLL"], outputtype=tuple,
    )
    return xpoi_vals, ypoi_vals, 2.*nll_vals

def interpolate(xscan, yscan, zscan, xrange, yrange, nbins):
    x = np.unique(xscan)
    y = np.unique(yscan)
    X, Y = np.meshgrid(x, y)

    z_ix = np.vectorize({v: k for k, v in enumerate(x)}.get)(xscan)
    z_iy = np.vectorize({v: k for k, v in enumerate(y)}.get)(yscan)
    Z = -1*np.ones_like(X)
    for idx, (ix, iy) in enumerate(zip(z_ix, z_iy)):
        Z[iy, ix] = zscan[idx]
    Z[Z<0.] = np.nan

    Z = np.ma.masked_invalid(Z)
    X1 = X[~Z.mask]
    Y1 = Y[~Z.mask]
    Z1 = Z[~Z.mask]
    gd1 = griddata((X1, Y1), Z1.ravel(), (X, Y), method='linear')

    X = X.ravel()
    Y = Y.ravel()
    X_new = X[(xrange[0] < X) & (X < xrange[1]) & (yrange[0] < Y) & (Y < yrange[1])]
    Y_new = Y[(xrange[0] < X) & (X < xrange[1]) & (yrange[0] < Y) & (Y < yrange[1])]
    W_new = gd1.ravel()[(xrange[0] < X) & (X < xrange[1]) & (yrange[0] < Y) & (Y < yrange[1])]

    nbinsx = (xrange[1] - xrange[0]) / (X.max() - X.min()) * nbins
    nbinsy = (yrange[1] - yrange[0]) / (Y.max() - Y.min()) * nbins
    return X_new, Y_new, W_new, nbinsx, nbinsy

def main():
    options = parse_args()

    xpoi = options.xpoi
    ypoi = options.ypoi
    xrange = [float(x) for x in options.xrange.split(",")]
    yrange = [float(y) for y in options.yrange.split(",")]
    xbf, ybf = process_bestfit(options.singles, xpoi, ypoi)
    xscan, yscan, zscan = process_scans(options.scan, xpoi, ypoi)

    xscan = xscan[zscan>0.]
    yscan = yscan[zscan>0.]
    zscan = zscan[zscan>0.]
    zscan[zscan>10.] = 10.

    X_new, Y_new, W_new, nbinsx, nbinsy = interpolate(
        xscan, yscan, zscan, xrange, yrange, options.nbins,
    )

    xcont_one, ycont_one = None, None
    if options.onesigma:
        xcont_one, ycont_one, _ = process_scans(options.onesigma, xpoi, ypoi)
        xcont_one, ycont_one = sort_phi(xcont_one, ycont_one, xbf, ybf)
        xcont_one = np.array(list(xcont_one)+[xcont_one[0]])
        ycont_one = np.array(list(ycont_one)+[ycont_one[0]])

    xcont_two, ycont_two = None, None
    if options.twosigma:
        xcont_two, ycont_two, _ = process_scans(options.twosigma, xpoi, ypoi)
        xcont_two, ycont_two = sort_phi(xcont_two, ycont_two, xbf, ybf)
        xcont_two = np.array(list(xcont_two)+[xcont_two[0]])
        ycont_two = np.array(list(ycont_two)+[ycont_two[0]])

    draw(
        X_new, Y_new, W_new,
        xcont_one, ycont_one,
        xcont_two, ycont_two,
        xbf, ybf,
        nbinsx, nbinsy,
        outpath = options.outpath,
    )

def draw(x, y, w, xc1, yc1, xc2, yc2, xbf, ybf, nx, ny,
         xlab=r'$r_{\mu\mu}$', ylab=r'$r_{\nu\nu}$', outpath="ll2dscan.pdf"):
    fig, ax = plt.subplots(figsize=(5.4, 4.8))

    _, _, _, im  = ax.hist2d(x, y, bins=(nx, ny), weights=w, cmap='Blues')
    im.set_clim((0., 10))

    ax.set_xlabel(xlab, fontsize=12)
    ax.set_ylabel(ylab, fontsize=12)

    cb = fig.colorbar(im)
    cb.set_label(r'$q({},{})$'.format(
        xlab.replace("$", ""),
        ylab.replace("$", ""),
    ), fontsize=12)

    if (xbf-1) > 1e-5 or (ybf-1) > 1e-5:
        ax.plot(xbf, ybf, marker='*', color='red', label="Best fit", lw=0.)
    ax.plot(1, 1, marker='P', color='black', label="SM", lw=0.)

    if xc1 is not None and yc1 is not None:
        ax.plot(xc1, yc1, label='68\% CL', lw=1.2, color='black')
    if xc2 is not None and yc2 is not None:
        ax.plot(xc2, yc2, label='95\% CL', lw=1.2, ls='--', color='black')

    args = ax.get_legend_handles_labels()
    kwargs = {"fontsize": 12, "framealpha": 0.8, "labelspacing": 0.25}
    ax.legend(*args, **kwargs)
    ax.text(0.01, 1, r'$\mathbf{CMS}\ \mathit{Preliminary}$',
            ha='left', va='bottom', transform=ax.transAxes, fontsize=12)
    ax.text(0.99, 1, r'$35.9\ \mathrm{fb}^{-1}(13\ \mathrm{TeV})$',
            ha='right', va='bottom', transform=ax.transAxes, fontsize=12)

    print("Creating {}".format(outpath))
    fig.savefig(outpath, format="pdf", bbox_inches="tight")
    plt.close(fig)

if __name__ == "__main__":
    main()
