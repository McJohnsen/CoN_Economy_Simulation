import csv


# Until which day we should be calculating
# Time measurement: Time is in days and days since game started.
end_of_time = 15

# Which in game time the game starts, in day format. 0.5 for 12:00, between 0 and 1
start_time = 0
if start_time == 0:
    day_change = 0
else:
    day_change = 1 - start_time

# Days it takes for population to go from one lvl to another. In slot 0, time in days to go from Lv1 to Lv2.
population_grow_duration = []

# Taken from buildings.csv, contains all relevant stats to buildings
building_stats = []

def start_production(resource: str):
    """
    To be used at initiation when players select the type of resource for their cities
    :param resource: type of resource
    :return: base production rate / day
    """
    switch = {
        "Supplies": 2100,
        "Components": 1800,
        "Fuel": 2100,
        "Electronics": 1500,
        "Rare Materials": 1200
    }
    return switch.get(resource)


def open_files():

    # Population
    file_name = "./data/population_growth.csv"
    with open(file_name, newline='') as f:
        reader = csv.reader(f)
        data = next(reader)
        for value in data:
            population_grow_duration.append(int(value))

    # building.csv
    file_name = "./data/population_growth.csv"
    with open(file_name, newline='') as f:
        pass  # TODO: implement
