
import pandas as pd
import numpy as np
import pandas as pd
import re

def replace_equation(map_dict, equation):
    keys = sorted(map_dict, key=len, reverse=True) # sorted by length, in case one expression is a prefix of another
    regexp = re.compile('|'.join(map(re.escape, keys)))

    while re.search('#P.P', equation):
        equation = regexp.sub(lambda match: '(' + map_dict[match.group(0)] + ')', equation)
    return equation  # Add a semicolon at the end of the equation

def convert_formulas_with_ref_var(variables,formulas):

    concatenated_variables = []
    for variable in variables:
        concatenated_variable = "#P." + str(variable)
        concatenated_variables.append(concatenated_variable)
    mapping_table = dict(zip(concatenated_variables, formulas))

    map_dict = mapping_table
    transformed_formulas = []
    for formula in formulas:
        transformed_formulas.append(replace_equation(map_dict, formula))

    return transformed_formulas

