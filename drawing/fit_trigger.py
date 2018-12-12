import ROOT

try:
    import cPickle as pickle
except ImportError:
    import pickle

def main():
    with open("trigger_efficiency_eff.pkl", 'r') as f:
        x, y, yerr = pickle.load(f)
    graph = ROOT.TGraphAsymmErrors(len(x))
    for i in range(len(x)):
        graph.SetPoint(i, x[i], y[i])
        graph.SetPointEYhigh(i, yerr[0,i])
        graph.SetPointEYlow(i, yerr[1,i])
        erf = ROOT.TF1("erf", "0.5*[0]*(1 + TMath::Erf((x-[1])/(TMath::Sqrt(2)*[2])))", 0, 500)
    erf.SetParameter(0, 1)
    erf.SetParameter(1, 150)
    erf.SetParameter(2, 10)
    graph.Fit(erf)
    with open("fit_results.pkl", 'w') as f:
        p0 = erf.GetParameter(0)
        if p0 > 1.:
            p0 = 1.
        pickle.dump((1, erf.GetParameter(1), erf.GetParameter(2)), f)

if __name__ == "__main__":
    main()
