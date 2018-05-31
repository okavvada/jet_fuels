import SuperPro_data as SP_data
import json
import argparse, sys, os


parser=argparse.ArgumentParser()

parser.add_argument('--path', help='this is the data file path')
parser.add_argument('--feedstock', choices=['corn_stover','sorghum'], help='Select your feedstock')
parser.add_argument('--fuel', choices=['ethanol','jet_fuel'], help='Select your fuel')
parser.add_argument('--optimal', choices=['True','False'], help='Select whether its an optimal scenario')
parser.add_argument('--preprocess', choices=['waterwash', 'iHG-Current', 'iHG-Projected', 'All'], help='Select the preprocessing step')
parser.add_argument('--output', help='Select the output folder')


args=parser.parse_args()
if args.optimal =='False':
	process = ['Aerobic', 'Microaerobic']
	ILs = ['Cholinium lysinate', 'Ethanolamine acetate']
	cats = ['1,8-cineole', 'Bisabolene', 'Epi-isozizaene', 'Limonene', 'Linalool', 'Isopentenol']
	secnarios = ['BY_ICR', 'CY_ICR', 'TY_ICR']

if args.optimal =='True':
	process = ['Aerobic']
	ILs = ['']
	cats = ['1,8-cineole', 'Bisabolene', 'Epi-isozizaene', 'Limonene', 'Linalool', 'Isopentenol']
	secnarios = ['OP_ICR']

for proc in process:
	for IL in ILs:
		for cat in cats:
			for scenario in secnarios:
				if args.optimal =='False':
					path = args.path + '/' + proc + '/' + IL + '/' + cat + '/' + cat + '-' + scenario + '.xls'
				if args.optimal =='True':
					path = args.path + '/Optimal/' + cat + '-' + scenario + '.xls'
				if not os.path.exists(path):
					continue
				result = SP_data.SuperPro_translate(path, args.feedstock, args.fuel, args.preprocess, cat, scenario, proc)

				if args.optimal =='False':
					if not os.path.exists(args.output+'/scenarios'):
						os.makedirs(args.output+'/scenarios')
					with open('{}/scenarios/SuperPro_data_{}_{}_{}_{}.js'.format(args.output, proc, IL, cat, scenario), 'w') as outfile:
						json.dump(result, outfile)
				if args.optimal =='True':
					if not os.path.exists(args.output+'/optimal'):
						os.makedirs(args.output+'/optimal')
					with open('{}/optimal/SuperPro_data_Optimal_{}_{}.js'.format(args.output, cat, scenario), 'w') as outfile:
						json.dump(result, outfile)
