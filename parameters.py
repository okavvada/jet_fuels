# removed process.water.m3 and included data in impact water vectors
# farmedstover flatbedtruck set to 0 in io_table and instead calculated as parameter in model
io_table_physicalunits_path = "io_tables/io_table_physicalunits.csv"
selectivity = ["iHG-Current","iHG-Projected", "waterwash"]
# Three ranges for sensitivity:  (a) low; (b) avg; and (c) high  
scenario_range = ["low", "avg", 'high']
processes = ["electricity_credit", "Farming", "Transportation", "Petroleum", "Electricity", "Chemicals_And_Fertilizers", "Direct", "Other"]
sections = ["Feedstock_Supply_Logistics", "Feedstock_Handling_and_Preparation", "IL_Pretreatment",
			"Enzymatic_Hydrolysis_and_Fermentation", "Recovery_and_Separation", "Hydrogeneration_and_Oligomerization",
			"Wastewater_Treatment", "Lignin_Utilization", "Direct_Water"]
energy_content_path = "unit_conversions_and_mw/energy_content_by_mass_and_volume.csv"
fuel_aliases_path = "unit_conversions_and_mw/fuel_aliases.csv"
co2_filepath = "io_tables/impact_vectors/co2_impact.csv"
ch4_filepath = "io_tables/impact_vectors/ch4_impact.csv"
n2o_filepath = "io_tables/impact_vectors/n2o_impact.csv"

#updated impact vectors with process.water.m3 from original io_tables/input_output_table_working.xls
water_consumption_path = "io_tables/impact_vectors_water/water_consumption.csv"
water_withdrawal_path = "io_tables/impact_vectors_water/water_withdrawal.csv"
