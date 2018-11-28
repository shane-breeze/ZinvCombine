# Zinv Combine

Code to run combine for the zinv width analysis

## Fitting

### Impacts

To see the impacts of the systematics on the POI run the `scripts/impacts.sh`
like so:
```
impacts.sh datacard.txt "-t -1" "Exp"
impacts.sh datacard.txt "" "Obs"
```

This will run a set of commands successively, so be wary if any step fails.

### ML Fit

The `mlfit.sh` script takes a datacard as an argument and performs a standard
maximum likelihood fit with 1 POI (typically the signal strength modifier).

### NLL scan

A NLL scan of the POI can be done by running the `llscan.sh` script on a
datacard.
