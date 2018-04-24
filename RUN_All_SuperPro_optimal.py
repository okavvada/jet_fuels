import SuperPro_data as SP_data
import json
import argparse, sys, os


parser=argparse.ArgumentParser()

parser.add_argument('--path', help='this is the data file path')
parser.add_argument('--feedstock', choices=['corn_stover','sorghum'], help='Select your feedstock')
parser.add_argument('--fuel', choices=['ethanol','jet_fuel'], help='Select your fuel')
parser.add_argument('--preprocess', choices=['waterwash', 'iHG-Current', 'iHG-Projected', 'All'], help='Select the preprocessing step')
parser.add_argument('--output', help='Select the output folder')

args=parser.parse_args()
process = ['Optimal']
cats = ['1,8-cineole', 'Bisabolene', 'Epi-isozizaene', 'Limonene', 'Linalool']
secnarios = ['OP_ICR']

for proc in process:
	for cat in cats:
		for scenario in secnarios:
			path = args.path + '/' + proc + '/' + cat + '-' + scenario + '.xls'

			result = SP_data.SuperPro_translate(path, args.feedstock, args.fuel, args.preprocess, cat, scenario, 'Aerobic')

			if not os.path.exists(args.output+'/optimal'):
				os.makedirs(args.output+'/optimal')

			with open('{}/optimal/SuperPro_data_{}_{}_{}.js'.format(args.output, proc, cat, scenario), 'w') as outfile:
			    json.dump(result, outfile)
