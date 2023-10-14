import math

import calculations
import initiation


def production_rate(base_production, pop_modifier, morale_modifier, building_modifier, state_modifier):
    """
    Returns the production rate by multiplying its modifiers. All modifiers in 1.x format.
    :param state_modifier:
    :param base_production:
    :param pop_modifier:
    :param morale_modifier:
    :param building_modifier:
    :return:
    """
    daily_production_rate = base_production * pop_modifier * morale_modifier * building_modifier * state_modifier
    return daily_production_rate


def get_next_pop_level(level):
    """
    Takes current population level and calculates the next population level,
    population levels go from 1 to 10 and are in 0.04 increments. Example: 5.01 -> 5.04
    :param level:
    :return:
    """
    pop_level = math.trunc(level)
    level -= pop_level
    if level == 0:
        level = 0.04
    else:
        level *= 25
        level = math.ceil(level)
        level /= 25
    level += pop_level
    return level


class Nations:

    def __init__(self):
        self.name = None
        # tracks on which days which national modifiers there are, by default needs to be zeros
        # TODO: When adding further calculation days, this list has to become longer
        self.morale_mod = [90] * math.trunc(initiation.end_of_time)


class City:

    def __init__(self):

        self.nation = None
        # how high the production rate is at each point
        self.production_rate = []

        # How many days after game start the city is conquered, 0 for having it from game start.
        self.ownership_time = 0
        self.day_of_ownership = math.trunc(self.ownership_time + initiation.start_time)
        # Moral modifier of the city at start of city control
        self.start_morale_mod = 0
        # starting modifier of the city from buildings to resource production
        self.start_build = 1

        # POPULATION
        # starting population modifier for resource production
        self.start_pop_mod = 1
        # starting population level of this city at time of ownership
        self.start_population = None
        # all population growth modifiers in this city coming from buildings.
        # [[time, "building", amount of growth % added from buildings (hospitals)]]
        self.population_growth_modifiers = []
        # If there are any existing hospitals, factor * to growth speed. Default 1, to increase: 1.x
        self.population_growth_modifiers_start = 1

        self.population_graph = []

        self.base_prod = None
        # 1 = core city, 0.5 = annexed, occupied = 0.25
        self.state = 1

        # MORALE
        # starting morale of this city!
        self.start_morale = 70
        # All building-steps that have an effect on morale, [effect amount] Time is implicit, 1st slot = 1st day
        # Already summed in buildings methods to only have 1 entry per day
        # TODO: Don't forget to sort this list or keep it sorted and keep it updated, warning of redundancy!
        self.morale_buildings = [0] * math.trunc(initiation.end_of_time)
        # Sums all the daily modifiers for morale for a city together. TODO: Needs to include default (90/100/..)
        self.morale_daily_mods = [0] * math.trunc(initiation.end_of_time)
        # The value of morale the city has each day
        # List full of zeros by default, if city is conquered later, list stays 0 until day of conquest
        self.morale_daily_values = [0] * math.trunc(initiation.end_of_time)
        self.morale_daily_values_mods = [0] * math.trunc(
            initiation.end_of_time)  # function to convert value to modifier applied
        # The target morale a city has each day
        self.morale_targets = [0] * math.trunc(initiation.end_of_time)
        # the effect morale has on each day on construction / pop growth / unit production, array[0] = 1st day of ownership!
        # [[time, "morale", modifier],...]
        self.morale_construction_mods = []

        # List of events affecting production rate of this city. TODO: Don't forget to add end_of_time event
        # [[time in days starting from 0, type of event, the new modifier]]
        self.events = []

        # amount produced at each time point
        # [[time in days starting from 0, production rate]]
        self.production_points = [[self.ownership_time, 0]]

        # CONSTRUCTION
        # [[start build time, end build time]] to track when the city is busy to check when we can build stuff.
        # TODO: Sort it after removing buildings
        self.busy_building = []
        # [[buildings_id, time of completion],...] to track all completed builduings, used later to check unit production requirement
        self.buildings = []

    def get_pop_level(self, time):
        """
        :param time:
        :return: pop level of the city at a given time
        """
        for i in range(len(self.population_graph)):
            if time > self.population_graph[i][0]:
                continue
            else:
                if i == 0:
                    return self.start_population
                else:
                    return self.population_graph[i - 1][1]
        return

    def get_build_mod(self, time):
        """

        :param time:
        :return: buildings modifier at given time
        """
        return 1

    def get_morale_mod(self, time):
        """
        Takes a time and returns the morale modifier on resource production
        :param time:
        :return:
        """
        day = math.trunc(time + initiation.start_time)
        morale_mod = self.morale_daily_values_mods[day]
        return morale_mod

    def get_state_mod(self, time):
        return 1

    def calculate_production(self):
        """
        When modifying events_list, the production_points list has to be cut down to the point of change.
        :return:
        """
        # sorting events
        self.events = sorted(self.events, key=lambda x: x[0], reverse=False)

        # If production_points is empty (only [0,0] the start points exists),
        # then we use the start modifiers of the city.
        if len(self.production_points) == 1:
            last_time = 0
            self.production_points.append(
                [self.events[0][0],
                 production_rate(self.base_prod, self.start_pop_mod, self.start_morale_mod, self.start_build,
                                 self.state)
                 * self.events[0][0]])
            self.production_rate.append([self.events[0][0],
                                         production_rate(self.base_prod, self.start_pop_mod, self.start_morale_mod,
                                                         self.start_build, self.state)])
        # Since we may start in the middle of the production_points list, we have to get all modifiers at that time to
        # calculate future production modifiers.
        else:
            self.production_rate = self.production_rate[0:len(self.production_points):1]
            last_time = self.events[len(self.production_points) - 1][0]
        # pop_mod = calculations.morale_to_construction(calculations.pop_modifier_on_production(last_time))
        pop_mod = calculations.pop_modifier_on_production(5)
        build_mod = self.get_build_mod(last_time)
        morale_mod = self.get_morale_mod(last_time)
        state_mod = self.get_state_mod(last_time)

        # iterate through the list of events, starting from the point where our production points ends.
        # That way we don't have to recalculate the entire list if the changes are only in the end of the events list.
        # As the first part of the production_points list is not outdated, it doesn't have to be recalculated.
        # Hence, the production_points has to be cut off by another method before calling this method at the appropriate
        # location.
        # We always look at the event i-1. If we want to calculate stock to event i, we need the modifiers up until
        # event i, excluding event i. Because that's the relevant production rate up until event i happens.
        for i in range(len(self.production_points) - 1, len(self.events)):
            # How much time passes from the previous event until the event i.
            time = self.events[i][0] - self.events[i - 1][0]

            # Which modifier was the last event, what changed?
            # Pop and Morale Modifier are overwritten, building modifiers add up.
            if self.events[i - 1][1] == "population":
                pop_mod = self.events[i - 1][2]
            elif self.events[i - 1][1] == "building":
                build_mod += self.events[i - 1][2]
            elif self.events[i - 1][1] == "morale":
                morale_mod = self.events[i - 1][2]
            elif self.events[i - 1][1] == "state":
                state_mod = self.events[i - 1][2]

            # Calculate how much has been produced in that time frame and then add it to production_points
            value = self.production_points[i][1] + time * production_rate(self.base_prod, pop_mod, morale_mod,
                                                                          build_mod, state_mod)
            self.production_points.append([self.events[i][0], value])
            print("pop mod: " + str(pop_mod))
            self.production_rate.append(
                [self.events[i][0], production_rate(self.base_prod, pop_mod, morale_mod, build_mod, state_mod)])

    def morale_calculator(self):
        """
        Calculates the morale modifier for production each day and stores it in self.events.
        In self.morale_daily_values (simple list) the daily morale values are stored.
        :return:
        """
        # TODO: special case if bunkers are being built to improve software efficiency:
        # higher morale -> faster bunkers built -> higher morale -> etc

        # remove all morale events from the events list as they are outdated now
        self.events = [ele for ele in self.events if ele[1] != "morale"]

        # Sums all morale targets coming in from national modifiers, building modifiers and daily city modifiers.
        self.morale_targets = self.nation.morale_mod
        for i in range(len(self.morale_targets)):
            self.morale_targets[i] += self.morale_buildings[i] + self.morale_daily_mods[i]

        # Calculate the daily morale values for the city
        for i in range(self.day_of_ownership, len(self.morale_daily_values)):
            # First day of ownership, nothing to calculate TODO: Fix this to accommodate city conquests
            if i == self.day_of_ownership:
                self.morale_daily_values[i] = self.start_morale
                continue
            difference = self.morale_daily_values[i - 1] - self.morale_targets[i - 1]
            # Formula for morale growth is every day 1/7th of the difference from current morale to target morale.
            self.morale_daily_values[i] = self.morale_daily_values[i - 1] + abs(difference) * 1 / 7

        self.morale_construction_mods = []
        # Create events, production modifier from morale
        for i in range(self.day_of_ownership, len(self.morale_daily_values)):
            self.morale_construction_mods.append(
                [i - initiation.day_change, "morale", calculations.morale_to_construction(self.morale_daily_values[i])])
            # Formula to convert morale to morale modifier on production
            modifier = ((self.morale_daily_values[i] / 100) * 0.8) + 0.25
            self.morale_daily_values_mods[i] = modifier
            if i == self.day_of_ownership:
                self.start_morale_mod = modifier
                continue
            self.events.append([i - initiation.start_time, "morale", modifier])

    def population_growth_calculator(self):

        # starting modifier that pop has on production
        self.start_pop_mod = calculations.pop_modifier_on_production(self.start_population)
        # iterate through the daily morale values and translate them to growth speed
        # Time, label "morale" or "building", factor
        growth_mods = self.morale_construction_mods
        # Adds the modifiers from buildings
        if len(self.population_growth_modifiers) != 0:
            growth_mods.append(self.population_growth_modifiers)
        # Sorts the list by time
        growth_mods = sorted(growth_mods, key=lambda x: x[0], reverse=False)

        # remove all pop events from the events list as they are outdated now
        self.events = [ele for ele in self.events if ele[1] != "population"]
        self.population_graph = [[0, self.start_population]]

        current_time = self.ownership_time
        current_pop_level = self.start_population
        current_building_mod = self.population_growth_modifiers_start
        current_morale_mod = calculations.morale_to_construction(self.morale_daily_values[self.day_of_ownership])
        next_pop_level = get_next_pop_level(current_pop_level)

        # First we loop from growth_mod to growth_mod, in growth_mods we have listed all modifiers affecting population growth.
        # Thus, we will be "inside" a growth_mod, where we have the same growth speed, and we work with that
        for i in range(1, len(growth_mods)):
            # time it takes to reach next pop level, not adjusted to modifications
            time_to_next_level = (next_pop_level - current_pop_level) * initiation.population_grow_duration[
                math.trunc(current_pop_level) - 1]
            # Time remaining in until next event that modifies pop growth
            remaining_time = growth_mods[i][0] - growth_mods[i - 1][0]
            # Inside a growth_mod, we will keep looping and growing our population until our population growth speed changes
            while True:
                # How much actual time do we need to grow to the next pop level, applying modifiers
                time_required = time_to_next_level * current_morale_mod * current_building_mod
                # If we advanced to the next population level, yes = True
                # Check if the remaining time we have is at least equal or more to the time we need to progress to the next pop level
                if remaining_time >= time_required:
                    # Since we use time to progress to the next level, we have less remaining_time available
                    remaining_time -= time_required
                    current_time += time_required
                    current_pop_level = next_pop_level
                    modifier = calculations.pop_modifier_on_production(current_pop_level)
                    self.events.append([current_time, "population", modifier])
                    self.population_graph.append([current_time, current_pop_level])
                    next_pop_level += 0.04
                    time_to_next_level = 0.04 * initiation.population_grow_duration[math.trunc(current_pop_level) - 1]
                    continue
                # We do not have enough remaining time, before the next pop growth modifier occurs, to reach the next pop level
                else:
                    # growth is a ratio, 0 to 1, how much % until the next pop level we did
                    growth = remaining_time / time_required
                    pop_difference = next_pop_level - current_pop_level
                    current_pop_level += (growth * pop_difference)
                    current_time += remaining_time
                    break
            # Before we move on to the next growth modifier, we take its modifier and apply it.
            if growth_mods[i][1] == "morale":
                current_morale_mod = growth_mods[i][2]
            elif growth_mods[i][1] == "building":
                current_building_mod += growth_mods[i][2]

    def construct_building(self, time, building_id):
        """
        this method creates events for production, population and morale management.
        Reduction of resources happens on a national basis.
        Building requirement check, prequesits and available time happens elsewhere!
        :param building_id:
        :param time:
        :return:
        """
        # 1. figure out type of building it is
        current_time = time
        pass

    def remove_building(self, name, level):
        pass