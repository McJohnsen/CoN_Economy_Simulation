import math

def morale_influence(morale):
    """
    Takes morale and calculates the factor that construction, unit production and population growth is affected by.
    Goes from 0.65 to 1.
    :param morale: morale percentage, between 0 and 1.
    :return: factor to construction speed.
    """
    factor = 0.004 * morale + 0.65
    # efficiency cannot go beyond 1.
    if factor > 1:
        factor = 1
    return factor


def morale_influence_on_production(morale):
    """

    :param morale:
    :return:
    """
    return morale * 0.8 / 100 + 0.25


def add_graphs(graphs):
    pass


def pop_modifier_on_production(population):
    """
    Enter population level, get modifier on resource production
    :param population: Between 1 and 10
    :return:
    """
    if population >= 5:
        factor = population - 5
        factor *= 0.05
        factor += 1
        return factor
    else:
        factor = 5 - population
        factor *= 0.2
        factor = 1 - factor
        return factor


def morale_change(current_morale: float, target_morale: float):
    new_morale = current_morale + (target_morale - current_morale) / 7
    if new_morale > 100:
        new_morale = 100
    return math.ceil(new_morale)
