import numpy as np
import matplotlib.pyplot as plt

sm = 487

x = np.array([
    493.9380530973452,
    487,
    499,
    503,
    498,
    539,
    450,
])

vals = [
    r'$494 \pm 11$',
    r'$487 \pm 14$',
    r'$499.0 \pm 1.5$',
    r'$503 \pm 16$',
    r'$498 \pm 17$',
    r'$539 \pm 31$',
    r'$450 \pm 48$',
]

y = [
    "World Average",
    "CMS (exp.)",
    "LEP Indirect",
    "LEP Combined",
    "L3",
    "OPAL",
    "ALEPH",
]

color = [
    '#000000',
    '#e31a1c',
    '#1f78b4',
    '#1f78b4',
    '#33a02c',
    '#33a02c',
    '#33a02c',
]

xerr = np.array([
    [10.53607372589629, 10.53607372589629],
    [14, 14],
    [1.5, 1.5],
    [16, 16],
    [16.97056275, 16.97056275],
    [31.06444913, 31.06444913],
    [48.08326112, 48.08326112],
]).T

def main():
    fig, ax = plt.subplots(
        figsize = (4.8, 5.6),
    )

    for idx in range(x.shape[0]):
        ax.errorbar(
            [x[idx]],
            [idx+1],
            xerr = xerr[:,idx].reshape(2, 1),
            fmt='o',
            markersize=4.5,
            linewidth=1.5,
            capsize=3,
            color=color[idx],
        )

        ax.text(
            585,
            idx+1,
            vals[idx],
            fontsize=14,
        )

    ax.set_xlabel(
        r'$\Gamma(\mathrm{Z}\rightarrow\mathrm{inv.})$ [MeV]',
        fontsize=14,
    )
    ax.text(
        0.01, 1, r'$\mathbf{CMS}\ \mathit{Preliminary}$',
        ha='left', va='bottom', transform=ax.transAxes, fontsize=14,
    )
    ax.text(
        0.99, 1, r'$35.9\ \mathrm{fb}^{-1}(13\ \mathrm{TeV})$',
        ha='right', va='bottom', transform=ax.transAxes, fontsize=14,
    )
    plt.yticks(list(range(1,x.shape[0]+1)), y, fontsize=14)

    #ax.axvline(
    #    sm,
    #    ls='--',
    #    lw=0.8,
    #    color='black',
    #)

    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('none')

    print("zinv.pdf")
    fig.savefig("zinv.pdf", format="pdf", bbox_inches="tight")

if __name__ == "__main__":
    main()
