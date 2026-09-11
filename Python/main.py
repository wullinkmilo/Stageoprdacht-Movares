import pandas as pd

class Asset:
    def __init__(
        self,
        sap_number,
        contract_area,
        asset_number,
        asset_name,
        water_manager,
        rail_section,
        geocode,
        kilometrage,
        coordinates,
        construction_year,
        renovation,
        track_classification,
        function,
        length,
        width,
        height,
        thickness,
        no_of_overhead_lines
    ):
        """
        Initialize an Asset instance.
        """
        self.SAP_number = sap_number
        self.PGO_contract_area = contract_area
        self.asset_number = asset_number
        self.asset_name = asset_name
        self.water_manager = water_manager
        self.rail_section = rail_section
        self.geocode = geocode
        self.kilometrage = kilometrage
        self.RDX_Y_coordinates = coordinates
        self.construction_year = construction_year
        self.renovation = renovation
        self.track_classification = track_classification
        self.function = function
        self.length = length
        self.width = width
        self.height = height
        self.thickness = thickness
        self.no_of_overhead_lines = no_of_overhead_lines


if __name__ == "__main__":

    excel_path = (
        r"C:\Users\milowullink\OneDrive - Movares\Documenten\Stageopdracht Movares\Data\Grip Op Kunstwerken Data\GOK\KW20-121-0001-Breda, Odg Westtangent 1-S\2\D90-MGE-KA-1701407.xlsx"
    )

    sheets = pd.read_excel(excel_path, sheet_name=None)
    print(f"Imported {excel_path}")
    print("Available sheets:", ", ".join(sheets))
    