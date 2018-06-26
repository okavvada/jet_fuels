import json
import argparse, sys, os
import pandas as pd
from Final_Impact_Model import FinalImpactModel

parser=argparse.ArgumentParser()

parser.add_argument('--input_path', help='Set the input data path')
parser.add_argument('--output_path', help='Set the output data path')
parser.add_argument('--fuel', choices=['1,8-cineole', 'Bisabolene', 'Epi-isozizaene', 'Limonene', 'Linalool','Isopentenol', 'All'], help='Select your jetfuel')
parser.add_argument('--electricity', choices=['grid','net'], help='Select your electricity source')
parser.add_argument('--optimal', choices=['True','False'], help='Select scenario')
parser.add_argument('--model', choices=['GHG','WithWater','ConsWater'], help='Select GHG or Water run')

args=parser.parse_args()

if not os.path.exists(args.output_path):
    os.makedirs(args.output_path)

if args.fuel == 'All':
    fuels = ['1,8-cineole', 'Bisabolene', 'Epi-isozizaene', 'Limonene', 'Linalool']
else:
    fuels = [args.fuel]

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

titles = ["Feedstock_Supply_Logistics", "Feedstock_Handling_and_Preparation", "IL_Pretreatment",
			"Enzymatic_Hydrolysis_and_Fermentation", "Recovery_and_Separation", "Hydrogeneration_and_Oligomerization",
			"Wastewater_Treatment", "Lignin_Utilization", "Credits", "Direct_Water"]
columns = titles[:]
columns.append("Scerario_Name")

button = 'button' + args.model

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
            for scenario in scenarios:
                if args.optimal == 'False':
                    path = args.input_path + '/scenarios/SuperPro_data_{}_{}_{}_{}.js'.format(process, IL, fuel, scenario)
                    if not os.path.exists(path):
                        continue
                else:
                    path = args.input_path + '/optimal/SuperPro_data_{}_{}_{}.js'.format(process, fuel, scenario)
                    if not os.path.exists(path):
                        continue
                data = json.load(open(path))
                if IL == 'Cholinium lysinate':
                    ionic_liquid = 'ChLys'
                if IL == 'Ethanolamine acetate':
                    ionic_liquid = 'EMIM'
                result = FinalImpactModel(data, 'sorghum', button, 'jet_fuel', fuel, ionic_liquid, credits=cred)
                result['Scerario_Name'] = '{}_{}_{}_{}'.format(process, IL, fuel, scenario)
                all_results = all_results.append(result)
sum_cols = titles[:]

if args.model == 'GHG':
    if args.electricity == 'net':
    	sum_cols.append('electricity_requirements')
    all_results['Total_gCO2_MJ'] = all_results[sum_cols].sum(axis=1)
    all_results['Total_gCO2_MJ_net'] = all_results['Total_gCO2_MJ'] + all_results['electricity_generated'] + all_results['steam_credits']
else:
    if args.electricity == 'net':
        sum_cols.append('electricity_requirements')
    all_results['Total_liters_MJ'] = all_results[sum_cols].sum(axis=1)
    all_results['Total_liters_MJ_net'] = all_results['Total_liters_MJ'] + all_results['electricity_generated']
    # all_results['Total_liters_MJ'] = all_results[sum_cols].sum(axis=1)

final = all_results.set_index('Scerario_Name')
final.to_csv(args.output_path + '/LCA_results_{}_{}_{}.csv'.format(opt, args.electricity, args.model))

