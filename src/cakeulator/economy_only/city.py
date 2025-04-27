import numpy as np
import pandas as pd
import math
from cakeulator.utilities.calculations import *


class City:
    def __init__(self, start_buildings: list, ressource: str, base_production: float, data_table: pd.DataFrame, pop_data: list, start_morale=70.0, start_population=5.0, is_homeland=True, day_of_ownership=0, calculate_till_day=30):
        self.start_buildings = start_buildings
        self.ressource = ressource
        self.base_production = base_production
        self.start_morale = start_morale
        self.start_population = start_population
        self.is_homeland = True
        self.data_table = data_table
        self.calculate_till_day = calculate_till_day
        self.pop_data = [number / 25 for number in pop_data]  # input arg is how many days each pop level needs
        # list of lists. [[start of production queue in game days, example: 1.5 for day1 12hrs: float,
        # [building abbreviation 1: str, building abbreviation 2, ...]], next construction queue at a later time]
        # List must always be ordered.
        self.construction_queue = []

        self.morale_list = [start_morale] * (calculate_till_day + 1)
        # List of morale on every day since the existence of this city

        self.day_of_ownership = day_of_ownership  # If owning from game start,
        # set this to the ingame clock at game start.

        if is_homeland:
            self.morale_targets = np.array([90.] * (calculate_till_day + 1))
        else:
            self.morale_targets = np.array([75.] * (calculate_till_day + 1))

        # list of modifiers that affect production: buildings, population, morale. Building is additive,
        # population and morale are set anew each time. List entries are (time, type, value)
        # buildings: 0, morale: 1, population: 2.
        # Value is how much they affect production.
        self.production_modifier_list = []
        # List of modifiers (from hospital and morale changes) that affect population growth.
        # List entries are (time, type, value). Buildings:0, morale:1 Buildings are additive
        # First entry is initial modifiers. Add a 2nd entries if hospitals exist already.
        self.population_modifier_list = [[self.day_of_ownership, 1, morale_influence(self.start_morale)]]

        # List of tuples. Each tuple is (time, new daily production rate)
        print(start_morale)
        print(morale_influence(start_morale))
        print(pop_modifier_on_production(start_population))
        self.total_production = [(day_of_ownership, 0)]
        self.population_list = []

        # TODO: Check starting buildings
        self.start_prod_factor_from_buildings = 1
        for building in start_buildings:
            build_info = self.data_table.loc[building]
            building_morale_bonus = build_info['effect on morale']
            building_production_bonus = build_info['effect on production']
            building_population_bonus = build_info['effect on population']
            if building_morale_bonus > 0:
                self.morale_targets += building_morale_bonus
            if building_production_bonus > 0:
                self.start_prod_factor_from_buildings += building_production_bonus
        self.start_production = base_production * morale_influence_on_production(start_morale) * pop_modifier_on_production(start_population) * self.start_prod_factor_from_buildings
        self.production_list = [(day_of_ownership, self.start_production)]

    def set_start_buildings(self, start_buildings: list):
        self.start_buildings = start_buildings
        # redo calculations if specific new buildings exist now

    def set_ressource(self, ressource:str):
        self.ressource = ressource

    def set_start_morale(self, start_morale: float):
        self.start_morale = start_morale
        # Redo full calculations

    def set_start_production(self, start_production: float):
        self.base_production = start_production
        # Redo production calculation

    def set_start_population(self, start_population: float):
        self.start_population = start_population
        # Redo pop calculation

    def add_building_to_construction(self, building: str, time: float, priority: int = 99):
        """
        Adds building to a construction queue or opens a new one if one doesn't exist in this time slot.

        :param building:
        :param time: in days
        :param priority: Each construction queue follows an order, priority=0 is first, =1 is second
        :return:
        """
        for construction_queue in self.construction_queue:
            for existing_building in construction_queue[1]:
                if building == existing_building:
                    return
        for construction_queue in self.construction_queue:
            if construction_queue[0] == time:
                if priority >= len(construction_queue[1]):
                    construction_queue[1].append(building)
                    return
                else:
                    construction_queue[1].insert(priority, building)
                    return
        self.construction_queue.append([time, [building]])
        self.construction_queue.sort(key=lambda inner_list: inner_list[0])
        return

    def remove_building_from_construction(self, building: str):
        pass

    def calculate_population(self):
        pop_level = self.start_population
        time = self.day_of_ownership
        building_modifier = 1
        morale_modifier = morale_influence(self.start_morale)
        for idx in range(len(self.population_modifier_list)):
            if idx+1 == len(self.population_modifier_list):
                time_break = self.calculate_till_day
            else:
                time_break = self.population_modifier_list[idx+1][0]  # calculate pop until next modifier
            if self.population_modifier_list[idx][1] == 0:
                building_modifier += self.population_modifier_list[idx][2]
            else:
                morale_modifier = self.population_modifier_list[idx][2]
            growth_speed = building_modifier * morale_modifier
            while time < time_break:
                diff_to_next_pop_level = (math.ceil(pop_level * 25) - pop_level * 25)
                if diff_to_next_pop_level == 0:
                    diff_to_next_pop_level = 1
                time_to_next_pop_lvl = self.pop_data[int(pop_level)-1] * diff_to_next_pop_level / growth_speed
                # If the next event (pop growth modifier) comes before this pop step can fully grow,
                # then only grow how much we can grow in this time period
                if time_to_next_pop_lvl+time >= time_break:
                    ratio = (time_break - time) / time_to_next_pop_lvl
                    pop_level += diff_to_next_pop_level * ratio / 25
                    time = time_break
                else:
                    pop_level += diff_to_next_pop_level / 25
                    time += time_to_next_pop_lvl
                    self.production_modifier_list.append([time, 2, pop_modifier_on_production(pop_level)])
                    self.population_list.append((time, pop_level))

        # Do production afterward
        pass

    def calculate_morale_and_buildings(self, start_time: float):
        # TODO: cut all relevant lists later than start_time
        time = start_time
        index = -1
        for idx, build_queue in enumerate(self.construction_queue):
            if build_queue[0] >= time:
                index = idx
                break
        done_constructing = False
        if index == -1:
            done_constructing = True
        while time <= self.calculate_till_day:
            # Check if buildings need to be constructed today
            if not done_constructing:
                if self.construction_queue[index][0] <= math.ceil(time):
                    time = self.construction_queue[index][0]
                    # Go through every building in the construction queue
                    for building in self.construction_queue[index][1]:
                        build_info = self.data_table.loc[building]
                        build_hp = build_info['HP']
                        building_morale_bonus = build_info['effect on morale'] / build_hp
                        building_production_bonus = build_info['effect on production'] / build_hp
                        building_population_bonus = build_info['effect on population'] / build_hp
                        # convert to days, build time for each step
                        original_build_time = build_time = (build_info['construction_time'] / build_hp)/24
                        # TODO: Get all other relevant infos: manpower, static money production
                        # build the building till all hp is built
                        while build_hp > 0:
                            morale = self.morale_list[math.floor(time-1)]
                            build_time = build_time / morale_influence(morale)
                            fake_time = time  # fake time is used in case the time is right on day change.
                            if fake_time == int(fake_time):
                                fake_time += 0.00001
                            if build_time <= math.ceil(fake_time) - fake_time:
                                # move the time to end of construction
                                time += build_time
                                # TODO: put this into lists
                                if building_morale_bonus > 0:
                                    self.morale_targets[math.ceil(time):] += building_morale_bonus
                                if building_production_bonus > 0:
                                    self.production_modifier_list.append([time, 0, building_production_bonus])
                                if building_population_bonus > 0:
                                    self.population_modifier_list.append([time, 0, building_population_bonus])
                                build_hp -= 1
                                # next building step:
                                build_time = original_build_time
                            else:  # build this overnight
                                remaining_build_time = build_time - (math.ceil(time) - time)
                                # take out morale influence from build time, next day will add new morale modifier
                                build_time = remaining_build_time * morale_influence(morale)
                                if time == int(time):
                                    time += 0.1
                                time = math.ceil(time)
                                self.morale_list[time] = morale_change(self.morale_list[time - 1], self.morale_targets[time])
                                if self.morale_list[time - 1] < 90:
                                    self.production_modifier_list.append([time, 1, morale_influence_on_production(self.morale_list[time])])
                                    self.population_modifier_list.append([time, 1, morale_influence(self.morale_list[time])])
                        # TODO: add building finished


                    index += 1
                    if index == len(self.construction_queue):
                        done_constructing = True
            if not done_constructing:
                if self.construction_queue[index][0] <= math.ceil(time):
                    continue  # do not move time to next day, proceed with next construction queue
            if time == int(time):
                time += 0.1
            time = math.ceil(time)
            if time >= len(self.morale_list):
                break
            self.morale_list[time] = morale_change(self.morale_list[time - 1], self.morale_targets[time])
            if self.morale_list[time - 1] < 90:
                self.production_modifier_list.append([time, 1, morale_influence_on_production(self.morale_list[time])])
                self.population_modifier_list.append([time, 1, morale_influence(self.morale_list[time])])
        # Do population afterward
        pass

    def calculation_production(self):
        self.production_modifier_list.sort(key=lambda inner_list: inner_list[0])
        if self.production_modifier_list[-1][0] < self.calculate_till_day:
            self.production_modifier_list.append([self.calculate_till_day, 3, 0])
        old_time = self.day_of_ownership
        total_production = 0
        building_modifier = self.start_prod_factor_from_buildings
        population_modifier = pop_modifier_on_production(self.start_population)
        morale_modifier = morale_influence_on_production(self.start_morale)
        base_production = self.base_production
        old_production = self.start_production
        for idx in range(len(self.production_modifier_list)):
            time = self.production_modifier_list[idx][0]  # calculate pop until next modifier
            if self.production_modifier_list[idx][1] == 0:
                building_modifier += self.production_modifier_list[idx][2]
            elif self.production_modifier_list[idx][1] == 1:
                morale_modifier = self.production_modifier_list[idx][2]
            elif self.production_modifier_list[idx][1] == 2:
                population_modifier = self.production_modifier_list[idx][2]
            production = base_production * building_modifier * morale_modifier * population_modifier
            self.production_list.append((time, production))
            total_production += (time - old_time) * old_production
            self.total_production.append((time, total_production))
            old_production = production
            old_time = time
