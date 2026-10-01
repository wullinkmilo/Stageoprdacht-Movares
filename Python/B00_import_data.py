import json

if __name__ == "__main__":
    assets = [
                {
                    "name": "Bridge 1",
                    "ID": "B1",
                    "construction_year_superstructure": 2000,
                    "construction_year_substructure": 2005,
                    "measures": [
                        {
                            "name": "Measure 1",
                            "ID": "M1",
                            "amount": 100,
                            "unit_price": 885,
                            "construction_year": 2000,
                            "dependencies": ["M2", "M3"]
                        },
                        {
                            "name": "Measure 2",
                            "ID": "M2",
                            "amount": 50,
                            "unit_price": 1600,
                            "construction_year": 2000
                        },
                        {
                            "name": "Measure 3",
                            "ID": "M3",
                            "amount": 50,
                            "unit_price": 12000,
                            "construction_year": 2000
                        }
                    ],
                    "madasters": [
                        {
                            "name": "Madaster 1",
                            "ID": "MD1",
                            "amount": 100,
                            "unit_price": 885
                        },
                        {
                            "name": "Madaster 2",
                            "ID": "MD2",
                            "amount": 50,
                            "unit_price": 1600
                        }
                    ]
                },
                {
                    "name": "Bridge 2",
                    "ID": "B2",
                    "construction_year_superstructure": 2025,
                    "construction_year_substructure": 2025,
                    "measures": [
                        {
                            "name": "Measure 1",
                            "ID": "M1",
                            "amount": 25,
                            "unit_price": 885,
                            "construction_year": 2025
                        },
                        {
                            "name": "Measure 2",
                            "ID": "M2",
                            "amount": 25,
                            "unit_price": 1600,
                            "construction_year": 2025
                        }
                    ],
                    "madasters": [
                        {
                            "name": "Madaster 1",
                            "ID": "MD1",
                            "amount": 25,
                            "unit_price": 885
                        },
                        {
                            "name": "Madaster 2",
                            "ID": "MD2",
                            "amount": 25,
                            "unit_price": 1600
                        }
                    ]
                }
            ]

    # Save the assets to a JSON file
    json.dump(assets, open("dummy_assets.json", "w"), indent=4, default=str)