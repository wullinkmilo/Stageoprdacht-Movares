import json

class Asset:
    def __init__(
        self,
        # Data from 'Life Cycle Costs'
        measures,
        madasters,
        construction_year_superstructure,
        construction_year_substructure,

        # Data from 'Kunstwerkpaspoort'
        ID,
        name,

        # Currently not used data
        superstructure = None,
        substructure = None,
        sap_number = None,
        contract_area = None,
        manager = None,
        rail_section = None,
        geocode = None,
        kilometrage = None,
        coordinates = None,
        construction_year = None,
        renovation_year = None,
        track_classification = None,
        function = None,
        length = None,
        width = None,
        height = None,
        thickness = None,

        # Data from risk assessment within the 'Kunstwerkpaspoort'
        conditions = None
    ):
        """
        Initialize an Asset instance.
        """

        # Data from 'Life Cycle Costs'
        self.measures = measures
        self.madasters = madasters
        self.construction_year_superstructure = construction_year_superstructure
        self.construction_year_substructure = construction_year_substructure

        # Data from 'Kunstwerkpaspoort'
        self.ID = ID
        self.name = name

        # Currently not used data
        self.superstructure = superstructure
        self.substructure = substructure
        self.SAP_number = sap_number
        self.PGO_contract_area = contract_area
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

        # Data from risk assessment within the 'Kunstwerkpaspoort'
        self.conditions = conditions

    def __str__(self):
        return str(self.ID)

    def __repr__(self):
        return str(self.ID)

class Measure:
    def __init__(self, ID, name, amount, unit_price, dependencies = None, structure_type = None, construction_year = None, cost_category = None, theme = None, abreviation = None, method_of_calculation = None, extra_info = None, unit = None, frequency = None):
        self.ID = ID
        self.name = name
        self.amount = amount
        self.unit_price = unit_price
        self.dependencies = dependencies if dependencies is not None else [ID]
        self.structure_type = structure_type
        self.year_of_last_measure_input = construction_year # MUST STILL BE ADJUSTED
        self.costs = amount * unit_price
        self.construction_year = construction_year
        self.cost_category = cost_category
        self.theme = theme
        self.abreviation = abreviation
        self.method_of_calculation = method_of_calculation
        self.extra_info = extra_info
        self.unit = unit
        self.frequency = frequency



    def __str__(self):
        return str(self.ID)

    def __repr__(self):
        return str(self.ID)

    def set_penalty_values(self, penalty, beta, theta):
        self.penalty = penalty
        self.beta = beta
        self.theta = theta

    def set_y_0(self, y_0):
        self.age = y_0 - self.construction_year
        self.tslm = y_0 - self.year_of_last_measure_input

class Madaster:
    def __init__(self, ID, name, amount, unit_price, cost_category = None, theme = None, abreviation = None, method_of_calculation = None, extra_info = None, unit = None):
        self.ID = ID
        self.name = name
        self.cost_category = cost_category
        self.theme = theme
        self.abreviation = abreviation
        self.method_of_calculation = method_of_calculation
        self.extra_info = extra_info
        self.amount = amount
        self.unit = unit
        self.unit_price = unit_price

    def __str__(self):
        return str(self.ID)

    def __repr__(self):
        return str(self.ID)

    def calculate_costs(self):
        self.costs = self.amount * self.unit_price


def load_json(json_file_path):
    with open(json_file_path, "r") as json_file:
        data = json.load(json_file)
    return data

def structure_data(assets_json_file_path, dependencies_json_file_path):

    asset_json = load_json(assets_json_file_path)
    dependencies = load_json(dependencies_json_file_path)

    # Create class instances for assets, measures, and madasters.
    assets = {}

    for asset in asset_json:
        # Add dependencies to the measure dictionary
        for measure in asset["measures"]:
            measure["dependencies"] = dependencies[str(measure["ID"])]

        # Add measures and madasters to the asset dictionary
        asset["measures"] = [
            Measure(**measure) for measure in asset["measures"]
        ]
        asset["madasters"] = [
            Madaster(**madaster) for madaster in asset["madasters"]
        ]
        asset = Asset(**asset)  # Create an Asset instance with the asset dictionary
        assets[asset.ID] = asset
    
    return assets


def check_standardization(assets):
    """
    Check if all names of the measures are the same for same IDs.
    """
    measure_name_numbers = {}
    madaster_name_numbers = {}

    for asset in assets.values():
        for madaster in asset.madasters:
            if madaster.ID not in madaster_name_numbers:
                madaster_name_numbers[madaster.ID] = set()
            madaster_name_numbers[madaster.ID].add(madaster.name)
        for measure in asset.measures:
            if measure.ID not in measure_name_numbers:
                measure_name_numbers[measure.ID] = set()
            measure_name_numbers[measure.ID].add(measure.name)

    for ID, names in madaster_name_numbers.items():
        if len(names) > 1:
            print(f"Madaster ID {ID} has different names: {names}")

    for ID, names in measure_name_numbers.items():
        if len(names) > 1:
            print(f"Measure ID {ID} has different names: {names}")


if __name__ == "__main__":

    assets_json_file_path = r"C:\\Users\\milowullink\\OneDrive - Movares\\Documenten\\Stageopdracht Movares\\assets.json"
    dependencies_json_file_path = r"C:\\Users\\milowullink\\OneDrive - Movares\\Documenten\\Stageopdracht Movares\\dependencies.json"

    assets = structure_data(assets_json_file_path, dependencies_json_file_path)

    check_standardization(assets)