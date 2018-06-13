from rootpy.io import root_open
import ROOT

def get_hist(path):
    filepath, histpath = path.split(":")
    with root_open(filepath, 'read') as f:
        hist = f.get(histpath)
        hist.set_directory(None)
    return hist

if __name__ == "__main__":
    #hist = get_hist("Monojet.root:plotAnalyzer/ZJetsToNuNu/GenMll")
    hist = get_hist("DYJetsToLL.root:plotAnalyzer/DYJetsToLL/GenMll")

    #w = ROOT.RooWorkspace()
    #w.factory('RooBreitWigner::g(x[70,110],mu[91,85,95],sigma[5,0,40])')
    #w.Print()

    # Generate model
    x = ROOT.RooRealVar("x", "Gen m_{#nu#nu}", 70, 120)
    mean = ROOT.RooRealVar("mean", "Z Mass", 91, 85, 95)
    sigma = ROOT.RooRealVar("sigma", "Width", 2, 0, 10)
    breit = ROOT.RooBreitWigner("breit", "breit(x,mean,sigma)", x, mean, sigma)

    # Generate data (MC in this case)
    l = ROOT.RooArgList(x)
    data = ROOT.RooDataHist("data", "data", l, hist)

    result = breit.fitTo(data,
        ROOT.RooFit.PrintLevel(-1),
        ROOT.RooFit.SumW2Error(True),
    )
    mean.Print()
    sigma.Print()

    # Draw
    xframe = x.frame()
    data.plotOn(xframe)
    breit.plotOn(xframe)
    breit.paramOn(xframe)

    canvas = ROOT.TCanvas()
    xframe.SetTitle("")
    xframe.GetXaxis().SetTitleSize(0.045)
    xframe.GetYaxis().SetTitle("Events / 1 GeV")
    xframe.GetYaxis().SetTitleSize(0.045)
    xframe.Draw()
    canvas.SaveAs("test.pdf")
