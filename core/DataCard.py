from collections import namedtuple
from collections import OrderedDict as odict

Region = namedtuple('Region', ['obs', 'processes'])
Process = namedtuple('Process', ['idx', 'rate', 'systematics'])
Systematic = namedtuple('Systematic', ['value'])

class DataCard(object):
    def __init__(self, filename):
        self.filename = filename
        self.f = open(filename, 'w')
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
            " ".join([param, "rateParam", region, process, str(value), additional_args])
        )

    def write_break(self):
        self.f.write("------------\n")

    def write_header(self):
        self.f.write("imax *  number of channels\n")
        self.f.write("jmax *  number of backgrounds\n")
        self.f.write("kmax *  number of nuisance parameters\n")

    def write_bins(self):
        line = "bin         "
        line += " ".join(self.regions.keys())
        self.f.write(line+"\n")

        line = "observation "
        line += " ".join([reg.obs for regionname, reg in self.regions.items()])
        self.f.write(line+"\n")

    def write_procs(self):
        line = "bin         "
        line += " ".join([" ".join([regname]*len(reg.processes)) for regname, reg in self.regions.items()])
        self.f.write(line+"\n")

        line = "process     "
        line += " ".join([procname
            for reg in self.regions.values()
            for procname in reg.processes.keys()
        ])
        self.f.write(line+"\n")

        line = "process     "
        line += " ".join([str(proc.idx)
            for reg in self.regions.values()
            for proc in reg.processes.values()
        ])
        self.f.write(line+"\n")

        line = "rate        "
        line += " ".join([proc.rate
            for reg in self.regions.values()
            for proc in reg.processes.values()
        ])
        self.f.write(line+"\n")

    def write_systs(self):
        for systname, pdf in self.systematics.items():
            line = "{} {} ".format(systname, pdf)
            to_add = []
            for regname, reg in self.regions.items():
                for procname, proc in reg.processes.items():
                    if systname in proc.systematics:
                        value = str(proc.systematics[systname].value)
                    else:
                        value = '-'
                    to_add.append(value)
            line += " ".join(to_add)
            self.f.write(line+"\n")

    def write_rate_params(self):
        for rate_param in self.rate_params:
            self.f.write(rate_param+"\n")

    def write(self):
        self.write_header()
        self.write_break()
        self.write_bins()
        self.write_break()
        self.write_procs()
        self.write_break()
        self.write_systs()
        self.write_break()
        self.write_rate_params()
        self.f.close()
        print "Created datacard {}".format(self.filename)
