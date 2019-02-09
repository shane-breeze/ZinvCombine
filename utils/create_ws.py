import ROOT

def main():
    rfile = ROOT.TFile("fitfuncs.root", "RECREATE")
    ws = ROOT.RooWorkspace("w")

    x = ROOT.RooRealVar("x", "x", 0, 1000)
    mean1 = ROOT.RooRealVar("mean1", "mean1", 100, 0, 400)
    width1 = ROOT.RooRealVar("width1", "width1", 50, 0, 400)
    alpha1 = ROOT.RooRealVar("alpha1", "alpha1", 0.1, 0, 10)
    n1 = ROOT.RooRealVar("n1", "n1", 1.5, 0, 10)
    mean2 = ROOT.RooRealVar("mean2", "mean2", 100, 0, 400)
    width2 = ROOT.RooRealVar("width2", "width2", 50, 0, 400)
    alpha2 = ROOT.RooRealVar("alpha2", "alpha2", 0.1, 0, 10)
    n2 = ROOT.RooRealVar("n2", "n2", 1.5, 0, 10)
    sigfrac = ROOT.RooRealVar("sigfrac", "sigfrac", 0.5, 0, 1)
    cb1 = ROOT.RooCBShape("cb1", "cb1", x, mean1, width1, alpha1, n1)
    cb2 = ROOT.RooCBShape("cb2", "cb2", x, mean2, width2, alpha2, n2)
    cblist = ROOT.RooArgList(cb1, cb2)
    cbsum = ROOT.RooAddPdf("cbsum", "cbsum", cblist, ROOT.RooArgList(sigfrac))
    cbsumcdf = cbsum.createCdf(ROOT.RooArgSet(x))
    cbsumcdf.Print()
    getattr(ws, "import")(x)
    getattr(ws, "import")(mean1)
    getattr(ws, "import")(width1)
    getattr(ws, "import")(alpha1)
    getattr(ws, "import")(n1)
    getattr(ws, "import")(mean2)
    getattr(ws, "import")(width2)
    getattr(ws, "import")(alpha2)
    getattr(ws, "import")(n2)
    getattr(ws, "import")(sigfrac)
    getattr(ws, "import")(cbsumcdf)

    ws.Write()
    rfile.Close()

if __name__ == "__main__":
    main()
