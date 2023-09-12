import pandas as pd

def build_multi_bench_universe_expression(benchs):
    formula = '('
    for x in range(len(benchs)-1):
        formula +='FG_CONSTITUENTS('+benchs[x]+',0,CLOSE)=1 OR '
    formula+='FG_CONSTITUENTS('+benchs[-1]+',0,CLOSE)=1)=1'
    return formula

def build_multi_bench_formulas(benchs):
    formulas = []
    for bench in benchs:
        form = 'ZAV(FG_CONSTITUENTS('+bench+',0,CLOSE))'
        formulas.append(form)
    return formulas


def build_multi_conditional_expression(formulas,operator='OR',mixed_list = None):
    formula = '('
    if (mixed_list ==None):
        for x in range(len(formulas)-1):
            formula +='FG_CONSTITUENTS('+formulas[x]+',0,CLOSE)=1 '+operator+' '
        formula+='FG_CONSTITUENTS('+formulas[-1]+',0,CLOSE)=1)=1'
    else:
        for x in range(len(formulas)-1):
            formula +='FG_CONSTITUENTS('+formulas[x]+',0,CLOSE)=1 '+mixed_list[x]+' '
        formula+='FG_CONSTITUENTS('+formulas[-1]+',0,CLOSE)=1)=1'
    return formula