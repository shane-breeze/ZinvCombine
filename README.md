# Zinv Combine

Code to write combine datacards and run combine for the zinv width analysis

## Creating datacards

To create the datacards for use with the combine tool we need the input
root files from AlphaTools which have distributions for all regions and
relevant processes, including variations under systematic uncertainties. In the
same directory as all of these root files create a yaml file that encodes the
structure in a nested dictionary with the following keys:
region, process, content/systs, name, up/down. An example is shown in the
example directory. Using this yaml file we can create the datacards by running
the following command:
```
generate_datacards.py -i examples/standard_analysis/inputs.yaml -o datacards/
```

This will create 3 datacards: monojet, singlemu and doublemu. We want to combine
these into a single datacard for a combined fit. This can be done with the
following command:
```
combineCards.py monojet=monojet.txt singlemu=singlemu.txt doublemu=doublemu.txt > zinv.txt
```

If we want to probe the ratio of branching fractions of Z to inv. and Z to mumu
we want to add rate parameters to this new file `zinv.txt` defined by
```
r_mumu = r * r_nunu
```
where `r_mumu` is the signal strength modifier for Z to mumu, `r_nunu` is the
signal strength modifier for Z to inv. and `r` is our new parameter of interest,
our ratio. We need to create a freely floating rate parameter `r_nunu` like so:
```
r_nunu rateParam monojet znunu 1
```
and we want to define the equation above with another rate parameter:
```
r_mumu rateParam doublemu dymumu (@0*@1) r,r_nunu
```
Note that `r` is the pre-defined POI and since `r_nunu` is freely floating then
`r` becomes our ratio.

If you want to do a 2D fit to `r_mumu` and `r_nunu` then comment out the rate
parameters defined above.

Example datacards can be found in the `examples/datacards` directory.

## Creating workspaces

It's useful to create the workspaces to inspect the likelihood in RooFit data
formats. There are two scripts to do this:
```
scripts/createws.sh zinv.txt
scripts/create2Dws.sh zinv.txt
```

The standard one doesn't do anything fancy, it just runs:
```
text2workspace.py -m 91 zinv.txt --PO verbose
```

The 2D version will use the 2-POI Physics model:
```
text2workspace.py -m 91 -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO 'map=.*/znunu:r_nunu[1,0,10]' --PO 'map=.*/dymumu:r_mumu[1,0,10]' zinv.txt --PO verbose
```
where the 2 POIs are defined as `r_nunu` and `r_mumu`.

## Fitting

### Impacts

To see the impacts of the systematics on the POI run the `scripts/impacts.sh`
like so:
```
sh scripts/impacts.sh zinv.root
```

This will run a set of commands successively, so be wary if any step fails.

### ML Fit

The `mlfit.sh` script takes a workspace as an argument and performs a standard
maximum likelihood fit with 1 POI (typically the signal strength modifier). The
command that's ran is:
```
combine zinv.root -n Zinv -m 91 -M FitDiagnostics --forceRecreateNLL --saveNLL --plots --saveNormalizations --saveWithUncertainties --expectSignal 1
```

### NLL scan

A NLL scan of the POI can be done by running the `llscan.sh` script on a
workspace. This runs the following commands:
```
combine -M MultiDimFit --algo grid --points 100 --rMin 0.9 --rMax 1.3 zinv.root -m 91 -n ZinvLLScan --expectSignal 1
plot1DScan.py higgsCombineZinvLLScan.MultiDimFit.mH91.root
```


# Combine tool

## FitDiagnostics

To run the standard maximum likelihood fit, run the following command on your
datacard:

```
combine monojet-datacard.txt -n Zinv -m 91 -M FitDiagnostics --forceRecreateNLL --saveNLL --plots --saveNormalizations --saveWithUncertainties
```

## Plotting

To view the systematics of a datacard easily in html, you can run the following
script:

```
python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/systematicsAnalyzer.py monojet-datacard-fakeshape.txt --all -m 91 -f html > monojet_systematics.html
```

## Output

Output of higgs combine is mostly in the form of a root file called e.g.
`fitDiagnosticsZinv.FitDiagnostics.mH91.root`. Inside this is a `TTree` called
`limit` with the following branches:

* `limit` - signal (e.g. zinv) strength modifier
* `limitErr` - esimated uncertainty on the result
* `mh` - mass parameter (meaningless here)
* `syst` - whether or not systematics (constrained nuisances) were included (floating)
* `iToy` - toy number id with `-t` option
* `iSeed` - seed with `-s` option
* `t_cpu` - estimated cpu time for algo
* `t_real` - estimated real time for algo
* `quantileExpected` - which quantile the limit is for (-1 is for observed)

## Options
Common options to be used in higgs combine for the different running method:

```
General:
--saveWorkspace
--saveToys

FitDiagnostics:
--saveNLL
--forceRecreateNLL
--plots
--saveNormalizations
--savePredictionsPerToy
--saveShapes
--saveWithUncertainties
--saveOverallShapes
--numToysForShapes 1000

MultiDimFit:
--saveNLL
--forceRecreateNLL
--fastScan
--saveSpecifiedNuis arg
--saveSpecifiedFunc arg
--saveSpecifiedIndex arg
--saveInactivePOI arg
--saveFitResult
```
