import uproot
import numpy as np
import matplotlib.pyplot as plt

color_procs = {
    "bkg":    "#d9d9d9",
    "wlnu":   "#b3de69",
    "qcd":    "#fb8072",
    "znunu":  "#80b1d3",
    "zmumu":  "#ffed6f",
    "gsmumu": "#fdbf6f",
    "zee":    "#ffed6f",
    "gsee":   "#fdbf6f",
}

proc_names = {
    "bkg":  "Bkgs.",
    "wlnu": r'$\mathrm{W}(\rightarrow l\nu) + \mathrm{jets}$',
    "qcd":  "QCD Multijet",
    "znunu": r'$\mathrm{Z}(\rightarrow \nu\nu) + \mathrm{jets}$',
    "zmumu": r'$\mathrm{Z}(\rightarrow \mu\mu) + \mathrm{jets}$',
    "gsmumu": r'$\gamma^{*}(\rightarrow \mu\mu) + \mathrm{jets}$',
    "zee": r'$\mathrm{Z}(\rightarrow ee) + \mathrm{jets}$',
    "gsee": r'$\gamma^{*}(\rightarrow ee) + \mathrm{jets}$',
}

bin_real_vals = np.array([200,210,220,230,250,275,300,350,400,500,600,800])

def draw(data, total_bkg, mc_procs, output):
    fig, (axtop, axbot) = plt.subplots(
        nrows=2, ncols=1, sharex='col', sharey=False,
        gridspec_kw={'height_ratios': [3, 1],
                     'wspace': 0.1,
                     'hspace': 0.1},
        figsize = (5.4, 5.4),
    )

    bins_low = np.array([b.left for b in total_bkg.index.get_level_values("bins").values])
    bins_upp = np.array([b.right for b in total_bkg.index.get_level_values("bins").values])

    bins_low = bin_real_vals[:-1]
    bins_upp = bin_real_vals[1:]

    bins = np.array(list(bins_low)+[bins_upp[-1]])
    bins_cent = (bins_low+bins_upp)/2

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
        label = "SM Total",
        zorder = 2,
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

    axtop.set_xlim(bins[0], bins[-1])
    #axtop.set_ylim(2, 2e4)
    axtop.set_yscale('log')
    handles, labels = axtop.get_legend_handles_labels()
    axtop.legend(handles[::-1], labels[::-1])

    axtop.set_ylabel(r'$dN / dp_{\mathrm{T}}^{\mathrm{miss}}$ (1/GeV)', fontsize=12)

    axtop.text(0.01, 1, r'$\mathbf{CMS}\ \mathit{Preliminary}$',
               ha='left', va='bottom', transform=axtop.transAxes, fontsize=12)
    axtop.text(0.99, 1, r'$35.9\ \mathrm{fb}^{-1}(13\ \mathrm{TeV})$',
               ha='right', va='bottom', transform=axtop.transAxes, fontsize=12)

    axbot.set_xlabel(r'$p_{\mathrm{T}}^{\mathrm{miss}}$ (GeV)', fontsize=12)
    axbot.set_ylabel(r'Ratio', fontsize=12)

    axbot.hist(
        bins_cent,
        bins = bins,
        weights = total_bkg["count"] / total_bkg["count"],
        histtype = 'step',
        color = 'black',
        zorder = 2,
    )

    ratio_err = np.sqrt(total_bkg["variance"])/total_bkg["count"]
    axbot.fill_between(
        bins,
        list(1 - ratio_err) + [1.],
        list(1 + ratio_err) + [1.],
        step = 'post',
        color = 'gray',
        label = "Uncertainty",
        alpha = 0.5,
        zorder = 3,
    )
    axbot.set_ylim((1-ratio_err).min(), (1+ratio_err).max())
    axbot.legend(*axbot.get_legend_handles_labels())

    print("Creating {}".format(output))
    fig.savefig(output, format="pdf", bbox_inches="tight")
    plt.close(fig)

def main():
    path = "/vols/build/cms/sdb15/ZinvWidth/HiggsCombine/ZinvCombine/data/finalfit/shape/cards_181212/test.root"

    with uproot.open(path) as f:
        for region_dir in f:
            data = f[region_dir]["data_obs"].pandas()
            data.index = data.index.rename("bins")

            total_bkg = f[region_dir]["TotalProcs"].pandas()
            total_bkg.index = total_bkg.index.rename("bins")

            mc_proc_names = [
                k.replace(";1", "")
                for k in f[region_dir].keys()
                if k.replace(";1", "") not in ["TotalBkg", "TotalProcs", "TotalSig", "data_obs"]
            ]

            mc_procs = {
                mc_proc_name: f[region_dir][mc_proc_name].pandas()
                for mc_proc_name in mc_proc_names
            }
            for mc_proc in mc_procs.values():
                mc_proc.index = mc_proc.index.rename("bins")

            bin_real_widths = (bin_real_vals[1:] - bin_real_vals[:-1])/2

            divisor = np.array(list(
                bin_real_widths[[int(b.left) for b in data.index.get_level_values("bins").values]]
            )*2).reshape(data.shape[::-1]).T
            data /= divisor

            divisor = np.array(list(
                bin_real_widths[[int(b.left) for b in total_bkg.index.get_level_values("bins").values]]
            )*2).reshape(total_bkg.shape[::-1]).T
            total_bkg /= divisor

            new_mc_procs = {}
            for proc_name, mc_proc in mc_procs.items():
                divisor = np.array(list(
                    bin_real_widths[[int(b.left) for b in mc_proc.index.get_level_values("bins").values]]
                )*2).reshape(mc_proc.shape[::-1]).T
                new_mc_procs[proc_name] = mc_proc / divisor

            draw(data, total_bkg, new_mc_procs, "fit_result_distributions_{}.pdf".format(region_dir.replace(";1", "")))
        pass
    pass

if __name__ == "__main__":
    main()
