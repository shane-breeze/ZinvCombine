import argparse
import glob
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import numpy as np
import pandas as pd
import os
import re
import uproot

conv_names = {
    "metTrigSF":   r'$p_{\rm{T}}^{\rm{miss}}$ trig.',
    "metTrigSyst": r'$p_{\rm{T}}^{\rm{miss}}$ trig. syst.',
    "metTrigStat": r'$p_{\rm{T}}^{\rm{miss}}$ trig. stat.',
    "stat":     r'Stat.',
    "jesTotal": r'JES',
    "jer":      r'JER',
    "unclust":  r'Unclustered Energy',
    "jesSinglePionECAL":  r'JES Single $\pi$ ECAL',
    "jesSinglePionHCAL":  r'JES Single $\pi$ HCAL',
    "jesFragmentation":   r'JES Fragmentation',
    "jesAbsoluteStat":    r'JES Abs. Stat.',
    "jesAbsoluteScale":   r'JES Abs. Scale',
    "jesAbsoluteMPFBias": r'JES Abs. MPF Bias',
    "jesFlavorQCD":       r'JES Flavour QCD',
    "jesRelativeFSR":     r'JES ISR+FSR',
    "jesRelativeStatFSR": r'JES Stat. ISR+FSR',
    "jesRelativeStatEC":  r'JES Stat. EC',
    "jesRelativeStatHF":  r'JES Stat. HF',
    "jesTimePtEta":       r'JES Time $p_{\rm{T}}$--$\eta$',
    "jesRelativePtBB":    r'JES $p_{\rm{T}}$ BB',
    "jesRelativePtEC1":   r'JES $p_{\rm{T}}$ EC1',
    "jesRelativePtEC2":   r'JES $p_{\rm{T}}$ EC2',
    "jesRelativePtHF":    r'JES $p_{\rm{T}}$ HF',
    "jesRelativeJEREC1":  r'JER EC1',
    "jesRelativeJEREC2":  r'JER EC2',
    "jesRelativeJERHF":   r'JER HF',
    "jesRelativeBal":     r'JES Bal.',
    "jesPileUpDataMC":    r'JES PU Data/MC',
    "jesPileUpPtBB":      r'JES PU $p_{\rm{T}}$ BB',
    "jesPileUpPtEC1":     r'JES PU $p_{\rm{T}}$ EC1',
    "jesPileUpPtEC2":     r'JES PU $p_{\rm{T}}$ EC2',
    "jesPileUpPtHF":      r'JES PU $p_{\rm{T}}$ HF',
    "jesPileUpPtRef":     r'JES PU $p_{\rm{T}}$ Ref.',
    "muonPtScale":       r'$\mu$ $p_{\mathrm{T}}$ scale',
    "eleEnergyScale":    r'$e$ energy scale',
    "photonEnergyScale": r'$\gamma$ energy scale',
    "muonId":    r'$\mu$ id.',
    "muonIso":   r'$\mu$ iso.',
    "muonTrack": r'$\mu$ track.',
    "eleIdIso": r'$e$ id. iso.',
    "eleReco":  r'$e$ reco.',
    "eleTrig":  r'$e$ trig.',
    "tauId": r'$\tau$ id.',
    "pileup": r'Pileup',
    "prefiring": r'Prefiring',
    "lumi":   r'Lumi.',
    "d1k_qcd":  r'$\delta^{(1)}K_{\rm QCD}$',
    "d2k_qcd":  r'$\delta^{(2)}K_{\rm QCD}$',
    "d3k_qcd":  r'$\delta^{(3)}K_{\rm QCD}$',
    "d1k_ew":   r'$\delta^{(1)}\kappa_{\rm{EW}}$',
    "d2k_ew_w": r'$\delta^{(2)}\kappa_{\rm{EW}}^{\rm{W}}$',
    "d2k_ew_z": r'$\delta^{(2)}\kappa_{\rm{EW}}^{\rm{Z}}$',
    "d3k_ew_w": r'$\delta^{(3)}\kappa_{\rm{EW}}^{\rm{W}}$',
    "d3k_ew_z": r'$\delta^{(3)}\kappa_{\rm{EW}}^{\rm{Z}}$',
    "dk_mix":   r'$\delta K_{\rm mix}$',
    "lhePdf":   r'PDF variations',
    "lheScale": r'Scale variations',
    "lheScale_gstar": r'Scale variations ($\gamma^{*}$)',
    "lheScale_zonly": r'Scale variations ($Z$)',
    "kzll_mcstat": r'$k_{\mathrm{Z}}$ MC stat.',
    "kgll_mcstat": r'$k_{\gamma^{*}}$ MC stat.',
    "qcdSyst":     r'QCD Syst.',
    "qcdSystBin0": r'QCD Syst. (0)',
    "qcdSystBin1": r'QCD Syst. (1)',
    "qcdSystBin2": r'QCD Syst. (2)',
    "qcdSystBin3": r'QCD Syst. (3)',
    "qcdSystBin4": r'QCD Syst. (4)',
    "qcdSystBin5": r'QCD Syst. (5)',
    "qcdSystBin6": r'QCD Syst. (6)',
    "qcdSystBin7": r'QCD Syst. (7)',
    "qcdSystBin8": r'QCD Syst. (8)',
    #"prop_binmonojet_bin0": r'MC stat. monojet bin 0',
    #"prop_binmonojet_bin1": r'MC stat. monojet bin 1',
    #"prop_binmonojet_bin2": r'MC stat. monojet bin 2',
    #"prop_binmonojet_bin3": r'MC stat. monojet bin 3',
    #"prop_binmonojet_bin4": r'MC stat. monojet bin 4',
    #"prop_binmonojet_bin5": r'MC stat. monojet bin 5',
    #"prop_binmonojet_bin6": r'MC stat. monojet bin 6',
    #"prop_binmonojet_bin7": r'MC stat. monojet bin 7',
    #"prop_binmonojet_bin8": r'MC stat. monojet bin 8',
    #"prop_binsinglemu_bin0": r'MC stat. singlemu bin 0',
    #"prop_binsinglemu_bin1": r'MC stat. singlemu bin 1',
    #"prop_binsinglemu_bin2": r'MC stat. singlemu bin 2',
    #"prop_binsinglemu_bin3": r'MC stat. singlemu bin 3',
    #"prop_binsinglemu_bin4": r'MC stat. singlemu bin 4',
    #"prop_binsinglemu_bin5": r'MC stat. singlemu bin 5',
    #"prop_binsinglemu_bin6": r'MC stat. singlemu bin 6',
    #"prop_binsinglemu_bin7": r'MC stat. singlemu bin 7',
    #"prop_binsinglemu_bin8": r'MC stat. singlemu bin 8',
    #"prop_bindoublemu_bin0": r'MC stat. doublemu bin 0',
    #"prop_bindoublemu_bin1": r'MC stat. doublemu bin 1',
    #"prop_bindoublemu_bin2": r'MC stat. doublemu bin 2',
    #"prop_bindoublemu_bin3": r'MC stat. doublemu bin 3',
    #"prop_bindoublemu_bin4": r'MC stat. doublemu bin 4',
    #"prop_bindoublemu_bin5": r'MC stat. doublemu bin 5',
    #"prop_bindoublemu_bin6": r'MC stat. doublemu bin 6',
    #"prop_bindoublemu_bin7": r'MC stat. doublemu bin 7',
    #"prop_bindoublemu_bin8": r'MC stat. doublemu bin 8',
    #"prop_binsingleele_bin0": r'MC stat. singleele bin 0',
    #"prop_binsingleele_bin1": r'MC stat. singleele bin 1',
    #"prop_binsingleele_bin2": r'MC stat. singleele bin 2',
    #"prop_binsingleele_bin3": r'MC stat. singleele bin 3',
    #"prop_binsingleele_bin4": r'MC stat. singleele bin 4',
    #"prop_binsingleele_bin5": r'MC stat. singleele bin 5',
    #"prop_binsingleele_bin6": r'MC stat. singleele bin 6',
    #"prop_binsingleele_bin7": r'MC stat. singleele bin 7',
    #"prop_binsingleele_bin8": r'MC stat. singleele bin 8',
    #"prop_bindoubleele_bin0": r'MC stat. doubleele bin 0',
    #"prop_bindoubleele_bin1": r'MC stat. doubleele bin 1',
    #"prop_bindoubleele_bin2": r'MC stat. doubleele bin 2',
    #"prop_bindoubleele_bin3": r'MC stat. doubleele bin 3',
    #"prop_bindoubleele_bin4": r'MC stat. doubleele bin 4',
    #"prop_bindoubleele_bin5": r'MC stat. doubleele bin 5',
    #"prop_bindoubleele_bin6": r'MC stat. doubleele bin 6',
    #"prop_bindoubleele_bin7": r'MC stat. doubleele bin 7',
    #"prop_bindoubleele_bin8": r'MC stat. doubleele bin 8',
    "rw": r'$r_{\rm{W}}$',
    "r": r'$r$',
    "rqcd": r'$r_{\mathrm{qcd}}$',
    "hat_rw": r'$\hat{r}_{\rm{W}}$',
    "hat_r": r'$\hat{r}$',
    "hat_rqcd": r'$\hat{r}_{\mathrm{qcd}}$',
    "dhat_rw": r'$\Delta\hat{r}_{\rm{W}}$',
    "dhat_r": r'$\Delta\hat{r}$',
    "dhat_rqcd": r'$\Delta\hat{r}_{\mathrm{qcd}}$',
}

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("results_dir", type=str,
                        help="Directory with the desired results")
    parser.add_argument("initial_fit", type=str,
                        help="Path to initial fit file")
    parser.add_argument("-n", "--name", type=str, default="Exp",
                        help="String to add to regex")
    parser.add_argument("-o", "--output", type=str, default="impacts.pdf",
                        help="Output file")
    parser.add_argument("-r", "--regex", type=str, default=r'.*',
                        help="Regex string to match inputs with")
    parser.add_argument("--poi", type=str, default='r',
                        help="Parameter of interest")

    return parser.parse_args()

def get_fit_result(path, param):
    try:
        limit = uproot.open(path)["limit"]
    except KeyError:
        raise KeyError(path)
    if limit.numentries == 0:
        return np.array([1., 1., 1.])
    if param not in limit.keys():
        assert KeyError(path)
    return limit.array(param)

def get_fit_results(poi, results_dir, initial_fit_file, regex_param_fit, regex_param):
    names = []
    nuisances = []
    impacts = []

    poi_nominal_fit = get_fit_result(initial_fit_file, poi)
    for path in glob.glob(os.path.join(results_dir, "*.root")):
        match = regex_param_fit.search(os.path.basename(path))
        if match:
            param = match.group("param")
            if not regex_param.search(param):
                continue
            poi_fit = get_fit_result(path, poi)
            try:
                nuis_fit = get_fit_result(path, param)
            except KeyError:
                nuis_fit = [0., 0., 0.]

            if len(nuis_fit) != 3:
                print(path)

            names.append(param)
            nuisances.append(list(nuis_fit))
            if poi_fit.shape[0]==2:
                poi_fit = np.array(list(poi_fit)+[1/poi_fit[-1]])
            impacts.append([poi_fit[1]-poi_fit[0], poi_fit[2]-poi_fit[0]])

    nuisances = np.array(nuisances)
    impacts = np.array(impacts)

    sort = np.argsort(np.mean(np.abs(impacts), axis=1))
    nuisances = nuisances[sort]
    impacts = impacts[sort]
    names = list(np.array(names)[sort])

    return names, nuisances, impacts, poi_nominal_fit

def draw_labels(axis, names):
    fontsize = 12*14./len(names)
    fontsize = max(4, min(20, fontsize))
    for idx in range(len(names)):
        axis.text(0.05, idx+0.5, str(len(names)-idx),
                  weight='bold', va='center', fontsize=fontsize)
        name = conv_names.get(names[idx], names[idx].replace("_", ""))
        axis.text(0.25, idx+0.5, name, va='center', fontsize=fontsize)
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

def draw_impacts(poi, names, nuisances, impacts, bestfit, output):
    name = conv_names.get(poi, poi.replace("_", " "))
    print("{} = {} -{} +{}".format(name,
                                   bestfit[0],
                                   bestfit[0]-bestfit[1],
                                   bestfit[2]-bestfit[0]))
    df = pd.DataFrame({
        "nuisance": names,
        "down_impact [%]": impacts[:,0],
        "up_impact [%]": impacts[:,1],
        "down_const": nuisances[:,1],
        "up_const": nuisances[:,2],
    }, columns=["nuisance", "down_impact [%]", "up_impact [%]", "down_const", "up_const"])
    df = df.set_index("nuisance")
    print(100.*df/bestfit[0])

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
    #axm.set_xlim(-1, 1)
    axm.set_xlabel(r'$(\hat{\theta}-\theta_0)/\Delta\theta$', fontsize='large')

    # Right axis
    draw_barhs(axr, impacts)
    xmax = np.abs(axr.get_xlim()).max()
    axr.set_xlim((-xmax, xmax))
    axr.set_xlabel(conv_names.get("dhat_"+poi, poi), fontsize='large')

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
    axm.text(0, 1.005, r'$\mathbf{CMS}\ \mathit{Preliminary}$',
             ha='left', va='bottom', transform=axm.transAxes,
             fontsize='large')

    # best fit stamp
    axr.text(1, 1,
             conv_names.get("hat_"+poi, poi)+r'$ = {:.3f}^{{+{:.3f}}}_{{-{:.3f}}}$'.format(
                 bestfit[0], bestfit[2]-bestfit[0], bestfit[0]-bestfit[1],
             ), ha='right', va='bottom', transform=axr.transAxes,
             fontsize='large')

    plt.tight_layout()
    fig.savefig(output, format="pdf", bbox_inches="tight")
    plt.close(fig)
    print("Created {}".format(output))

def main():
    options = parse_args()
    poi_name = options.poi

    regex_param_fit = re.compile("higgsCombine_paramFit_{}_(?P<param>[^.]*)\.MultiDimFit\.mH91\.root".format(options.name))
    regex_param = re.compile(options.regex)

    names, nuisances, impacts, bestfit = get_fit_results(
        poi_name,
        options.results_dir,
        options.initial_fit,
        regex_param_fit,
        regex_param,
    )
    draw_impacts(poi_name, names, nuisances, impacts, bestfit, options.output)

if __name__ == "__main__":
    main()
