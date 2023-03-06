# %% imports
import numpy as np
import pandas as pd
import gamstransfer as gt


# %% functions
def timesort(df, index_sets='h_1', timeindex_name='h_1', timeindex_string='h'):
    """
    Sorts a pandas dataframe indexed by a string-float combination by float (ignoring string) in descending order.
    Useful for sorting GAMS-time-set-indexed data.
    :param df: A dataframe indexed by a float-string combination
    :param index_sets: column name(s) to be used as index
    :param timeindex_name: name of df's index. Defaults to 't'
    :param timeindex_string:
    :return:
    """
    df.reset_index(inplace=True)
    df['hix'] = pd.to_numeric(df[timeindex_name].str.split(pat=timeindex_string).str.get(1))
    df.sort_values(by=['hix'], inplace=True)
    df.set_index(index_sets, drop=True, inplace=True)
    df.drop(columns=['hix'], inplace=True)
    return df


def modify(input_gdx, symbol_values_dict, output_gdx=None):
    """
    Modifies an existing GAMS container by adding or changing symbols
    :param output_gdx: optional; path and name for newly created output gdx-file
    :param input_gdx: path to a GAMS gdx-file
    :param symbol_values_dict: a dictionary {SymbolName: pd.DataFrame(
    data=[setid1, value], columns=['set1', 'Value'])}
    :return:
    """
    container = gt.Container(input_gdx)
    pm_clct = {}
    for symbol, dataframe in symbol_values_dict.items():
        if symbol in container:
            container.removeSymbols(symbol)

        if np.array_equal(symbol_values_dict[symbol]['Value'].values,
                          symbol_values_dict[symbol]['Value'].values.astype(bool)):
            pm_clct[symbol] = gt.Set(container, symbol, records=dataframe)
        elif np.array_equal(symbol_values_dict[symbol]['Value'].values,
                          symbol_values_dict[symbol]['Value'].values.astype(float)):
            sets = list(dataframe.columns)
            sets.remove('Value')
            pm_clct[symbol] = gt.Parameter(container, symbol, sets, records=dataframe)
        else:
            print('Wrong value type. Can not infer symbol type')

    if output_gdx is not None:
        container.write(output_gdx)
    else:
        container.write(input_gdx)


def gdxscale_y2h(gdx, symbol, annualval, output_gdx):

    container = gt.Container(gdx)
    ts = container.data[symbol].records
    sets = list(ts.columns)
    sets.remove('value')
    ts = ts.set_index(sets)
    sets_clean = [s.split('_', 1)[0] for s in sets]
    ts.index = ts.index.rename(sets_clean)

    scaling_factor = annualval / ts.sum()
    ts_scaled = ts * scaling_factor
    ts_scaled = ts_scaled.reset_index()
    container.removeSymbols(symbol)
    gt.Parameter(container, symbol, sets, records=ts_scaled)
    container.write(output_gdx)
