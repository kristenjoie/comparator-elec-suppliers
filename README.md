# comparator-elec-suppliers

Calculate and Compare price for different electricity suppliers

## 🚥 Pre-requisites
Download consumption file from [Enedis.fr](https://enedis.fr) 

## 🏗️ Install
```
pip3 install pandas
```

## 🚀 Run
```
python3 calcul.py consumption.csv
```
With options:
- `--year` to select the year
- `--month` to select the month

## Example of results
Consumption is in kW
Price are in euro (€ TTC)

```
Consumption for day 0 is HP: 24.951 HC: 33.915 total: 58.866
Consumption for day 1 is HP: 30.434 HC: 25.968 total: 56.402
Consumption for day 2 is HP: 29.561 HC: 21.579 total: 51.14
Consumption for day 3 is HP: 21.916 HC: 40.106 total: 62.022000000000006
Consumption for day 4 is HP: 27.141 HC: 36.173 total: 63.314
Consumption for day 5 is HP: 34.961 HC: 34.707 total: 69.668
Consumption for day 6 is HP: 28.073 HC: 16.785 total: 44.858000000000004
-----------------------------------------------------------------------
Consumption is HP: 197.037 HC: 209.233 total: 406.27
-----------------------------------------------------------------------
(Supplier)          (Contract Name + Option)                 (Subscrtion Price)    (Total price)
Mint energie         Summer HP/HC                             sub: 18.24           total: 80.0898
Vattenfall           HP/HC                                    sub: 17.30           total: 81.1738
Mint energie         Summer                                   sub: 16.87           total: 82.1170
EDF                  Tarif Bleu HP/HC                         sub: 15.30           total: 82.3318
TotalEnergie         Offre Essentielle                        sub: 14.16           total: 82.4134
...
```
