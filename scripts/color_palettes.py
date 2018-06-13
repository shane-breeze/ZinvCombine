import numpy as np
import ROOT

class ColourPalette(object):
    def __init__(self):
        self.mystic_ocean()

    def set_palette(self, name, alpha=1., ncolours=255):
        if hasattr(self, name):
            getattr(self, name)()
        else:
            print "No colour palette {}".format(name)
            return
        ROOT.TColor.CreateGradientColorTable(
            len(self.stop),
            self.stop,
            self.red,
            self.green,
            self.blue,
            ncolours,
            alpha,
        )

    def mystic_ocean(self):
        self.stop  = np.array([0.0, 100.0])/100.
        self.red   = np.array([255,    56])/255.
        self.green = np.array([255,    69])/255.
        self.blue  = np.array([255,   145])/255.

    def deep_sea(self):
        self.stop  = np.array([0.0, 12.5, 25.0, 37.5, 50.0, 62.5, 75.0, 87.5, 100.0])/100.
        self.red   = np.array([  0,    9,   13,   17,   24,   32,   27,   25,    29])/255.
        self.green = np.array([  0,    0,    0,    2,   37,   74,  113,  160,   221])/255.
        self.blue  = np.array([ 28,   42,   59,   78,   98,  129,  154,  184,   221])/255.

if __name__ == "__main__":
    palette = ColourPalette()
