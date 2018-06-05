import json
import argparse, sys, os
import pandas as pd
from ParameterValues_MonteCarlo import ParameterValues

parser=argparse.ArgumentParser()

parser.add_argument('--input_path', help='Set the input data path')
parser.add_argument('--output_path', help='Set the output data path')
parser.add_argument('--model', choices=['GHG','WithWater','ConsWater'], help='Select GHG or Water run')
parser.add_argument('--risk', choices=['uncertainty','sensitivity'], help='Select risk analysis to run')
parser.add_argument('--fuel', choices=['1,8-cineole', 'Bisabolene', 'Epi-isozizaene', 'Limonene', 'Linalool','Isopentenol'], help='Select your jetfuel')

args=parser.parse_args()

if not os.path.exists(args.output_path):
    os.makedirs(args.output_path)

SuperPro_names = {
    "Corn Liquor": "csl.kg",
    "Diammonium phos": "dap.kg",
    "EMIM Acetate": "ionicLiquid_amount",
    "ChLy": "ionicLiquid_amount",
    "Hydrolase": "cellulase_amount",
    "Methane": "ng_input_stream_MJ",
    "NaOH (50% w/w)": "naoh.kg",
    "Octane": "octane_ltr",
    "Std Power": "electricity",
    "Stover": "feedstock.kg",
    "WWT nutrients": "caoh.kg",
    "Sulfuric Acid": "acid.kg",
    "Water": "water_direct_consumption",
    "Hydrogen": "h2.kg",
    "Inoculum": "inoculum.kg",
    "CIP2": "cip2.kg",
    "AlCl3": "alcl3.kg", 
    "dehydrating Cat": "cat.kg",
    "Ru": "ru.kg",
    "Pd/AC Catalyst": "PdAC_catalyst.kg",
    "Cooling Water": "cooling_water",
    "CoolingWater25C": "cooling_water25",
    "Chilled Water": "chilled_water",
    "electricity_generated": "electricity_generated"
}

sections_translate = {  "Feedstock supply logistics": "Feedstock_Supply_Logistics",
                        "Feedstock handling": "Feedstock_Handling_and_Preparation", 
                        "Pretreatment": "IL_Pretreatment", 
                        "Hydrolysis and fermentation": "Enzymatic_Hydrolysis_and_Fermentation", 
                        "Wastewater treatment": "Wastewater_Treatment",
                        "Hydrogenation": "Hydrogeneration_and_Oligomerization",
                        "Recovery and separation": "Recovery_and_Separation", 
                        "Lignin utilization": "Lignin_Utilization",
                        "Credits": "Credits",
                        "Direct_Water": "Direct_Water"}

fuels = [args.fuel]

titles = ["Feedstock_Supply_Logistics", "Feedstock_Handling_and_Preparation", "IL_Pretreatment",
			"Enzymatic_Hydrolysis_and_Fermentation", "Recovery_and_Separation", "Hydrogeneration_and_Oligomerization",
			"Wastewater_Treatment", "Lignin_Utilization", "Credits", "Direct_Water"]

columns = titles[:]
columns.append("Scerario_Name")

button = 'button' + args.model

def convertDfToDict(data):
    final_dict = {}
    grouped = data.groupby(data.columns[0])
    for process in processes:
        new_process_name = sections_translate[process]
        d={}
        for i, row in grouped.get_group(process).iterrows():
            if 'Steam' in row['Material']:
                new_material_name = 'steam_low'
                
            elif row['Material'] not in SuperPro_names.keys():
                new_material_name = row['Material']
            else:
                new_material_name = SuperPro_names[row['Material']]
            if 'Methane' in row['Material']:
                d.update({new_material_name:{'Baseline': row['Baseline'],
                                              'Minimum': row['Minimum '],
                                             'Maximum': row['Maximum'],
                                             'Std_Dev': row['Std_Dev']}})
            
            else:
                d.update({new_material_name:{'Baseline': row['Baseline'],
                                              'Minimum': row['Minimum '],
                                             'Maximum': row['Maximum'],
                                             'Std_Dev': row['Std_Dev']}})
        final_dict.update({new_process_name:d})
    return final_dict

if args.fuel == 'Isopentenol':
    data_path = 'data_isopentenol'
else:
    data_path = 'data'

if args.risk == 'sensitivity':
    for fuel in fuels:
        data = pd.read_csv(data_path+'/Risk/{}.csv'.format(args.fuel))
        processes = list(data['Process'].unique())
        risk_params = convertDfToDict(data)
        path = args.input_path + '/scenarios/SuperPro_data_Aerobic_Cholinium lysinate_{}_BY_ICR.js'.format(fuel)
        parameters = json.load(open(path))
        
        Params = ParameterValues(parameters, risk_params)
        sensi_params = Params.sensitivity(fuel, 'ChLys', button)
        
        final_df = pd.DataFrame()
        for process in sensi_params.keys():
            datafr = pd.DataFrame.from_dict(sensi_params[process]).T
            datafr['Process'] = process
            final_df = final_df.append(datafr)
        final_df=final_df.reset_index()
        final_df = final_df.rename(index=str, columns={'index': 'Material'})
        final_df.to_csv(args.output_path + '/sensitivity_{}_{}.csv'.format(fuel, args.model))


if args.risk == 'uncertainty':
    for fuel in fuels:
        final_df = pd.DataFrame()
        data = pd.read_csv(data_path+'/Risk/{}.csv'.format(fuel))
        processes = list(data['Process'].unique())
        risk_params = convertDfToDict(data)
        path = args.input_path + '/scenarios/SuperPro_data_Aerobic_Cholinium lysinate_{}_BY_ICR.js'.format(fuel)
        parameters = json.load(open(path))
        Params = ParameterValues(parameters, risk_params)
        for i in range(5000):
            uncertain_df = Params.uncertainty(fuel, 'ChLys', button)
            final_df = final_df.append(uncertain_df)
        final_df.to_csv(args.output_path + '/uncertainty_{}_{}.csv'.format(fuel, args.model))