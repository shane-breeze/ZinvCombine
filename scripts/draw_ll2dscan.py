#!/usr/bin/env python
import argparse
import numpy as np
from rootpy.io import root_open
from rootpy.tree import Cut
from rootpy.plotting import Canvas, Graph, Legend, Hist
from rootStyles import setup_root
from rootHistTools import draw_header, create_legend
setup_root()

import ROOT
ROOT.gStyle.SetNumberContours(256)
#one_sigma = ROOT.TMath.Erf(1/np.sqrt(2))
#two_sigma = ROOT.TMath.Erf(2/np.sqrt(2))
chi2_2df_one_sigma = ROOT.TMath.ChisquareQuantile(0.68, 2)
chi2_2df_two_sigma = ROOT.TMath.ChisquareQuantile(0.95, 2)

from color_palettes import ColourPalette

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help="Root file from the 2D scan")
    parser.add_argument("outfile", help="File to write to")
    parser.add_argument("-x", "--x-poi", default="r_mumu",
                        help="POI on the x-axis")
    parser.add_argument("-y", "--y-poi", default="r_nunu",
                        help="POI on the y-axis")
    parser.add_argument("-z", "--z-param", default="2*deltaNLL",
                        help="Name of the Z parameter")
    parser.add_argument("-n", "--npoints", default=250, type=int,
                        help="Sqrt of points scanned minus 1")
    parser.add_argument("--x-range", default="(0.8,1.2)",
                        help="X-axis scan range as a tuple")
    parser.add_argument("--y-range", default="(0.9,1.3)",
                        help="Y-axis scan range as a tuple")
    parser.add_argument("--z-range", default="(0,10)",
                        help="Z-axis range as a tuple")
    return parser.parse_args()

def profile_tree(tree, expression, bins, selection=""):
    prof = scan.draw(
        expression+">>prof({})".format(",".join(map(str, bins))),
        selection = selection,
        options = "prof",
    )
    return prof

name_conv = {
    "r_mumu": "r_{#mu#mu}",
    "r_nunu": "r_{inv.}",
    "2*deltaNLL": "q({}, {})",
}

if __name__ == "__main__":
    options = parse_args()

    # Create binning
    npoints = options.npoints
    xpoi = options.x_poi
    ypoi = options.y_poi
    zparam = options.z_param
    x_range = eval(options.x_range)
    y_range = eval(options.y_range)
    z_range = eval(options.z_range)
    bins = [npoints]+list(x_range)+[npoints]+list(y_range)

    with root_open(options.infile, 'read') as rootfile:
        scan = rootfile.get("limit")

        # 2D profile of NLL scan averages per bin (smooths somewhat)
        prof = profile_tree(
            scan,
            "{}:{}:{}".format(xpoi, ypoi, zparam),
            bins,
            selection = "{}>0.".format(zparam),
        )
        prof.GetXaxis().SetTitle(name_conv[xpoi])
        prof.GetYaxis().SetTitle(name_conv[ypoi])
        prof.GetZaxis().SetTitle(name_conv[zparam].format(name_conv[xpoi],
                                                          name_conv[ypoi]))
        prof.SetMinimum(z_range[0])
        prof.SetMaximum(z_range[1])

        # Fill in failed points
        for p in prof:
            if p.value <= 0.:
                prof.Fill(p.x.center, p.y.center, 1000.)

        # Find best fit point within axes
        point_bf = Graph(1,
            drawstyle   = 'p',
            markerstyle = 34,
            markercolor = 'black',
            markersize  = 2,
            legendstyle = 'p',
            title = "Best fit",
        )
        best_fit = [(getattr(p, xpoi), getattr(p, ypoi))
            for p in scan.copy_tree(
                '{}==0 & 0.8<{}<1.2 & 0.9<{}<1.3'.format(zparam, xpoi, ypoi),
            )
        ]
        point_bf.SetPoint(1, *best_fit[0])

        # Make contours: 68 and 95%
        cont_1sig = prof.Clone()
        cont_1sig.linewidth = 2
        cont_1sig.linecolor = "black"
        cont_1sig.legendstyle = 'l'
        cont_1sig.title = "68% CL"

        cont_2sig = cont_1sig.Clone()
        cont_2sig.linestyle = 2
        cont_2sig.legendstyle = 'l'
        cont_2sig.title = "95% CL"

        cont_1sig.SetContour(1, np.array([chi2_2df_one_sigma]))
        cont_2sig.SetContour(1, np.array([chi2_2df_two_sigma]))

        cont_2sig_leg = Hist(
            10, 0, 10,
            linestyle = 2,
            linewidth = 2,
            linecolor = "black",
            legendstyle = 'l',
            title = "95% CL",
        )

        # need rebin 2 sigma to be able to set linestyle=2
        nmerge = npoints / 25
        cont_2sig = cont_2sig.rebinned((nmerge, nmerge))

        # Create SM point
        point_sm = Graph(1,
            drawstyle   = 'p',
            markerstyle = 33,
            markercolor = '#e31a1c',
            markersize  = 2,
            legendstyle = 'p',
            title = "SM",
        )
        point_sm.SetPoint(1, 1, 1)

        point_sm_bkg = point_sm.Clone()
        point_sm_bkg.markercolor = 'white'
        point_sm_bkg.markersize = 2.3

        # Custom palette
        palette = ColourPalette()
        palette.set_palette("mystic_ocean")

        # Create canvas
        canvas = Canvas(width=750, height=650)
        canvas.margin = 0.12, 0.15, 0.12, 0.08

        # Custom legend
        # legend position
        #         False      True
        #       ----------------------
        # True  | top left | top right
        #       |---------------------
        # False | bot left | bot right
        pos = {
            (True, True): "top right",
            (False, True): "top left",
            (True, False): "bot right",
            (False, False): "bot left",
        }[(best_fit[0][0]-sum(x_range)/2 < 0.,
           best_fit[0][1]-sum(y_range)/2 < 0.)]

        legend = create_legend(
            [point_bf, point_sm, cont_1sig, cont_2sig_leg],
            pos = pos,
        )
        legend.SetFillColor(0)
        legend.SetFillStyle(1001)

        # draw it
        prof.Draw("colz")
        cont_1sig.Draw("cont3same")
        cont_2sig.Draw("cont3same")
        point_sm_bkg.Draw("same")
        point_sm.Draw("same")
        point_bf.Draw("same")
        legend.Draw()
        draw_header()
        canvas.save_as(options.outfile)
