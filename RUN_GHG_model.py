import json
import argparse, sys, os
import pandas as pd
from Final_Impact_Model import FinalImpactModel

parser=argparse.ArgumentParser()

parser.add_argument('--electricity', choices=['grid','net'], help='Select your electricity source')
parser.add_argument('--optimal', choices=['True','False'], help='Select scenario')

args=parser.parse_args()

if not os.path.exists('results'):
    os.makedirs('results')

if args.optimal=='True':
    processes = ['Optimal']
    ILs = ['Ethanolamine acetate']
    scenarios = ['OP_ICR']
    opt = 'optimal'
else:
    processes = ['Aerobic', 'Microaerobic']
    ILs = ['Cholinium lysinate',  'Ethanolamine acetate']
    scenarios = ['BY_ICR', 'CY_ICR', 'TY_ICR']
    opt = 'all'

if args.electricity=='grid':
	cred = False
else:
	cred = True
fuels = ['1,8-cineole', 'Bisabolene', 'Epi-isozizaene', 'Limonene', 'Linalool']

titles = ["Feedstock_Supply_Logistics", "Feedstock_Handling_and_Preparation", "IL_Pretreatment",
			"Enzymatic_Hydrolysis_and_Fermentation", "Recovery_and_Separation", "Hydrogeneration_and_Oligomerization",
			"Wastewater_Treatment", "Lignin_Utilization"]
columns = titles[:]
columns.append("Scerario_Name")

catalysts = {
            "alcl3": 1.91,
            "ru": 10,
            "deh_cat": 3.75,
            "PdAC_catalyst": 8.308
}

all_results = pd.DataFrame(columns = columns)
for process in processes:
    for IL in ILs:
        for fuel in fuels:
            if fuel == '1,8-cineole': 
                hhv_jet_fuel = 46.6
                density_jet_fuel = 0.922
            if fuel == 'Bisabolene': 
                hhv_jet_fuel = 46.68
                density_jet_fuel = 0.879
            if fuel == 'Epi-isozizaene': 
                hhv_jet_fuel = 46.68
                density_jet_fuel = 0.879
            if fuel == 'Limonene': 
                hhv_jet_fuel = 45.04
                density_jet_fuel = 0.841
            if fuel == 'Linalool': 
                hhv_jet_fuel = 42.18
                density_jet_fuel = 0.858
            for scenario in scenarios:
                if args.optimal == 'False':
                    path = 'static/scenarios/SuperPro_data_{}_{}_{}_{}.js'.format(process, IL, fuel, scenario)
                else:
                    path = 'static/optimal/SuperPro_data_{}_{}_{}.js'.format(process, fuel, scenario)
                data = json.load(open(path))
                if IL == 'Cholinium lysinate':
                    ionic_liquid = 'ChLys'
                if IL == 'Ethanolamine acetate':
                    ionic_liquid = 'EMIM'
                result = FinalImpactModel(data, 'sorghum', 'buttonGHG', 'jet_fuel', catalysts, fuel, ionic_liquid, credits=cred)*1000/hhv_jet_fuel
                result['Scerario_Name'] = '{}_{}_{}_{}'.format(process, IL, fuel, scenario)
                all_results = all_results.append(result)

sum_cols = titles[:]
if args.electricity == 'net':
	sum_cols.append('electricity_requirements')
all_results['Total_gCO2_MJ'] = all_results[sum_cols].sum(axis=1)
all_results['Total_gCO2_MJ_net'] = all_results['Total_gCO2_MJ'] + all_results['electricity_generated'] + all_results['steam_credits']

final = all_results.set_index('Scerario_Name')
final.to_csv('results/LCA_results_{}_{}.csv'.format(opt, args.electricity))

