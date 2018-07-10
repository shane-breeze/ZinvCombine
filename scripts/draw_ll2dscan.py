#!/usr/bin/env python
import argparse
import numpy as np
from rootpy.io import root_open
from rootpy.tree import Cut
from rootpy.plotting import Canvas, Graph, Legend, Hist
from rootStyles import setup_root
from rootHistTools import draw_header, create_legend
setup_root()

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
    "r_ee": "r_{ee}",
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

    files = options.infile.split(":")
    with root_open(files[0], 'read') as rootfile:
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
            title = "Expected",
        )
        best_fit = [(getattr(p, xpoi), getattr(p, ypoi))
            for p in scan.copy_tree(
                '{}==0 & 0.8<{}<1.2 & 0.9<{}<1.3'.format(zparam, xpoi, ypoi),
            )
        ][0]
        point_bf.SetPoint(1, *best_fit)

    def func(p):
        phi = np.arctan(abs((p[1]-best_fit[1]) / (p[0]-best_fit[0])))
        if p[0] >= best_fit[0] and p[1] >= best_fit[1]:
            return phi
        elif p[0] < best_fit[0] and p[1] >= best_fit[1]:
            return np.pi - phi
        elif p[0] < best_fit[0] and p[1] < best_fit[1]:
            return np.pi + phi
        else:
            return 2*np.pi - phi

    # 68% contour
    with root_open(files[1], 'read') as rootfile:
        contour = rootfile.get("limit")

        points = [(getattr(p, xpoi), getattr(p, ypoi)) for p in contour][1:]
        points = sorted(points, key=lambda p: func(p))
        points.append(points[0]) # cyclic
        cont_1sig = Graph(len(points),
            linewidth = 2,
            linestyle = 1,
            linecolor = "black",
            legendstyle = 'l',
            title = "68% CL",
        )
        for i, p in enumerate(points):
            cont_1sig.SetPoint(i, *p)

    # 95% contour
    with root_open(files[2], 'read') as rootfile:
        contour = rootfile.get("limit")

        points = [(getattr(p, xpoi), getattr(p, ypoi)) for p in contour][1:]
        points = sorted(points, key=lambda p: func(p))
        points.append(points[0]) # cyclic
        cont_2sig = Graph(len(points),
            linewidth = 2,
            linestyle = 2,
            linecolor = "black",
            legendstyle = 'l',
            title = "95% CL",
        )
        for i, p in enumerate(points):
            cont_2sig.SetPoint(i, *p)

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
    }[(best_fit[0]-sum(x_range)/2 <= 0.,
       best_fit[1]-sum(y_range)/2 < 0.)]

    legend = create_legend(
        [point_bf, cont_1sig, cont_2sig],
        pos = pos,
    )
    legend.SetFillColor(0)
    legend.SetFillStyle(1001)

    # draw it
    prof.Draw("colz")
    cont_1sig.Draw("same")
    cont_2sig.Draw("same")
    point_sm_bkg.Draw("same")
    #point_sm.Draw("same")
    point_bf.Draw("same")
    legend.Draw()
    draw_header()
    canvas.save_as(options.outfile)
