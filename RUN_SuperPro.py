import SuperPro_data as SP_data
import json
import argparse, sys

parser=argparse.ArgumentParser()

parser.add_argument('--path', help='this is the xls file path')
parser.add_argument('--feedstock', choices=['corn_stover','sorgum'], help='Select your feedstock')
parser.add_argument('--fuel', choices=['ethanol','jet_fuel'], help='Select your fuel')
parser.add_argument('--preprocess', choices=['waterwash', 'iHG-Current', 'iHG-Projected', 'All'], help='Select the preprocessing step')
parser.add_argument('--process', choices=['Aerobic', 'Microaerobic'], help='Select the processing step')
parser.add_argument('--IL', choices=['Cholinium lysinate', 'Ethanolamine acetate'], help='Select the IL')
parser.add_argument('--cat', choices=['1,8-cineole', 'Bisabolene', 'Epi-isozizaene', 'Limonene', 'Linalool'], help='Select the catalyst')
parser.add_argument('--scenario', choices=['BY_ICR', 'CY_ICR', 'TY_ICR'], help='Select the IL')


args=parser.parse_args()

path = args.path + '/' + args.process + '/' + args.IL + '/' + args.cat + '/' + args.cat + '-' + args.scenario + '.xls'

result = SP_data.SuperPro_translate(path, args.feedstock, args.fuel, args.preprocess, args.cat)

with open('static/SuperPro_data_{}_{}_{}_{}.js'.format(args.process, args.IL, args.cat, args.scenario), 'w') as outfile:
    json.dump(result, outfile)
