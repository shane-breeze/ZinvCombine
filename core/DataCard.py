from collections import namedtuple
from collections import OrderedDict as odict

Region = namedtuple('Region', ['obs', 'processes'])
Process = namedtuple('Process', ['idx', 'rate', 'systematics'])
Systematic = namedtuple('Systematic', ['value'])

class DataCard(object):
    def __init__(self, filename):
        self.filename = filename
        self.regions = odict()
        self.systematics = odict()
        self.rate_params = []

    def add_region(self, region, obs):
        self.regions[region] = Region(str(obs), odict())

    def add_process(self, region, process, idx, rate):
        r = str(rate) if rate != 0. else "1e-10"
        self.regions[region].processes[process] = Process(idx, r, odict())

    def add_systematic(self, region, process, systematic, pdf, value):
        if systematic not in self.systematics:
            self.systematics[systematic] = pdf
        self.regions[region].processes[process].systematics[systematic] = Systematic(value)

    def add_rateparam(self, param, region, process, value, *args):
        additional_args = ""
        if len(args) == 2:
            additional_args = "[{},{}]".format(*args)
        elif len(args) > 1:
            additional_args = args[0]
        else:
            additional_args = ""

        self.rate_params.append(
            [param, "rateParam", region, process, str(value), additional_args]
        )

    def sort_systematics(self, sorted_list):
        if set(sorted(self.systematics.keys())) != set(sorted(sorted_list)):
            missing = list(set(sorted(self.systematics.keys())) - set(sorted(sorted_list)))
            print "Trying to sort systematics, but missing: {}\nWill skip sorting".format(missing)
            return
        self.systematics = odict([(k, self.systematics[k]) for k in sorted_list])

    def textblock_break(self):
        return self.format_lines([['------------']])

    def textblock_header(self):
        lines = [
            ["imax", "*", "number of channels"],
            ["jmax", "*", "number of backgrounds"],
            ["kmax", "*", "number of nuisance parameters"],
        ]
        return self.format_lines(lines)

    def textblock_bins(self):
        """
        e.g.
        [
            ['bin', 'monojet', 'singlemu', 'doublemu'],
            ['observation', '155933.0', '63095.0', '7286.0'],
        ]
        """
        lines = [
            ["bin"] + self.regions.keys(),
            ["observation"] + [reg.obs for reg in self.regions.values()],
        ]
        return self.format_lines(lines)

    def textblock_procs(self):
        """
        e.g.
        [
            ['bin', 'monojet', 'monojet', 'monojet', 'monojet', 'singlemu', 'singlemu', 'singlemu', 'doublemu', 'doublemu', 'doublemu'],
            ['process', 'znunu', 'wlnu', 'qcd', 'bkg', 'wlnu', 'qcd', 'bkg', 'dymumu', 'qcd', 'bkg'],
            ['process', '0', '1', '2', '3', '1', '2', '3', '0', '1', '2'],
            ['rate', '91060.8', '53907.3', '298.7', '4108.7', '61873.6', '641.6', '4117.1', '7341.8', '1e-10', '204.2'],
        ]
        """
        lines = [
            ["bin"] + [entry
                       for regname, reg in self.regions.items()
                       for entry in [regname]*len(reg.processes)],
            ["process"] + [procname
                           for reg in self.regions.values()
                           for procname in reg.processes.keys()],
            ["process"] + [str(proc.idx)
                           for reg in self.regions.values()
                           for proc in reg.processes.values()],
            ["rate"] + [proc.rate
                        for reg in self.regions.values()
                        for proc in reg.processes.values()],
        ]
        return self.format_lines(lines)

    def textblock_systs(self):
        """
        create lines of columns, e.g.:
        [
            ['CMS_lumi', 'lnN', '1.025', '-', '-', '1.025', '-', '-', '1.025', '1.025', '-', '1.025'],
            ...
        ]
        where the values are for the respective (region, process). '-' are for
        (region, process) where the systematic isn't applied
        """
        lines = [
            [systname, pdf] + [
                str(proc.systematics[systname].value) \
                    if systname in proc.systematics \
                    else '-'
                for regname, reg in self.regions.items()
                for procname, proc in reg.processes.items()
            ] for systname, pdf in self.systematics.items()
        ]
        return self.format_lines(lines)

    def textblock_rate_params(self):
        """
        e.g.
        [
            ['tf_wlnu', 'rateParam', 'monojet', 'wlnu', '1'],
            ['tf_wlnu', 'rateParam', 'singlemu', 'wlnu', '1'],
            ['r_mumu', 'rateParam', 'doublemu', 'dymumu', '1'],
            ['r_nunu', 'rateParam', 'monojet', 'znunu', '(@0*@1) r,r_mumu'],
        ]
        """
        lines = [rate_param for rate_param in self.rate_params]
        return self.format_lines(lines)

    def format_lines(self, lines):
        row_maxes = [max([len(entry) for entry in rows]) for rows in zip(*lines)]
        return "\n".join([
            " ".join([entry+" "*(row_max-len(entry))
                for row_max, entry in zip(row_maxes, columns)
            ]).rstrip() for columns in lines
        ])

    def write(self):
        lines = "\n".join([
            self.textblock_header(),
            self.textblock_break(),
            self.textblock_bins(),
            self.textblock_break(),
            self.textblock_procs(),
            self.textblock_break(),
            self.textblock_systs(),
            self.textblock_break(),
            self.textblock_rate_params(),
        ])
        with open(self.filename, 'w') as f:
            f.write(lines)
        print "Created datacard {}".format(self.filename)

    def clear(self):
        self.filename = None
        self.regions = odict()
        self.systematics = odict()
        self.rate_params = []
