import ROOT
import np

def erf_func(x, par):
    x    = x[0]
    norm   = par[0]
    offset = par[1]
    width  = par[2]
    return 0.5*norm*(1 + ROOT.TMath.Erf((x - offset)/(np.sqrt(2)*width)))

def crystalballEfficiency(x, par):
    x     = x[0]
    m0    = par[0]
    sigma = par[1]
    alpha = par[2]
    n     = par[3]
    norm  = par[4]
    return _crystalballEfficiency( x, m0, sigma, alpha, n, norm )

def doubleCrystalballErrfEfficiency(x, par):
    x     = x[0]
    m0_1    = par[0]
    sigma_1 = par[1]
    alpha_1 = par[2]
    n_1     = par[3]
    norm_1  = par[4]
    m0_2    = par[5]
    sigma_2 = par[6]
    alpha_2 = par[7]
    n_2     = par[8]
    norm_2  = par[9]
    return _crystalballEfficiency( x, m0_1, sigma_1, alpha_1, n_1, norm_1 ) + \
           _crystalballEfficiency( x, m0_2, sigma_2, alpha_2, n_2, norm_2 )

def _crystalballEfficiency(m, m0, sigma, alpha, n, norm):
    sqrt_pi_half = np.sqrt(np.pi/2)
    sqrt_two     = np.sqrt(2.)
    sig          = abs(sigma)
    t            = (m - m0)/sig * alpha / abs(alpha)
    abs_alpha    = abs(alpha/sig)
    a            = (n/abs_alpha)**(n) * np.exp(-0.5*abs_alpha**2)
    b            = abs_alpha - n/abs_alpha
    arg          = abs_alpha / sqrt_two

    if   arg >  5.: approx_erf =  1.
    elif arg < -5.: approx_erf = -1.
    else          : approx_erf = ROOT.TMath.Erf(arg)

    left_area  = (1. + approx_erf) * sqrt_pi_half
    right_area = (a/((abs_alpha-b)**(n-1))) / (n-1)
    area       = left_area + right_area

    if t <= abs_alpha:
        arg = t / sqrt_two
        if   arg >  5.: approx_erf =  1.
        elif arg < -5.: approx_erf = -1.
        else          : approx_erf = ROOT.TMath.Erf(arg)
        return norm * (1 + approx_erf) * sqrt_pi_half / area
    else:
        return norm * (left_area + a * (1/((t-b)**(n-1)) - \
                                        1/((abs_alpha-b)**(n-1)) / (1-n)) / area
