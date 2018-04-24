import json
import numpy as np
from Final_Impact_Model import FinalImpactModel

class ParameterValues():
    def __init__(self, parameters, risk_params):
        self.parameters = parameters
        self.risk_params = risk_params
        self.new_params = {}
        
    def uncertainty(self, catalysts, fuel, ionic_liquid, hhv_jet_fuel):
        for section, section_values in self.parameters.iteritems():
            new_value = 0
            if section not in self.new_params.keys():
                self.new_params.update({section:{}})
            if type(section_values) == float:
                new_value = self.parameters[section]
                self.new_params[section] = new_value
            if section == 'credits':
                self.new_params[section] = self.parameters[section]
            else:
                for item, item_value in section_values.iteritems():
                    if isinstance(item_value, basestring):
                        self.new_params[section].update({item:item_value})
                        continue
                    if item not in self.new_params[section].keys():
                        self.new_params[section].update({item:{}})
                    if item not in self.risk_params[section].keys():
                        if item == 'feedstock.kg':
                            new = 0
                            for feed in ['AcetateSOR', 'AshSOR', 'CelluloseSOR', 'ExtractiveSOR', 'HemicelluloseSO', 'LigninSOR', 'ProteinsSOR']:
                                new += np.random.triangular(self.risk_params[section][feed]['Minimum'], self.risk_params[section][feed]['Baseline'], self.risk_params[section][feed]['Maximum'])
                            new_value = new
                            self.new_params[section][item] = new_value
                        else:
                            new_value = self.parameters[section][item]
                            self.new_params[section][item] = new_value
                    else:
                        new_value = np.random.triangular(self.risk_params[section][item]['Minimum'], self.risk_params[section][item]['Baseline'], self.risk_params[section][item]['Maximum'])
                        self.new_params[section][item] = new_value

        impact = FinalImpactModel(self.new_params, 'sorghum', 'buttonGHG', 'jet_fuel', catalysts, fuel, ionic_liquid, credits=False)*1000/hhv_jet_fuel
        impact_drop = impact.drop(['electricity_requirements', 'electricity_cred'], axis=1)
        impact_drop['Total_gCO2_MJ_net'] = impact_drop.sum(axis=1)['All']
        return impact_drop

    def sensitivity(self, catalysts, fuel, ionic_liquid, hhv_jet_fuel):
        results = {}
        update_params = self.parameters.copy()
        for section, section_values in self.parameters.iteritems():
            if section == 'credits':
                continue
            results.update({section:{}})
            if type(section_values) == float:
                results[section] = section_values
                continue
            for item, item_value in section_values.iteritems():
                if (item == 'water_direct_withdrawal'):
                    continue
                results[section].update({item:{}})
                if isinstance(item_value, basestring):
                    continue

                value_avg = update_params[section][item]

                if item not in self.risk_params[section].keys():
                    if item == 'feedstock.kg':
                        new_min = 0
                        new_max = 0
                        for feed in ['AcetateSOR', 'AshSOR', 'CelluloseSOR', 'ExtractiveSOR', 'HemicelluloseSO', 'LigninSOR', 'ProteinsSOR']:
                            new_min += self.risk_params[section][feed]['Minimum']
                            new_max += self.risk_params[section][feed]['Maximum']
                        value_low = new_min
                        value_high = new_max

                    else:
                        continue

                else:
                    value_low = self.risk_params[section][item]['Minimum']
                    value_high = self.risk_params[section][item]['Maximum']

                update_params[section][item] = value_avg
                impact = FinalImpactModel(update_params, 'sorghum', 'buttonGHG', 'jet_fuel', catalysts, fuel, ionic_liquid, credits=False)*1000/hhv_jet_fuel
                impact_drop = impact.drop(['electricity_requirements', 'electricity_cred'], axis=1)
                sum_impact = impact_drop.sum(axis=1)['All']
                results[section][item].update({'avg':sum_impact})

                update_params[section][item] = value_low
                impact = FinalImpactModel(update_params, 'sorghum', 'buttonGHG', 'jet_fuel', catalysts, fuel, ionic_liquid, credits=False)*1000/hhv_jet_fuel
                impact_drop = impact.drop(['electricity_requirements', 'electricity_cred'], axis=1)
                sum_impact = impact_drop.sum(axis=1)['All']
                results[section][item].update({'low':sum_impact})

                update_params[section][item] = value_high
                impact = FinalImpactModel(update_params, 'sorghum', 'buttonGHG', 'jet_fuel', catalysts, fuel, ionic_liquid, credits=False)*1000/hhv_jet_fuel
                impact_drop = impact.drop(['electricity_requirements', 'electricity_cred'], axis=1)
                sum_impact = impact_drop.sum(axis=1)['All']
                results[section][item].update({'high':sum_impact})

                results[section][item].update({'minimum_value':value_low})
                results[section][item].update({'maximum_value':value_high})

                update_params[section][item] = value_avg

        
        return results
