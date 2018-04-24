import json
import argparse, sys, os
import pandas as pd

parser=argparse.ArgumentParser()

parser.add_argument('--path')
parser.add_argument('--optimal')
args=parser.parse_args()

if args.optimal == 'True':
	process = ['Aerobic', 'Microaerobic']
	ILs = ['Cholinium lysinate', 'Ethanolamine acetate']
	cats = ['1,8-cineole', 'Bisabolene', 'Epi-isozizaene', 'Limonene', 'Linalool']
	secnarios = ['BY_ICR', 'CY_ICR', 'TY_ICR']
	name = 'scenarios'
else:
	process = ['Optimal']
	cats = ['1,8-cineole', 'Bisabolene', 'Epi-isozizaene', 'Limonene', 'Linalool']
	secnarios = ['OP_ICR']
	name = 'optimal'
df_all = pd.DataFrame()
for proc in process:
for IL in ILs:
	for cat in cats:
		for scenario in secnarios:
			data = args.path + '/' + name + '/SuperPro_data_/'+ proc + '/' + IL + '/' + cat + '_' + scenario + '.js'
			electricity = 0
			natural_gas = 0

			for process in data.keys():
				if process == 'fuel_kg':
					fuel = data[process]
					continue
				for item in process.keys():
					if item == 'electricity':
						electricity += data[process][item]
					if item == 'ng_input_stream_MJ':
						natural_gas += data[process][item]
					if item == 'electricity_generated':
						elect_cred = data[process][item]

			scen = proc + '/' + IL + '/' + cat + '_' + scenario + '_' + name
			all_data = [scen, fuel, electricity*fuel, natural_gas*fuel/52.2, elect_cred*fuel]
			df = pd.DataFrame(all_data, columns=['scenario', 'fuel_kg', 'electricity_req', 'methane_req', 'electricity_gen'])
			df_all = df_all.append(df)
