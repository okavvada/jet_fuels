import pandas as pd
import numpy as np
import parameters as P
import helper_functions as hf
from unit_conversions_and_mw.feedstock_conversions import *


io_data = pd.read_csv(P.io_table_physicalunits_path).fillna(0)
water_consumption = hf.csv_dict_list(P.water_consumption_path)
water_withdrawal = hf.csv_dict_list(P.water_withdrawal_path)
# Ethanol produciton functional unit (1 kg of ethanol)
etoh_feed_stream_mass_kg = 1
hhv_methane = 52.2 # MJ/kg



def FinalImpactModel(SP_params, feedstock, model, fuel, catalysts, typefuel, ionic_liquid='ChLys', credits=True):
    # Returns a dataframe of of all GHG emissions in the form of kg CO2e per MJ enthanol  or 
    # water impacts in the form of Liters per MJ enthanol per process
    #
    # Args:
    #  SP_params: process specific parameters dictionary
    #  model: string refering to whether the GHG model or the water model is run. Options are:
    #  'buttonGHG', 'buttonConsWater', 'buttonWithWater' for the GHG model, the water consumption model and
    #  the withdrawal model respectively
    
    # Returns:
    #  The net GHG emissions (kg CO2e) for the product life cycle by sector for model = 'buttonGHG'
    #  The net consumption water impacts (liters) for the product life cycle by sector for model = 'buttonConsWater'
    #  The net withdrawal water impacts (liters) for the product life cycle by sector for model = 'buttonWithWater'
    if fuel == 'jet_fuel':
        selectivities = P.sections
    if fuel == 'logistics':
        selectivities = SP_params.keys()
    if fuel == 'ethanol':
        selectivities = P.selectivity

    SP_params['analysis_params'] = {
                                    'time_horizon': 100,
                                    'facility_electricity': 'US',
                                    'feedstock': feedstock,
                                    'fuel': fuel,
                                    'electricity_credits': SP_params['credits']['electricity_generated'],
                                    'steam_credits': SP_params['credits']['steam_generated']
                                     }
    m = {} 
    total_steam = 0

    new_data = np.zeros([len(selectivities), 1])
    m = pd.DataFrame(new_data, columns=['All'], index=selectivities)
    required_electricity = 0

    for selectivity in selectivities:
        y = {}
        y_cred = {}
        for item in io_data['products']:
            y.update({item:0})
            y_cred.update({item:0})
        biorefinery_direct_ghg = 0
        cooled_water_ghg = 0
        steam_ghg = 0
        catalyst_ghg = 0
        if fuel == 'ethanol':
            ionic_liquid_amount = SP_params[selectivity]['ionicLiquid_amount']
            feedstock_amount = SP_params[selectivity]['feedstock.kg']
        if fuel == 'jet_fuel':
            ionic_liquid_amount = SP_params['IL_Pretreatment']['ionicLiquid_amount']
            feedstock_amount = SP_params["Feedstock_Supply_Logistics"]['feedstock.kg']
        if 'acid.kg' in SP_params[selectivity].keys():
            if (SP_params[selectivity]['acid'] == 'hcl'):
                y["hcl.kg"] = SP_params[selectivity]['acid.kg']
            elif (SP_params[selectivity]['acid'] == 'h2so4'):
                y["h2so4.kg"] = SP_params[selectivity]['acid.kg']
        if 'ionicLiquid_amount' in SP_params[selectivity].keys():
            if ionic_liquid == 'ChLys':
                y["lysine.us.kg"] = ionic_liquid_amount * 0.58
                y["cholinium.hydroxide.kg"] = ionic_liquid_amount * 0.42  
            if ionic_liquid == 'EMIM':
                y["emim_acetate.kg"] = ionic_liquid_amount
        if 'cellulase_amount' in SP_params[selectivity].keys():
            y["cellulase.kg"] = SP_params[selectivity]['cellulase_amount']
        if 'csl.kg' in SP_params[selectivity].keys():
            y["csl.kg"] = SP_params[selectivity]['csl.kg']
        if 'feedstock.kg' in SP_params[selectivity].keys():
            if SP_params['analysis_params']['feedstock'] == 'corn_stover':
                y["farmedstover.kg"] = feedstock_amount
            if SP_params['analysis_params']['feedstock'] == 'sorghum':
                y["sorghum.kg"] = feedstock_amount
            if SP_params['analysis_params']['feedstock'] == 'mixed':
                y["sorghum.kg"] = feedstock_amount * 0.4
                y["farmedstover.kg"] = feedstock_amount * 0.4
                y["farmedmiscanthus.kg"] = feedstock_amount * 0.2
                y["switchgrass.kg"] = feedstock_amount * 0.2
        if 'dap.kg' in SP_params[selectivity].keys():
            y["dap.kg"] = SP_params[selectivity]['dap.kg']
        if 'caoh.kg' in SP_params[selectivity].keys():
            y["lime.kg"] = SP_params[selectivity]['caoh.kg']
        if 'naoh.kg' in SP_params[selectivity].keys():
            y["naoh.kg"] = SP_params[selectivity]['naoh.kg']
        if 'h2.kg' in SP_params[selectivity].keys():
            y["h2.kg"] = SP_params[selectivity]['h2.kg']
        if 'ng_input_stream_MJ' in SP_params[selectivity].keys():
            y["naturalgas.MJ"] = SP_params[selectivity]['ng_input_stream_MJ'] * hhv_methane
        if 'octane_ltr' in SP_params[selectivity].keys():
            y["gasoline.MJ"] = (hf.FuelConvertMJ(SP_params[selectivity]['octane_ltr'], "gasoline", "liter"))

        if (fuel == 'ethanol') or (selectivity == "Transportation"):
            y["rail.mt_km"] = ((ionic_liquid_amount * feedstock_amount/1000) * 
                            SP_params['common']['IL_rail_km'] +
                            (etoh_feed_stream_mass_kg/1000 * SP_params['common']['etoh_distribution_rail']) +
                            (feedstock_amount/1000) * 
                            SP_params['common']['feedstock_distribution_rail'])
            y["flatbedtruck.mt_km"] = (((ionic_liquid_amount * feedstock_amount/1000) * 
                                            SP_params['common']['IL_flatbedtruck_mt_km']) +
                                        (etoh_feed_stream_mass_kg/1000 * (
                                            SP_params['common']['etoh_distribution_truck'])) +
                                        (feedstock_amount/1000) * 
                                            SP_params['common']['feedstock_distribution_truck'])

        if 'electricity' in SP_params[selectivity].keys():
            required_electricity += SP_params[selectivity]['electricity']
            if credits == False:
                y["electricity.{}.kWh".format(SP_params['analysis_params']['facility_electricity'])] = (
                                                        SP_params[selectivity]['electricity'])
        if 'cooling_water' in SP_params[selectivity].keys():
            if 'water_direct_withdrawal' in SP_params[selectivity].keys():
                SP_params[selectivity]['water_direct_withdrawal'] += SP_params[selectivity]['cooling_water']
            else:
                SP_params[selectivity]['water_direct_withdrawal'] = SP_params[selectivity]['cooling_water']
            cooled_water_ghg += SP_params[selectivity]['cooling_water'] * hf.CooledWaterCO2kg('cooling_water')
        if 'cooling_water25' in SP_params[selectivity].keys():
            if 'water_direct_withdrawal' in SP_params[selectivity].keys():
                SP_params[selectivity]['water_direct_withdrawal'] += SP_params[selectivity]['cooling_water25']
            else:
                SP_params[selectivity]['water_direct_withdrawal'] = SP_params[selectivity]['cooling_water25']
            cooled_water_ghg += SP_params[selectivity]['cooling_water25'] * hf.CooledWaterCO2kg('cooling_water25')
        if 'chilled_water' in SP_params[selectivity].keys():
            if 'water_direct_withdrawal' in SP_params[selectivity].keys():
                SP_params[selectivity]['water_direct_withdrawal'] += SP_params[selectivity]['chilled_water']
            else:
                SP_params[selectivity]['water_direct_withdrawal'] = SP_params[selectivity]['chilled_water']
            cooled_water_ghg += SP_params[selectivity]['chilled_water'] * hf.CooledWaterCO2kg('chilled_water')
        if 'steam_low' in SP_params[selectivity].keys():
            steam_ghg += SP_params[selectivity]['steam_low'] * hf.CooledWaterCO2kg('steam_low')
            total_steam += SP_params[selectivity]['steam_low']
        if 'steam_high' in SP_params[selectivity].keys():
            steam_ghg += SP_params[selectivity]['steam_high'] * hf.CooledWaterCO2kg('steam_high')
            total_steam += SP_params[selectivity]['steam_high']
        if 'n.kg' in SP_params[selectivity].keys():
            y["n.kg"] = SP_params[selectivity]['n.kg']
        if 'p.kg' in SP_params[selectivity].keys():
            y["p.kg"] = SP_params[selectivity]['p.kg']
        if 'k.kg' in SP_params[selectivity].keys():
            y["k.kg"] = SP_params[selectivity]['k.kg']
        if 'diesel.MJ' in SP_params[selectivity].keys():
            y["diesel.MJ"] = SP_params[selectivity]['diesel.MJ']
        if 'direct_GHG' in SP_params[selectivity].keys():
            biorefinery_direct_ghg += SP_params[selectivity]['direct_GHG']
        if 'alcl3.kg' in SP_params[selectivity].keys():
            catalyst_ghg += catalysts['alcl3'] * SP_params[selectivity]['alcl3.kg']
        if 'ru.kg' in SP_params[selectivity].keys():
            catalyst_ghg += catalysts['ru'] * SP_params[selectivity]['ru.kg']
        if 'deh_cat.kg' in SP_params[selectivity].keys():
            catalyst_ghg += catalysts['deh_cat'] * SP_params[selectivity]['deh_cat.kg']
        if 'PdAC_catalyst.kg' in SP_params[selectivity].keys():
            catalyst_ghg += catalysts['PdAC_catalyst'] * SP_params[selectivity]['PdAC_catalyst.kg']

        if model == 'buttonGHG':

            results_kg_co2e = hf.TotalGHGEmissions(io_data, y,
                                                   biorefinery_direct_ghg, cooled_water_ghg, steam_ghg, catalyst_ghg, SP_params['analysis_params']['time_horizon'])

            results_kg_co2e_dict = results_kg_co2e.set_index('products')['ghg_results_kg'].to_dict()

            hf.AggregateResults(m, results_kg_co2e_dict, selectivity, fuel)

            if fuel == 'ethanol':
                m[selectivity] = m[selectivity] * 1000/27 # converting kg per kg results to g per MJ
                
            else:
                m['All'][selectivity] = m['All'][selectivity] # kg per kg


    if fuel == 'ethanol':
        aggregated_data_avg = m['avg'][selectivities].T
        aggregated_data_low = m['low'][selectivities].T
        aggregated_data_high = m['high'][selectivities].T
        
        if 'electricity_credit' in aggregated_data_avg.columns.values:
            aggregated_data_avg_pos = aggregated_data_avg.drop(['electricity_credit'],1)
        if 'steam_low_credit' in aggregated_data_avg.columns.values:
            aggregated_data_avg_pos = aggregated_data_avg.drop(['steam_low_credit'],1)
        if 'water_direct_consumption_credit' in aggregated_data_avg.columns.values:
            aggregated_data_avg_pos = aggregated_data_avg.drop(['water_direct_consumption_credit'],1)

    else:
        y = {}
        y_net = {}
        y_cred = {}
        for item in io_data['products']:
            y.update({item:0})
            y_net.update({item:0})
            y_cred.update({item:0})


        y["electricity.{}.kWh".format(SP_params['analysis_params']['facility_electricity'])] = (
                                                    required_electricity)
        y_net["electricity.{}.kWh".format(SP_params['analysis_params']['facility_electricity'])] = -(
                                                    SP_params['analysis_params']['electricity_credits'])
        y_cred["electricity.{}.kWh".format(SP_params['analysis_params']['facility_electricity'])] = (np.where(
                                                    (required_electricity - SP_params['analysis_params']['electricity_credits'])<=0, 
                                                    required_electricity - SP_params['analysis_params']['electricity_credits'],
                                                    0))

        electricity_kg_co2e = hf.TotalGHGEmissions(io_data, y,
                                                   0, 0, 0, 0, SP_params['analysis_params']['time_horizon'])
        results_kg_co2e_net = hf.TotalGHGEmissions(io_data, y_net, 
                                                          0, 0, 0, 0,
                                                          SP_params['analysis_params']['time_horizon'])
        results_kg_co2e_cred = hf.TotalGHGEmissions(io_data, y_cred, 
                                                          0, 0, 0, 0,
                                                          SP_params['analysis_params']['time_horizon'])


        electricity_kg_co2e_req = electricity_kg_co2e.set_index('products')['ghg_results_kg'].to_dict()
        results_kg_co2e_dict_net = results_kg_co2e_net.set_index('products')['ghg_results_kg'].to_dict()
        results_kg_co2e_dict_cred = results_kg_co2e_cred.set_index('products')['ghg_results_kg'].to_dict()

        aggregated_data_avg = m.T
        aggregated_data_avg['electricity_requirements'] = sum(electricity_kg_co2e_req.values())
        aggregated_data_avg['electricity_generated'] = sum(results_kg_co2e_dict_net.values())
        aggregated_data_avg['electricity_cred'] = sum(results_kg_co2e_dict_cred.values())

        steam_credits = -(total_steam * hf.CooledWaterCO2kg('steam_low'))
        aggregated_data_avg['steam_credits'] = steam_credits

        aggregated_data_avg_pos = aggregated_data_avg


    aggregated_data_avg_plot = aggregated_data_avg[list(reversed(aggregated_data_avg.columns.values))]

    return aggregated_data_avg_plot




