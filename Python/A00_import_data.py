import time
import pandas as pd
import openpyxl
import os
import json
import pprint

"""
This script imports data from Excel files in a specified folder and processes it to create a JSON file containing asset information, measures, and madasters.

IMPORTANT:
This script is unique for the Grip Op Kunstwerken project and is not intended for general use.
It is designed to handle specific Excel file formats and structures used in this project and convert it to a standerdized JSON format.
"""

def importKW(file_path):
    """
    importKW imports data from an Excel file and returns a dictionary of the asset.

    :param file_path: The path to the Excel file to be imported.
    :return: A dictionary of the asset.
    """

    try:
        wb = openpyxl.load_workbook(file_path, data_only=True)

    except Exception as e:
        print(f"Error importing {file_path}: {e}")
        return None

    ws = wb.worksheets[0]

    conditions = {}
    unique_colors = set()

    for row in [41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 52, 53]:
        for col in ['L', 'M']:
            cell = f"{col}{row}"
            color = ws[cell].fill.start_color.rgb
            unique_colors.add(color)
            conditions[cell] = {"color": color}
            conditions[cell]["condition"] = {
                41: "age",
                42: "constructive",
                43: "damage",
                44: "leakage",
                45: "watermanagement",
                46: "deckmounting",
                47: "joints",
                48: "abutment",
                49: "collisiondanger",
                50: "workingconditions",
                52: "railings",
                53: "foundation",
            }[row]

    # Convert to pandas DataFrame
    data = ws.values
    df = pd.DataFrame(data)

    # Rename the columns to match the index of column
    df.columns = range(len(df.columns))

    # Import properties of the asset from the Excel file
    SAP_number = df.iloc[4, 11]
    PGO_contract_area = df.iloc[5, 11]
    ID = df.iloc[6, 11]
    name = df.iloc[7, 11]
    manager = df.iloc[8, 11]
    rail_section = df.iloc[9, 11]
    geocode = df.iloc[10, 11]
    kilometrage = df.iloc[11, 11]
    RDX_RXY_coordinates = df.iloc[12, 11]
    construction_year = df.iloc[13, 11]
    renovation_year = df.iloc[14, 11]
    track_classification = df.iloc[15, 11]
    function = df.iloc[16, 11]
    length = df.iloc[22, 11]
    width = df.iloc[23, 11]
    height = df.iloc[24, 11]
    thickness = df.iloc[25, 11]

    conditions["assessment_date"] = df.iloc[39, 12]

    for row in [41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 52, 53]:
        for col in ['L', 'M']:
            cell = f"{col}{row}"
            if col == 'L':
                NA = df.iloc[row - 1, 11]
            elif col == 'M':
                NA = df.iloc[row - 1, 12]
            else:
                return ValueError(f"Unexpected column: {col}")
            if NA == "N.v.t.":
                conditions[cell]["NA"] = True
            else:
                conditions[cell]["NA"] = False

    asset = {
        "sap_number": SAP_number,
        "contract_area": PGO_contract_area,
        "ID": ID,
        "name": name,
        "manager": manager,
        "rail_section": rail_section,
        "geocode": geocode,
        "kilometrage": kilometrage,
        "coordinates": RDX_RXY_coordinates,
        "construction_year": construction_year,
        "renovation_year": renovation_year,
        "track_classification": track_classification,
        "function": function,
        "length": length,
        "width": width,
        "height": height,
        "thickness": thickness,
        "conditions": conditions
    }

    return asset, unique_colors

def importLCC(file_path):
    """
    Import data from an LCC Excel file and return a dictionary of DataFrames for each sheet.

    :param file_path: The path to the Excel file to be imported.
    :return: Dictionaries of the asset, measures, and madaster information.
    """
    try:
        df_voorblad = pd.read_excel(file_path, sheet_name="Voorblad")
        df_berekening = pd.read_excel(file_path, sheet_name="Berekening MJOP+LTP")
        
    except Exception as e:
        print(f"Error importing {file_path}: {e}")
        return None

    # Rename the columns to match the index of column
    df_voorblad.columns = range(len(df_voorblad.columns))
    df_berekening.columns = range(len(df_berekening.columns))

    # Show all rows
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)

    asset_ID = df_voorblad.iloc[17, 5]
    construction_year_superstructure = df_voorblad.iloc[22, 5]
    construction_year_substructure = df_voorblad.iloc[23, 5]


    # Superstructure and substructure
    superstructure = None
    substructure = None

    structure_types = {
        97: ("superstructure", "Steel", list(range(58, 74)) + list(range(76, 95)) + list(range(97, 99))),
        149: ("superstructure", "Concrete", list(range(109, 125)) + list(range(127, 147)) + list(range(149, 151))),
        187: ("superstructure", "Masonry", list(range(158, 172)) + list(range(174, 185)) + [187]),
        204: ("substructure", "Concrete", list(range(195, 199)) + [201, 204]),
        221: ("substructure", "Masonry", list(range(212, 216)) + [218, 221]),
    }

    measures = []

    # Loop over all structure types and extract the measures for each structure type
    for main_row, (structure, structure_type, rows) in structure_types.items():
        amount = df_berekening.iloc[main_row - 2, 16]

        # If the amount is not zero, we will process the measures for this structure type
        if amount != 0:

            # Append all possible measures for the current structure type
            for row in rows:
                i = row - 2
                measure_ID = row
                amount = df_berekening.iloc[i, 16]
                if pd.isna(amount):
                    amount = 0
                cost_category = df_berekening.iloc[i, 1]
                theme = df_berekening.iloc[i, 5]
                abreviation = df_berekening.iloc[i, 8]
                name = df_berekening.iloc[i, 10]
                method_of_calculation = df_berekening.iloc[i, 14]
                extra_info = df_berekening.iloc[i, 15]
                unit = df_berekening.iloc[i, 17]
                unit_price = df_berekening.iloc[i, 18]
                frequency = df_berekening.iloc[i, 20]
                construction_year = construction_year_superstructure if structure == "superstructure" else construction_year_substructure

                measure = {
                    "ID": measure_ID,
                    "structure_type": structure_type,
                    "construction_year": construction_year,
                    "cost_category": cost_category,
                    "theme": theme,
                    "abreviation": abreviation, # Not unique!
                    "name": name, # Not unique!
                    "method_of_calculation": method_of_calculation,
                    "extra_info": extra_info,
                    "amount": amount,
                    "unit": unit,
                    "unit_price": unit_price,
                    "frequency": frequency
                }
                measures.append(measure)


            # Assign the structure type to the asset
            if structure == "superstructure":
                superstructure = structure_type
            else:
                substructure = structure_type

    asset = {
        "ID": asset_ID,
        "superstructure": superstructure,
        "substructure": substructure,
        "construction_year_superstructure": construction_year_superstructure,
        "construction_year_substructure": construction_year_substructure
    }

    # Extract list of madasters
    madasters = []

    for row in range(229, 237):
        i = row - 2
        amount = df_berekening.iloc[i, 16]
        if not pd.isna(amount) and amount != 0:
            madaster_ID = row
            cost_category = df_berekening.iloc[i, 1]
            theme = df_berekening.iloc[i, 5]
            abreviation = df_berekening.iloc[i, 8]
            name = df_berekening.iloc[i, 10]
            method_of_calculation = df_berekening.iloc[i, 14]
            extra_info = df_berekening.iloc[i, 15]
            unit = df_berekening.iloc[i, 17]
            unit_price = df_berekening.iloc[i, 18]
            
            madaster = {
                "ID": madaster_ID,
                "cost_category": cost_category,
                "theme": theme,
                "abreviation": abreviation, # Not unique!
                "name": name, # Not unique!
                "method_of_calculation": method_of_calculation,
                "extra_info": extra_info,
                "amount": amount,
                "unit": unit,
                "unit_price": unit_price
            }
            madasters.append(madaster)

    return asset, measures, madasters

def import_all(folder_path):
    """
    Import all data from the specified folder and return unique colors, assets, measures, and asset numbers.
    """
    print(f"Importing data from folder: {folder_path}")
    start = time.time()

    assets_KW = []
    assets_LCC = []
    measures_LCC = {}
    madasters_LCC = {}

    i = 0
    j = 0
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".xlsx"):
                if file.endswith("LCC.xlsx"):
                    file_path = os.path.join(root, file)
                    print(f"Processing file: {file}")
                    i += 1
                    asset_LCC, measures, madasters = importLCC(file_path)
                    measures_LCC[asset_LCC["ID"]] = measures
                    madasters_LCC[asset_LCC["ID"]] = madasters
                    assets_LCC.append(asset_LCC)
                elif not file.endswith("zonder versiebeheer.xlsx"):
                    file_path = os.path.join(root, file)
                    if "2" in root.split(os.sep) and "Vervallen" not in root.split(os.sep):
                        print(f"Processing file: {file}")
                        j += 1
                        asset_KW, _ = importKW(file_path)
                        assets_KW.append(asset_KW)

    # Create JSONafiable objects
    assets = []
    for asset_KW in assets_KW:
        asset_ID = asset_KW["ID"]
        for asset_LCC in assets_LCC:
            if asset_LCC["ID"] == asset_ID:
                for key, value in asset_LCC.items():
                    asset_KW[key] = value
                assets.append(asset_KW)
                asset_KW["measures"] = measures_LCC[asset_ID]
                asset_KW["madasters"] = madasters_LCC[asset_ID]

    # Save the assets to a JSON file
    json.dump(assets, open("assets.json", "w"), indent=4, default=str)

    print(f"LCC files imported: {i}")
    print(f"KW files imported: {j}")
    print(f"Number of assets with complete data: {len(assets)}")
    end = time.time()
    print(f"Imported data in {end - start:.2f} seconds")

if __name__ == "__main__":

    folder_path = (
        r"C:\Users\milowullink\OneDrive - Movares\Documenten\Stageopdracht Movares\Data\Grip Op Kunstwerken Data\GOK"
    )

    import_all(folder_path)