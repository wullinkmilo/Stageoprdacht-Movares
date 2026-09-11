import pandas as pd
import openpyxl
from openpyxl.styles import Color
import os


def importKW(file_path):
    """
    Import data from an Excel file and return a dictionary of DataFrames for each sheet.
    """
    try:
        wb = openpyxl.load_workbook(file_path, data_only=True)

    except Exception as e:
        print(f"Error importing {file_path}: {e}")
        return None

    ws = wb.worksheets[0]

    colorL41 = ws['L41'].fill.start_color.rgb
    colorL42 = ws['L42'].fill.start_color.rgb
    colorL43 = ws['L43'].fill.start_color.rgb
    colorL44 = ws['L44'].fill.start_color.rgb
    colorL45 = ws['L45'].fill.start_color.rgb
    colorL46 = ws['L46'].fill.start_color.rgb
    colorL47 = ws['L47'].fill.start_color.rgb
    colorL48 = ws['L48'].fill.start_color.rgb
    colorL49 = ws['L49'].fill.start_color.rgb
    colorL50 = ws['L50'].fill.start_color.rgb
    colorL52 = ws['L52'].fill.start_color.rgb
    colorL53 = ws['L53'].fill.start_color.rgb
    colorM41 = ws['M41'].fill.start_color.rgb
    colorM42 = ws['M42'].fill.start_color.rgb
    colorM43 = ws['M43'].fill.start_color.rgb
    colorM44 = ws['M44'].fill.start_color.rgb
    colorM45 = ws['M45'].fill.start_color.rgb
    colorM46 = ws['M46'].fill.start_color.rgb
    colorM47 = ws['M47'].fill.start_color.rgb
    colorM48 = ws['M48'].fill.start_color.rgb
    colorM49 = ws['M49'].fill.start_color.rgb
    colorM50 = ws['M50'].fill.start_color.rgb
    colorM52 = ws['M52'].fill.start_color.rgb
    colorM53 = ws['M53'].fill.start_color.rgb

    unique_colors = set()
    unique_colors.add(colorL41)
    unique_colors.add(colorL42)
    unique_colors.add(colorL43)
    unique_colors.add(colorL44)
    unique_colors.add(colorL45)
    unique_colors.add(colorL46)
    unique_colors.add(colorL47)
    unique_colors.add(colorL48)
    unique_colors.add(colorL49)
    unique_colors.add(colorL50)
    unique_colors.add(colorL52)
    unique_colors.add(colorL53)
    unique_colors.add(colorM41)
    unique_colors.add(colorM42)
    unique_colors.add(colorM43)
    unique_colors.add(colorM44)
    unique_colors.add(colorM45)
    unique_colors.add(colorM46)
    unique_colors.add(colorM47)
    unique_colors.add(colorM48)
    unique_colors.add(colorM49)
    unique_colors.add(colorM50)
    unique_colors.add(colorM52)
    unique_colors.add(colorM53)

    print(f"Unique colors in {file_path}: {unique_colors}")

    # Convert to pandas DataFrame
    data = ws.values
    df = pd.DataFrame(data)

    # Rename the columns to match the index of column
    df.columns = range(len(df.columns))

    # # Print full dataframe
    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.max_columns', None)
    # print(df)

    # Import properties of the asset from the Excel file
    SAP_number = df.iloc[4, 11]
    PGO_contract_area = df.iloc[5, 11]
    asset_number = df.iloc[6, 11]
    asset_name = df.iloc[7, 11]
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

    risk_assessment_date = df.iloc[39, 12]

    NA_cd_age = df.iloc[40, 12]
    NA_cd_constructive = df.iloc[41, 12]
    NA_cd_damage = df.iloc[42, 12]
    NA_cd_leakage = df.iloc[43, 12]
    NA_cd_watermanagement = df.iloc[44, 12]
    NA_cd_deckmounting = df.iloc[45, 12]
    NA_cd_joints = df.iloc[46, 12]
    NA_cd_abutment = df.iloc[47, 12]
    NA_cd_collisiondanger = df.iloc[48, 12]
    NA_cd_workingconditions = df.iloc[49, 12]
    NA_cd_railings = df.iloc[51, 12]
    NA_cd_foundation = df.iloc[52, 12]


    asset = Asset(
        # Properties of the asset
        sap_number=SAP_number,
        contract_area=PGO_contract_area,
        asset_number=asset_number,
        asset_name=asset_name,
        manager=manager,
        rail_section=rail_section,
        geocode=geocode,
        kilometrage=kilometrage,
        coordinates=RDX_RXY_coordinates,
        construction_year=construction_year,
        renovation_year=renovation_year,
        track_classification=track_classification,
        function=function,
        length=length,
        width=width,
        height=height,
        thickness=thickness,

        # Conditions of certain aspects of the asset
        risk_assessment_date = risk_assessment_date,
        cd_age = colorM41,
        cd_constructive = colorM42,
        cd_damage = colorM43,
        cd_leakage = colorM44,
        cd_watermanagement = colorM45,
        cd_deckmounting = colorM46,
        cd_joints = colorM47,
        cd_abutment = colorM48,
        cd_collisiondanger = colorM49,
        cd_workingconditions = colorM50,
        cd_railings = colorM52,
        cd_foundation = colorM53,

        # N/A values for certain aspects of the asset
        NA_cd_age = NA_cd_age,
        NA_cd_constructive = NA_cd_constructive,
        NA_cd_damage = NA_cd_damage,
        NA_cd_leakage = NA_cd_leakage,
        NA_cd_watermanagement = NA_cd_watermanagement,
        NA_cd_deckmounting = NA_cd_deckmounting,
        NA_cd_joints = NA_cd_joints,
        NA_cd_abutment = NA_cd_abutment,
        NA_cd_collisiondanger = NA_cd_collisiondanger,
        NA_cd_workingconditions = NA_cd_workingconditions,
        NA_cd_railings = NA_cd_railings,
        NA_cd_foundation = NA_cd_foundation
    )

    return unique_colors, asset

def importKWs(folder_path):
    """
    Import data from multiple Excel files in a folder and return a list of Asset instances.
    """
    # Structure is as follows: 

    # This contains folders, in which a folder named "2" contains the Excel file. The folder name is the asset number, which is also in the Excel file.

    # Import all Excel files in the folder and its subfolders
    assets = {}
    unique_colors_all = set()
    i = 0
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".xlsx") and not file.endswith("LCC.xlsx") and not file.endswith("zonder versiebeheer.xlsx"):
                file_path = os.path.join(root, file)
                if "2" in root.split(os.sep) and "Vervallen" not in root.split(os.sep):
                    i += 1
                    unique_colors, asset = importKW(file_path)
                    unique_colors_all.update(unique_colors)
                    assets[asset.asset_number] = asset

    print(f"Assets considered: {i}")
    return unique_colors_all, assets

class Asset:
    def __init__(
        self,
        sap_number,
        contract_area,
        asset_number,
        asset_name,
        manager,
        rail_section,
        geocode,
        kilometrage,
        coordinates,
        construction_year,
        renovation_year,
        track_classification,
        function,
        length,
        width,
        height,
        thickness,
        risk_assessment_date,
        cd_age,
        cd_constructive,
        cd_damage,
        cd_leakage,
        cd_watermanagement,
        cd_deckmounting,
        cd_joints,
        cd_abutment,
        cd_collisiondanger,
        cd_workingconditions,
        cd_railings,
        cd_foundation,
        NA_cd_age,
        NA_cd_constructive,
        NA_cd_damage,
        NA_cd_leakage,
        NA_cd_watermanagement,
        NA_cd_deckmounting,
        NA_cd_joints,
        NA_cd_abutment,
        NA_cd_collisiondanger,
        NA_cd_workingconditions,
        NA_cd_railings,
        NA_cd_foundation
    ):
        """
        Initialize an Asset instance.
        """
        self.SAP_number = sap_number
        self.PGO_contract_area = contract_area
        self.asset_number = asset_number
        self.asset_name = asset_name
        self.manager = manager
        self.rail_section = rail_section
        self.geocode = geocode
        self.kilometrage = kilometrage
        self.RDX_RXY_coordinates = coordinates
        self.construction_year = construction_year
        self.renovation_year = renovation_year
        self.track_classification = track_classification
        self.function = function
        self.length = length
        self.width = width
        self.height = height
        self.thickness = thickness
        self.risk_assessment_date = risk_assessment_date
        self.cd_age = cd_age
        self.cd_constructive = cd_constructive
        self.cd_damage = cd_damage
        self.cd_leakage = cd_leakage
        self.cd_watermanagement = cd_watermanagement
        self.cd_deckmounting = cd_deckmounting
        self.cd_joints = cd_joints
        self.cd_abutment = cd_abutment
        self.cd_collisiondanger = cd_collisiondanger
        self.cd_workingconditions = cd_workingconditions
        self.cd_railings = cd_railings
        self.cd_foundation = cd_foundation
        self.NA_cd_age = NA_cd_age
        self.NA_cd_constructive = NA_cd_constructive
        self.NA_cd_damage = NA_cd_damage
        self.NA_cd_leakage = NA_cd_leakage
        self.NA_cd_watermanagement = NA_cd_watermanagement
        self.NA_cd_deckmounting = NA_cd_deckmounting
        self.NA_cd_joints = NA_cd_joints
        self.NA_cd_abutment = NA_cd_abutment
        self.NA_cd_collisiondanger = NA_cd_collisiondanger
        self.NA_cd_workingconditions = NA_cd_workingconditions
        self.NA_cd_railings = NA_cd_railings
        self.NA_cd_foundation = NA_cd_foundation


if __name__ == "__main__":

    folder_path = (
        r"C:\Users\milowullink\OneDrive - Movares\Documenten\Stageopdracht Movares\Data\Grip Op Kunstwerken Data\GOK"
    )

    unique_colors, assets = importKWs(folder_path)
    print(f"All unique colors in the folder: {unique_colors}")
    print(f"Total number of assets imported: {len(assets)}")

    count = 0
    for asset in assets.values():
        if asset.NA_cd_age == "N.v.t.":
            count += 1
        if asset.NA_cd_constructive == "N.v.t.":
            count += 1
        if asset.NA_cd_damage == "N.v.t.":
            count += 1
        if asset.NA_cd_leakage == "N.v.t.":
            count += 1
        if asset.NA_cd_watermanagement == "N.v.t.":
            count += 1
        if asset.NA_cd_deckmounting == "N.v.t.":
            count += 1
        if asset.NA_cd_joints == "N.v.t.":
            count += 1
        if asset.NA_cd_abutment == "N.v.t.":
            count += 1
        if asset.NA_cd_collisiondanger == "N.v.t.":
            count += 1
        if asset.NA_cd_workingconditions == "N.v.t.":
            count += 1
        if asset.NA_cd_railings == "N.v.t.":
            count += 1
        if asset.NA_cd_foundation == "N.v.t.":
            count += 1
    print(f"Total number of N.v.t. values in the assets: {count}")
