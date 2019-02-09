import ROOT
import numpy as np

def create_workspace(bins, processes, data_dict, proc_dict, output):
    # I/O
    filename, wsname = output.split(":")
    rootfile = ROOT.TFile(filename, "RECREATE")
    wspace = ROOT.RooWorkspace(wsname, wsname)

    # binning variables
    bins_cent = (bins[1:] + bins[:-1])/2
    realvar_x = ROOT.RooRealVar("x", "x", bins.min(), bins.max())
    arglist_x = ROOT.RooArgList(realvar_x)

    erf_func = "(@0*0.5*(1 + TMath::Erf(({}-@1)/(@2*sqrt(2)))))"
    realvar_eff0    = ROOT.RooRealVar("eff0",    "eff0",    1., 0.9,   1.1)
    realvar_effmu   = ROOT.RooRealVar("effmu",   "effmu",   1., 0.9,   1.1)
    realvar_mean0   = ROOT.RooRealVar("mean0",   "mean0",   0., 0.,    300.)
    realvar_meanmu  = ROOT.RooRealVar("meanmu",  "meanmu",  0., -500., 0.)
    realvar_sigma0  = ROOT.RooRealVar("sigma0",  "sigma0",  0., 0.,    300.)
    realvar_sigmamu = ROOT.RooRealVar("sigmamu", "sigmamu", 0., 0.,    500.)
    realvar_syst    = ROOT.RooRealVar("syst",    "syst",  0.)
    getattr(wspace, 'import')(realvar_eff0)
    getattr(wspace, 'import')(realvar_mean0)
    getattr(wspace, 'import')(realvar_sigma0)
    getattr(wspace, 'import')(realvar_effmu)
    getattr(wspace, 'import')(realvar_meanmu)
    getattr(wspace, 'import')(realvar_sigmamu)
    getattr(wspace, 'import')(realvar_syst)

    # MC
    for proc in processes:
        print(proc, data_dict[proc].sum(), proc_dict[proc].sum())

        # Data
        data_name = "{}_data_obs".format(proc)
        hdata = ROOT.TH1F(data_name, data_name, len(bins)-1, bins)
        for ibin in range(1, hdata.GetNbinsX()+1):
            hdata.SetBinContent(ibin, data_dict[proc][ibin-1])
        datahist_data = ROOT.RooDataHist(data_name, data_name, arglist_x, hdata)
        getattr(wspace, 'import')(datahist_data)

        # MC
        signal = proc_dict[proc]
        arglist_formvar_yields = ROOT.RooArgList()
        for ibin in range(bins.shape[0]-1):
            # Nominal
            mcyield = signal[ibin]
            mcyield_err = np.sqrt(signal[ibin])

            # real vars - const
            realvar_yield = ROOT.RooRealVar(
                "mcyield_const_cat_{}_bin_{}".format(proc, ibin),
                "mcyield_const_cat_{}_bin_{}".format(proc, ibin),
                mcyield, 0, 5*mcyield,
            )
            realvar_yield.setConstant()
            getattr(wspace, 'import')(realvar_yield)

            # function of real vars
            eff0 = ROOT.RooFormulaVar(
                "eff0_cat_{}_bin_{}".format(proc, ibin),
                "eff0_cat_{}_bin_{}".format(proc, ibin),
                erf_func.format(bins_cent[ibin]),
                ROOT.RooArgList(
                    wspace.var(realvar_eff0.GetName()),
                    wspace.var(realvar_mean0.GetName()),
                    wspace.var(realvar_sigma0.GetName()),
                ),
            )
            effmu = ROOT.RooFormulaVar(
                "effmu_cat_{}_bin_{}".format(proc, ibin),
                "effmu_cat_{}_bin_{}".format(proc, ibin),
                erf_func.format(bins_cent[ibin]),
                ROOT.RooArgList(
                    wspace.var(realvar_effmu.GetName()),
                    wspace.var(realvar_meanmu.GetName()),
                    wspace.var(realvar_sigmamu.GetName()),
                ),
            )
            getattr(wspace, 'import')(eff0)
            getattr(wspace, 'import')(effmu)

            nmu = {"singlemu": 1, "doublemu": 2, "triplemu": 3}[proc]
            eff_linear = ROOT.RooFormulaVar(
                "mcyield_linear_cat_{}_bin_{}".format(proc, ibin),
                "mcyield_linear_cat_{}_bin_{}".format(proc, ibin),
                "((@0)+(@1)*{})".format(nmu),
                ROOT.RooArgList(
                    wspace.function(eff0.GetName()),
                    wspace.function(effmu.GetName()),
                ),
            )
            eff_power = ROOT.RooFormulaVar(
                "mcyield_power_cat_{}_bin_{}".format(proc, ibin),
                "mcyield_power_cat_{}_bin_{}".format(proc, ibin),
                "(@0*@1**({}))".format(nmu),
                ROOT.RooArgList(
                    wspace.function(eff0.GetName()),
                    wspace.function(effmu.GetName()),
                ),
            )
            getattr(wspace, 'import')(eff_linear)
            getattr(wspace, 'import')(eff_power)

            formvar_yield = ROOT.RooFormulaVar(
                "mcyield_formula_cat_{}_bin_{}".format(proc, ibin),
                "mcyield_formula_cat_{}_bin_{}".format(proc, ibin),
                "@0/(@1 * TMath::Power((@2/@1), @3))",
                ROOT.RooArgList(
                    wspace.var(realvar_yield.GetName()),
                    wspace.function(eff_power.GetName()),
                    wspace.function(eff_linear.GetName()),
                    wspace.var("syst"),
                ),
            )
            getattr(wspace, 'import')(formvar_yield)

            # absolute value of function
            absvar_yield = ROOT.RooFormulaVar(
                "mcyield_abs_cat_{}_bin_{}".format(proc, ibin),
                "mcyield_abs_cat_{}_bin_{}".format(proc, ibin),
                "@0*(@0>0) + 1e-7",
                ROOT.RooArgList(wspace.function(formvar_yield.GetName())),
            )
            getattr(wspace, 'import')(absvar_yield)
            arglist_formvar_yields.add(wspace.function(absvar_yield.GetName()))

        name = "{}_{}_pass".format(proc, proc)
        paramhist = ROOT.RooParametricHist(
            name, name, realvar_x, arglist_formvar_yields, hdata,
        )
        paramhist_norm = ROOT.RooAddition(
            "{}_norm".format(name), "{}_norm".format(name), arglist_formvar_yields,
        )

        getattr(wspace, 'import')(paramhist)
        getattr(wspace, 'import')(paramhist_norm, ROOT.RooFit.RecycleConflictNodes())

    rootfile.cd()
    wspace.Print()
    wspace.Write()
    rootfile.Close()
    rootfile.Delete()

def get_hist(pathname):
    filename, histname = pathname.split(":")
    tfile = ROOT.TFile.Open(filename, 'READ')
    obj = tfile.Get(histname)
    obj.SetDirectory(0)
    tfile.Close()
    return np.array([obj.GetXaxis().GetBinLowEdge(i) for i in range(1, obj.GetNbinsX()+2)]),\
           np.array([obj.GetBinContent(i) for i in range(1, obj.GetNbinsX()+1)]),\
           np.array([obj.GetBinError(i) for i in range(1, obj.GetNbinsX()+1)])

def main():
    bins, singlemu, _ = get_hist("Zinv_METnoX-ShapeTemplates_met_trigger.root:singlemu/data_obs")
    _, doublemu, _ = get_hist("Zinv_METnoX-ShapeTemplates_met_trigger.root:doublemu/data_obs")
    _, triplemu, _ = get_hist("Zinv_METnoX-ShapeTemplates_met_trigger.root:triplemu/data_obs")
    _, singlemu_pass, _ = get_hist("Zinv_METnoX-ShapeTemplates_met_trigger.root:singlemu/singlemu_pass")
    _, doublemu_pass, _ = get_hist("Zinv_METnoX-ShapeTemplates_met_trigger.root:doublemu/doublemu_pass")
    _, triplemu_pass, _ = get_hist("Zinv_METnoX-ShapeTemplates_met_trigger.root:triplemu/triplemu_pass")
    create_workspace(
        bins,
        ["singlemu", "doublemu", "triplemu"],
        {"singlemu": singlemu, "doublemu": doublemu, "triplemu": triplemu},
        {"singlemu": singlemu_pass, "doublemu": doublemu_pass, "triplemu": triplemu_pass},
        "workspace.root:wspace",
    )

if __name__ == "__main__":
    main()
