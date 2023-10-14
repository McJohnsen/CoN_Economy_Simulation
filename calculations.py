def morale_to_construction(morale):
    """
    Takes morale and calculates the factor that construction, unit production and population growth is affected by.
    Goes from 0.65 to 1.
    :param morale:
    :return: factor to construction speed.
    """
    factor = 0.004 * morale + 0.65
    # efficiency cannot go beyond 1.
    if factor > 1:
        factor = 1
    return factor


def add_graphs(graphs):
    pass


def pop_modifier_on_production(population):
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
