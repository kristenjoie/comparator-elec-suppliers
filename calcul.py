import argparse
import pandas
import time
import json
import os

pandas.options.mode.chained_assignment = None  # default='warn'

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str,
                    help="path csv")
parser.add_argument("--month", type=int)
parser.add_argument("--year", type=int)
args = parser.parse_args()

suppliers = json.loads(open(os.path.dirname(os.path.realpath(__file__)) + "/suppliers.config.json").read())

df = pandas.read_csv(args.file, sep=";", skiprows=[0,1], engine='python', usecols=['Horodate', 'EAS F1', 'EAS F2', 'EAS F3', 'EAS F4', 'EAS F5', 'EAS F6'])
# remove lasts line without data to use
df = df.loc[0:(df['Horodate'] != "Periode").idxmin()-1,:]

# convert data columns
df.set_index('Horodate', drop=False, inplace=True)
df.Horodate = pandas.to_datetime(df.Horodate)
df["EAS F1"] = pandas.to_numeric(df["EAS F1"])
df["EAS F2"] = pandas.to_numeric(df["EAS F2"])
df["EAS F3"] = pandas.to_numeric(df["EAS F3"])
df["EAS F4"] = pandas.to_numeric(df["EAS F4"])
df["EAS F5"] = pandas.to_numeric(df["EAS F5"])
df["EAS F6"] = pandas.to_numeric(df["EAS F6"])

# Merge Red, White and Blue days
df = df.fillna(0)
df['consoHC'] = -df['EAS F1'].diff(-1) + -df['EAS F3'].diff(-1) +-df['EAS F5'].diff(-1)
df['consoHP'] = -df['EAS F2'].diff(-1) + -df['EAS F4'].diff(-1) +-df['EAS F6'].diff(-1)

FIRST_LOOP = True

def sort_days(df, month=None, year=None):
    if month is not None:
        df = df['{}-{}-01'.format(year, "%02d" % month):'{}-{}-01'.format(year, "%02d" % (month + 1))]
    elif year is not None:
        df = df['{}-01-01'.format(year):'{}-01-01'.format(year + 1)]
    

    df["Horodate"] = pandas.to_datetime(df["Horodate"], utc=True)

    for d in range(0, 7):
        df_d = df.loc[df["Horodate"].dt.weekday == d]
        HP = df_d['consoHP'].sum() / 1000
        HC = df_d['consoHC'].sum() / 1000
        print( "Consumption for day {} is HP: {} HC: {} total: {}".format(d, HP, HC, (HP+HC)))

def get_conso(weekend, day=None, month=None, year=None):
    global df, FIRST_LOOP
    if month is not None:
        df = df['{}-{}-01'.format(year, "%02d" % month):'{}-{}-01'.format(year, "%02d" % (month + 1))]
        length = 1
    elif year is not None:
        df = df['{}-01-01'.format(year):'{}-01-01'.format(year + 1)]
        d1 = df.iloc[-1]['Horodate']
        d2 = df.iloc[0]['Horodate']
        length = (d1.year - d2.year) * 12 + d1.month - d2.month + 1
    else :
        d1 = df.iloc[-1]['Horodate']
        d2 = df.iloc[0]['Horodate']
        length = (d1.year - d2.year) * 12 + d1.month - d2.month + 1
    
    HP = df['consoHP'].sum() / 1000
    HC = df['consoHC'].sum() / 1000

    if FIRST_LOOP :
        FIRST_LOOP = False
        print("-----------------------------------------------------------------------")
        print("Consumption is HP: {} HC: {} total: {}".format(HP, HC, (HP+HC)))
        print("-----------------------------------------------------------------------")
        print("(Supplier)          (Contract Name + Option)                 (Subscrtion Price)    (Total price)")
    if weekend :
        df.Horodate = pandas.to_datetime(df.Horodate, utc=True)
        df_wk = df.loc[df.Horodate.dt.weekday > 4]
        HP_we = df_wk['consoHP'].sum() / 1000
        HC_we = df_wk['consoHC'].sum() / 1000
        HP = HP - HP_we
        HC = HC - HC_we
    else: HP_we, HC_we = 0, 0 

    if day is not None and day in [0, 4]:
        df_d = df.loc[df.Horodate.dt.weekday == day]
        HP_d = df_d['consoHP'].sum() / 1000
        HC_d = df_d['consoHC'].sum() / 1000
        HP = HP - HP_d
        HC = HC - HP_d
    else: HP_d, HC_d = 0, 0 

    return HP, HC, HP_we, HC_we, HP_d, HC_d, length

def calculate_bill(contract, month=None, year=None):
    global df
    hp_price = contract["value"]["HP"]
    hc_price = contract["value"]["HC"]
    abo_price = contract["value"]["abo"]
    hp_we_price = contract["weekend"]["HP"] if "weekend" in contract else 0
    hc_we_price = contract["weekend"]["HC"] if "weekend" in contract else 0
    hp_d_price = contract["weekend"]["HP"] if "day" in contract else 0
    hc_d_price = contract["weekend"]["HC"] if "day" in contract else 0
    
    we = True if "weekend" in contract else False
    day = contract["day"] if "day" in contract else None
    hp, hc, hp_we, hc_we, hp_d, hc_d, length = get_conso(we, day, month, year)
    abo = ( length * ( abo_price / 12 ) )
    bill = abo + ( hp_price* hp ) + ( hc_price * hc ) + ( hp_we_price * hp_we ) + ( hc_we_price * hc_we ) + ( hp_d_price * hp_d ) + ( hc_d_price * hc_d ) 
    return abo, bill

if __name__ == '__main__':
    sort_days(df, args.month, args.year)

    # compute data for each suppliers
    result = []
    for f in suppliers:
        for c in f["contrats"]:
            abo, bill = calculate_bill(c, args.month, args.year)
            result.append({'name': f["name"], 'contrat': c["name"], 'abo': abo, 'bill': bill})

    # sort and print results
    newlist = sorted(result, key=lambda d: d['bill']) 
    for i in newlist:
        print("{0:<20} {1:<40} sub: {2:<15} total: {3}".format(i["name"], i["contrat"], "%.2f" % i["abo"], "%.4f" % i["bill"]))
