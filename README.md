# Zinv Combine

Code to write combine datacards and run combine for the zinv width analysis

## Combine tool

### FitDiagnostics

To run the standard maximum likelihood fit, run the following command on your
datacard:

```
combine monojet-datacard.txt -n Zinv -m 91 -M FitDiagnostics --forceRecreateNLL --saveNLL --plots --saveNormalizations --saveWithUncertainties
```

### Plotting

To view the systematics of a datacard easily in html, you can run the following
script:

```
python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/systematicsAnalyzer.py monojet-datacard-fakeshape.txt --all -m 91 -f html > monojet_systematics.html
```

### Output

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

### Options
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
