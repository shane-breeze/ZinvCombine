import argparse
import uproot
import numpy as np
import matplotlib.pyplot as plt

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, help="Input path")
    parser.add_argument("-r", "--regions", type=str, default="monojet",
                        help="List of regions to process")
    parser.add_argument("--doratio", action='store_true', default=False,
                        help="Plot the ratio")
    parser.add_argument("--dopull", action='store_true', default=False,
                        help="Plot the pulls")
    return parser.parse_args()

color_procs = {
    "bkg":      "#d9d9d9",
    "wlnu":     "#b3de69",
    "wlnu_qcd": "#b3de69",
    "qcd":      "#fb8072",
    "znunu":    "#80b1d3",
    "zmumu":    "#ffed6f",
    "gsmumu":   "#fdbf6f",
    "zee":      "#ffed6f",
    "gsee":     "#fdbf6f",
}

proc_names = {
    "bkg":      "Backgrounds",
    "wlnu":     r'$\mathrm{W}_{l\nu} + \mathrm{jets}$',
    "wlnu_qcd": r'$\mathrm{W}_{l\nu} + \mathrm{jets}$',
    "qcd":      "QCD Multijet",
    "znunu":    r'$\mathrm{Z}_{\nu\nu} + \mathrm{jets}$',
    "zmumu":    r'$\mathrm{Z}_{\mu\mu} + \mathrm{jets}$',
    "gsmumu":   r'$\gamma^{*}_{\mu\mu} + \mathrm{jets}$',
    "zee":      r'$\mathrm{Z}_{ee} + \mathrm{jets}$',
    "gsee":     r'$\gamma^{*}_{ee} + \mathrm{jets}$',
}

conv_region = {
    "monojet":     r'Signal Region',
    "monojetqcd":  r'QCD Sideband',
    "singlee":     r'Single Electron',
    "singleeqcd":  r'Single Electron QCD',
    "singlemu":    r'Single Muon',
    "singlemuqcd": r'Single Muon QCD',
    "singletau":   r'Single Tau',
    "doublee":     r'Double Electron',
    "doublemu":    r'Double Muon',
}


#bin_real_vals = np.array([200,210,220,230,250,275,300,350,400,500,600,800])
bin_real_vals = np.array([200,220,250,280,310,340,370,400,430,470,510,550,590,640,690,740,790,840,900,960,1020,1100])
#bin_real_vals = np.array([40,100,150,200,300,500])
#bin_real_vals = np.array([40,60,80,100,150,200,250,300,400,500,750,1000])
#bin_real_vals = np.array([0,1,2])
#bin_real_vals = np.array([100,120,140,160,180,200,220,240,260,280,300,340,380,420,500,600,800,1000])

def draw(data, total_bkg, total_bkg_prefit, mc_procs, region_name, output, doratio, dopull):
    nrows = 1
    height_ratios = [3]
    ratio_idx = 0
    pull_idx = 0
    if doratio:
        nrows += 1
        height_ratios.append(1)
        ratio_idx += 1
        pull_idx += 1
    if dopull:
        nrows += 1
        height_ratios.append(1)
        pull_idx += 1
    fig, axes = plt.subplots(
        nrows=nrows, ncols=1, sharex='col', sharey=False,
        gridspec_kw={'height_ratios': height_ratios,
                     'wspace': 0.1,
                     'hspace': 0.1},
        figsize = (5.0, 6.0),
    )
    if nrows>1:
        axtop = axes[0]
        axbot = axes[-1]
    else:
        axtop = axes
        axbot = axes

    bins_low = np.array([b.left for b in total_bkg.index.get_level_values("bins").values])
    bins_upp = np.array([b.right for b in total_bkg.index.get_level_values("bins").values])

    bins_low = bin_real_vals[:-1]
    bins_upp = bin_real_vals[1:]

    bins = np.array(list(bins_low)+[bins_upp[-1]])
    bins_cent = (bins_low+bins_upp)/2

    #data = data.reindex(bins[:-1])
    #data[np.isnan(data)] = 0.
    #total_bkg = total_bkg.reindex(bins[:-1])
    #total_bkg[np.isnan(data)] = 0.
    #total_bkg_prefit = total_bkg_prefit.reindex(bins[:-1])

    mc_procs_sorted = sorted(mc_procs.items(), key=lambda kv: kv[1]["count"].sum())
    mc_procs_sorted_names = [k for k, v in mc_procs_sorted]
    mc_procs_sorted = [v["count"].values for k, v in mc_procs_sorted]

    axtop.hist(
        [bins_cent]*len(mc_procs_sorted),
        bins = bins,
        weights = mc_procs_sorted,
        stacked = True,
        color = [color_procs[proc] for proc in mc_procs_sorted_names],
        label = [proc_names[proc] for proc in mc_procs_sorted_names],
        zorder = 1,
    )

    axtop.hist(
        bins_cent,
        bins = bins,
        weights = total_bkg["count"],
        histtype = 'step',
        color = 'black',
        label = 'Postfit',
        zorder = 2,
    )

    axtop.hist(
        bins_cent,
        bins = bins,
        weights = total_bkg_prefit["count"],
        ls = '--',
        histtype = 'step',
        color = 'black',
        label = 'Prefit',
        zorder = 3,
    )

    axtop.fill_between(
        bins,
        list(total_bkg["count"] - np.sqrt(total_bkg["variance"])) + [0.],
        list(total_bkg["count"] + np.sqrt(total_bkg["variance"])) + [0.],
        step = 'post',
        color = 'gray',
        alpha = 0.5,
        zorder = 3,
    )

    axtop.errorbar(
        bins_cent,
        data["count"],
        yerr = np.sqrt(data["count"]),
        fmt = 'o',
        markersize = 4,
        linewidth = 0.6,
        capsize = 2.5,
        color = 'black',
        label = 'Data',
        zorder = 4,
    )

    axtop.set_xlim(bins[0], bins[-1])
    #axtop.set_ylim(2, 2e4)
    axtop.set_yscale('log')
    handles, labels = axtop.get_legend_handles_labels()
    legend = axtop.legend(handles[::-1], labels[::-1],
                          title = conv_region.get(region_name, region_name),
                          labelspacing = 0.4,
                          loc = 1)
    plt.setp(legend.get_title(), fontsize=12)

    #axtop.set_ylabel(r'$dN / dp_{\mathrm{T}}^{\mathrm{miss}}$ (1/GeV)', fontsize=12)
    axtop.set_ylabel(r'Event yield', fontsize=12)

    axtop.text(0.01, 1, r'$\mathbf{CMS}\ \mathit{Preliminary}$',
               ha='left', va='bottom', transform=axtop.transAxes, fontsize=12)
    axtop.text(0.99, 1, r'$35.9\ \mathrm{fb}^{-1}(13\ \mathrm{TeV})$',
               ha='right', va='bottom', transform=axtop.transAxes, fontsize=12)

    if doratio:
        axratio = axes[ratio_idx]
        axratio.set_ylabel(r'Ratio', fontsize=12)

        yvals = total_bkg["count"] / total_bkg["count"]
        axratio.hist(
            bins_cent,
            bins = bins,
            weights = yvals,
            histtype = 'step',
            color = 'black',
            zorder = 2,
        )
        yval_range = [np.abs(yvals-1).max()]

        yvals = total_bkg_prefit["count"] / total_bkg["count"]
        axratio.hist(
            bins_cent,
            bins = bins,
            weights = yvals,
            ls = '--',
            histtype = 'step',
            color = 'black',
            label = '',
            zorder = 3,
        )
        yval_range.append(np.abs(yvals-1).max())

        ratio_err = np.sqrt(total_bkg["variance"])/total_bkg["count"]
        axratio.fill_between(
            bins,
            list(1 - ratio_err) + [1.],
            list(1 + ratio_err) + [1.],
            step = 'post',
            color = 'gray',
            label = "Uncertainty",
            alpha = 0.5,
            zorder = 3,
        )
        yval_range.append(np.abs(ratio_err).max())

        yvals = data["count"] / total_bkg["count"]
        yerrs = np.sqrt(data["count"]) / total_bkg["count"]
        axratio.errorbar(
            bins_cent,
            data["count"] / total_bkg["count"],
            yerr = np.sqrt(data["count"]) / total_bkg["count"],
            fmt = 'o',
            markersize = 4,
            linewidth = 0.6,
            capsize = 2.5,
            color = 'black',
            label = '',
            zorder = 4,
        )
        yvals = np.abs(data["count"] / total_bkg["count"] - 1) + np.sqrt(data["count"])/total_bkg["count"]
        yvals = np.abs(yvals)
        yval_range.append(yvals.max())

        #axratio.set_ylim((1-1.5*ratio_err).min(), (1+1.5*ratio_err).max())
        #axratio.set_ylim(1-1.1*max(yval_range), 1+1.1*max(yval_range))
        #axratio.set_ylim(0.9,1.05)
        axratio.set_ylim(0.5, 1.5)
        handles, labels = axratio.get_legend_handles_labels()
        axratio.legend(handles, labels, loc=4)

    if dopull:
        axpull = axes[pull_idx]
        yvals = (data["count"] - total_bkg["count"]) / np.sqrt(np.abs(data["count"] + total_bkg["variance"]))
        axpull.errorbar(
            bins_cent,
            yvals,
            fmt = 'o',
            markersize = 4,
            color = 'black',
            zorder = 10,
        )
        yval_range = [np.abs(yvals).max()]

        yvals = (data["count"] - total_bkg_prefit["count"]) / np.sqrt(np.abs(data["count"] + total_bkg["variance"]))
        axpull.errorbar(
            bins_cent,
            yvals,
            fmt = 'o',
            markersize = 4,
            color = 'black',
            mfc = 'white',
            zorder = 1,
        )
        yval_range.append(np.abs(yvals).max())

        #axpull.set_ylim(-1.1*max(yval_range), 1.1*max(yval_range))
        axpull.set_ylim(-3., 3.)
        axpull.axhline(-1, color='gray', lw=1, ls='--')
        axpull.axhline( 1, color='gray', lw=1, ls='--')

        axpull.set_ylabel(r'Pull', fontsize=12)

    axbot.set_xlabel(r'$p_{\mathrm{T}}^{\mathrm{miss}}$ (GeV)', fontsize=12)

    print("Creating {}".format(output))
    fig.savefig(output, format="pdf", bbox_inches="tight")
    plt.close(fig)

def main():
    options = parse_args()
    path = options.path

    with uproot.open(path) as f:
        for region in options.regions.split(","):
            post_fit_region = region + "_postfit"
            pre_fit_region = region + "_prefit"
            data = f[post_fit_region]["data_obs"].pandas()
            data.index = data.index.rename("bins")

            total_bkg = f[post_fit_region]["TotalProcs"].pandas()
            total_bkg.index = total_bkg.index.rename("bins")

            total_bkg_prefit = f[pre_fit_region]["TotalProcs"].pandas()
            total_bkg_prefit.index = total_bkg_prefit.index.rename("bins")

            mc_proc_names = [
                k.replace(";1", "")
                for k in f[post_fit_region].keys()
                if k.replace(";1", "") not in ["TotalBkg", "TotalProcs", "TotalSig", "data_obs"]
            ]

            mc_procs = {
                mc_proc_name: f[post_fit_region][mc_proc_name].pandas()
                for mc_proc_name in mc_proc_names
            }
            for mc_proc in mc_procs.values():
                mc_proc.index = mc_proc.index.rename("bins")

            #bin_real_widths = (bin_real_vals[1:] - bin_real_vals[:-1])/2
            #
            #divisor = np.array(list(
            #    bin_real_widths[[int(b.left) for b in data.index.get_level_values("bins").values]]
            #)*2).reshape(data.shape[::-1]).T
            #data /= divisor

            #divisor = np.array(list(
            #    bin_real_widths[[int(b.left) for b in total_bkg.index.get_level_values("bins").values]]
            #)*2).reshape(total_bkg.shape[::-1]).T
            #total_bkg /= divisor

            new_mc_procs = {}
            for proc_name, mc_proc in mc_procs.items():
            #    divisor = np.array(list(
            #        bin_real_widths[[int(b.left) for b in mc_proc.index.get_level_values("bins").values]]
            #    )*2).reshape(mc_proc.shape[::-1]).T
            #    new_mc_procs[proc_name] = mc_proc / divisor
                new_mc_procs[proc_name] = mc_proc

            draw(
                data, total_bkg, total_bkg_prefit, new_mc_procs,
                post_fit_region.replace(";1", "").replace("_postfit", ""),
                "fit_result_distributions_{}.pdf".format(post_fit_region.replace(";1", "")),
                options.doratio, options.dopull,
            )

if __name__ == "__main__":
    main()
