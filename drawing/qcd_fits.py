import uproot
import pandas as pd
import autograd.numpy as np
import matplotlib.pyplot as plt
import argparse
from scipy.optimize import curve_fit
from scipy.stats import t
from scipy.special import gammaincinv
from scipy.interpolate import interp1d
from autograd import jacobian

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input file")
    parser.add_argument("-o", "--output", default="fit.pdf", help="Output file")
    parser.add_argument("-b", "--binning", default="[200]", help="List of bins")
    return parser.parse_args()

def get_fit(func, xs, fitrange, ys, confprob, **curve_fit_kwargs):
    # least squares curve fit with errors on y
    if "absolute_sigma" not in curve_fit_kwargs:
        curve_fit_kwargs["absolute_sigma"] = True
    popt, pcov = curve_fit(func, xs, ys, **curve_fit_kwargs)
    x = np.linspace(fitrange[0], fitrange[1], 1001)

    norm = False
    if norm:
        alpha = 1.0 - confprob
        prb = 1.0 - alpha/2.
        corr_factor = t.ppf(prb, ys.shape[0]-popt.shape[0])
    else:
        corr_factor = 2.*gammaincinv(0.5, 0.68)

    func2 = lambda xcare, pcare: func(xcare, *pcare)
    dfdp = jacobian(func2, argnum=1)(x, popt)
    if popt.shape[0]>1:
        df = np.sqrt(np.array([
            np.dot(dfdp[i,:], np.matmul(pcov, dfdp.T)[:,i])
            for i in range(x.shape[0])
        ]))
    else:
        df = dfdp[0]*np.sqrt(pcov[0,0])

    y = func(x, *popt)
    delta  = corr_factor * df
    return x, y, delta

def get_hist(pathname):
    filename, histname = pathname.split(":")
    with uproot.open(filename) as f:
        hist = f[histname].pandas()

    xlow = np.array([x.left for x in hist.index.values])
    xhigh = np.array([x.right for x in hist.index.values])
    count = hist["count"].values
    errs = np.sqrt(hist["variance"].values)
    return xlow, xhigh, count, errs

def draw(xpoints, xpoints_err, ypoints, ypoints_err, xs, ys_const, ys_linear, errs_const, errs_linear, output):
    fig, (axtop, axbot) = plt.subplots(
        nrows=2, ncols=1, sharex='col', sharey=False,
        gridspec_kw={'height_ratios': [3, 1],
                     'wspace': 0.1,
                     'hspace': 0.1},
        figsize = (4.8, 6),
    )

    axtop.errorbar(
        xpoints, ypoints, xerr=xpoints_err, yerr=ypoints_err,
        label = '(data-bkg)/sig',
        fmt='o', markersize=4, linewidth=0.6, capsize=2.5, color="black",
        zorder=5,
    )
    axtop.plot(xs, ys_const, color='#e31a1c', label='Const. fit', zorder=4)
    axtop.plot(xs, ys_linear, color='#1f78b4', label='Linear fit', zorder=2)

    axtop.fill_between(
        xs, ys_const-errs_const, ys_const+errs_const,
        color='#e31a1c', alpha=0.3, zorder=3,
    )

    axtop.fill_between(
        xs, ys_linear-errs_linear, ys_linear+errs_linear,
        color='#1f78b4', alpha=0.3, zorder=1,
    )

    axtop.axvspan(0, 40, alpha=0.3, color='gray', label='SR')

    axtop.set_ylabel(r'QCD scale factor', fontsize=12)

    axtop.text(0.01, 1, r'$\mathbf{CMS}\ \mathit{Preliminary}$',
               ha='left', va='bottom', transform=axtop.transAxes, fontsize=12)
    axtop.text(0.99, 1, r'$35.9\ \mathrm{fb}^{-1}(13\ \mathrm{TeV})$',
               ha='right', va='bottom', transform=axtop.transAxes, fontsize=12)
    axtop.legend(*axtop.get_legend_handles_labels())

    axtop.set_xlim(xs.min(), xs.max())

    # bottom axis
    axbot.plot(xs, ys_const-ys_const, color='#e31a1c')
    axbot.plot(xs, ys_linear-ys_const, color='#1f78b4')

    errs = np.sqrt(errs_linear**2 - errs_const**2)
    axbot.fill_between(
        xs, ys_linear-ys_const-errs, ys_linear-ys_const+errs,
        color='#1f78b4', alpha=0.3,
    )

    axbot.axvspan(0, 40, alpha=0.3, color='gray', label='SR')
    axbot.set_xlabel(
        r'$p_{\mathrm{T}}(\mathrm{jet\ nearest\ }p_{\mathrm{T}}^{\mathrm{miss}})$ (GeV)',
        fontsize = 12,
    )
    axbot.set_ylabel(r'Linear - Const.', fontsize=12)

    fig.savefig(output, format="pdf", bbox_inches="tight")
    print("Created {}".format(output))

def draw_full(xs, ycons, errcons, ylins, errlins, output):
    fig, (axtop, axbot) = plt.subplots(
        nrows=2, ncols=1, sharex='col', sharey=False,
        gridspec_kw={'height_ratios': [3, 1],
                     'wspace': 0.1,
                     'hspace': 0.1},
        figsize = (4.8, 6),
    )

    errs = np.sqrt(errlins**2 - errcons**2)

    bins = np.array(list(xs)+[1000.])
    axtop.hist(xs, bins=bins, weights=ycons, histtype='step', label="Const.", color='#e31a1c', zorder=5)
    axtop.hist(xs, bins=bins, weights=ylins, histtype='step', label="Linear", color='#1f78b4', zorder=5)

    low = ylins-errs
    low = np.array(list(low)+[low[-1]])
    hig = ylins+errs
    hig = np.array(list(hig)+[hig[-1]])
    axtop.fill_between(
        bins, low, hig, step='post', color='#1f78b4', alpha=0.3, zorder=3,
    )

    axtop.set_ylabel("QCD scale factor", fontsize=12)
    axtop.set_xlim(bins.min(), bins.max())
    axtop.text(0.01, 1, r'$\mathbf{CMS}\ \mathit{Preliminary}$',
               ha='left', va='bottom', transform=axtop.transAxes, fontsize=12)
    axtop.text(0.99, 1, r'$35.9\ \mathrm{fb}^{-1}(13\ \mathrm{TeV})$',
               ha='right', va='bottom', transform=axtop.transAxes, fontsize=12)
    axtop.legend(*axtop.get_legend_handles_labels(), loc=1)

    axbot.hist(xs, bins=bins, weights=ylins-ycons, histtype='step', color='black')
    low = ylins-ycons-errs
    low = np.array(list(low)+[low[-1]])
    hig = ylins-ycons+errs
    hig = np.array(list(hig)+[hig[-1]])
    axbot.fill_between(
        bins, low, hig, step='post', color='gray', alpha=0.3,
    )

    #yrange = 1.05*np.abs(ylins-ycons).max()
    #axbot.set_ylim(-yrange, yrange)
    axbot.axhline(0., lw=1, ls='--', color='black')

    axbot.set_xlabel(r'$p_{\mathrm{T}}^{\mathrm{miss}}$ (GeV)', fontsize=12)
    axbot.set_ylabel(r'Linear - Const.', fontsize=12)

    fig.savefig(output, format='pdf', bbox_inches='tight')
    print("Created {}".format(output))

    return pd.DataFrame(
        {"x": xs, "qcd_syst": ylins-ycons, "qcd_syst_bin": errs},
        columns=["x", "qcd_syst", "qcd_syst_bin"],
    )

def process(input, output):
    xlow, xhigh, data, _ = get_hist("{}:monojetqcd/data_obs".format(input))
    _, _, signal, signal_err = get_hist("{}:monojetqcd/qcd".format(input))
    _, _, wlnu, wlnu_err = get_hist("{}:monojetqcd/wlnu_qcd".format(input))
    _, _, bkg, bkg_err = get_hist("{}:monojetqcd/bkg".format(input))

    print(signal**2/signal_err**2)

    bkg += wlnu
    bkg_err = np.sqrt(bkg_err**2 + wlnu_err**2)

    bins = np.array(list(xlow)+[xhigh[-1]])
    xs = (bins[1:] + bins[:-1])/2
    ys = (data - bkg) / signal
    ys_err = ys*np.sqrt((data+bkg_err**2)/(data-bkg)**2 + signal_err**2/signal**2)

    def const(x, p0):
        return p0*np.ones_like(x)
    def linear(x, p0, p1):
        return p0 + x*p1

    x, ycon, errcon = get_fit(const, xs, (0., 1000.), ys, 0.68, sigma=ys_err)
    _, ylin, errlin = get_fit(linear, xs, (0., 1000.), ys, 0.68, sigma=ys_err)

    draw(xs, bins[1:]-xs, ys, ys_err, x, ycon, ylin, errcon, errlin, output)
    return ycon, errcon, ylin, errlin

def main():
    options = parse_args()
    xs = []
    ycons, errcons = [], []
    ylins, errlins = [], []
    for bin in eval(options.binning):
        xs.append(float(bin))
        input = options.input.format(bin)
        output = options.output.format(bin)
        ycon, errcon, ylin, errlin = [p[0] for p in process(input, output)]
        ycons.append(ycon)
        errcons.append(errcon)
        ylins.append(ylin)
        errlins.append(errlin)

    xs = np.array(xs)
    ycons = np.array(ycons)
    errcons = np.array(errcons)
    ylins = np.array(ylins)
    errlins = np.array(errlins)

    df = draw_full(xs, ycons, errcons, ylins, errlins, "fit_met.pdf")
    xrebin = [200,220,250,280,310,340,370,400,430,470,510,550,590,640,690,740,790,840,900,960,1020]
    newdf = pd.DataFrame({"x": xrebin})
    newdf["qcd_syst"] = interp1d(
        df["x"], df["qcd_syst"],
        kind = 'linear',
        fill_value = 'extrapolate',
    )(xrebin)
    newdf.loc[xrebin>df["x"].max(), "qcd_syst"] = df["qcd_syst"].iloc[-1]
    newdf.loc[xrebin<df["x"].min(), "qcd_syst"] = df["qcd_syst"].iloc[0]
    newdf["qcd_syst_bin"] = interp1d(
        df["x"], df["qcd_syst_bin"],
        kind = 'nearest',
        fill_value = 'extrapolate',
    )(xrebin)
    newdf.loc[xrebin>df["x"].max(), "qcd_syst_bin"] = df["qcd_syst_bin"].iloc[-1]
    newdf.loc[xrebin<df["x"].min(), "qcd_syst_bin"] = df["qcd_syst_bin"].iloc[0]
    for i in range(df.shape[0]):
        qcd_syst_interp = newdf["qcd_syst_bin"].values
        qcd_syst_bin = np.zeros_like(qcd_syst_interp)
        mask = (qcd_syst_interp == df["qcd_syst_bin"].iloc[i])
        qcd_syst_bin[mask] = qcd_syst_interp[mask]
        newdf["qcd_syst_bin{}".format(i)] = qcd_syst_bin
    newdf = newdf.drop("qcd_syst_bin", axis=1)
    print(df.to_string())
    print(newdf.to_string())
    newdf.to_csv("qcd_systs.txt", index=None, sep=' ')

if __name__ == "__main__":
    main()
