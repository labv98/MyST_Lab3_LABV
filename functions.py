
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Estas son las funciones que se necesitan para el laboratorio 3 de MyST                     -- #
# -- script: functions.py : python script with general functions                                         -- #
# -- author: labv98                                                                  -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/labv98/MyST_Lab3_LABV.git                                            -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

# Librerías a utilizar
import numpy as np
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime
import yfinance as yf

# ----PARTE 1 ESTADÍSTICA DESCRIPTIVA----


def f_initialize(path, login, password, server):
    """Función que inicializa el servidor de Metatrader 5, con tu usuario y contraseña
    asimismo descarga los archivos necesarios a analizar."""
    ini = mt5.initialize(path=path, login=login, password=password, server=server)
    if not ini:
        print("No se inicializó = ", mt5.last_error())
    else:
        print("Cuenta inicializada =", mt5.account_info())
        hist_deals = mt5.history_deals_get(datetime(2021, 1, 1), datetime.now())
        df_deals = pd.DataFrame(list(hist_deals), columns=hist_deals[0]._asdict().keys())
        df_deals["time"] = pd.to_datetime(df_deals["time"], unit="s")
        hist_orders = mt5.history_orders_get(datetime(2021, 1, 1), datetime.now())
        df_orders = pd.DataFrame(list(hist_orders), columns=hist_orders[0]._asdict().keys())
        df_orders["time_setup"] = pd.to_datetime(df_orders["time_setup"], unit="s")
        df_orders["time_done"] = pd.to_datetime(df_orders["time_done"], unit="s")
        use_cols = ["time", "ticket", "symbol", "type", "volume", "price",
                    "order", "commission", "swap", "profit", "comment"]
        use_cols2 = ["time_setup", "time_done", "ticket", "symbol", "type",
                     "volume_initial", "price_open", "sl", "tp", "state", "comment"]
        return mt5, df_deals[use_cols], df_orders[use_cols2]


def f_leer_archivo(param_archivo):
    """Función a la que se le ingresa el path del archivo .xlsx y
    regresa los dataframes de positions, orders and deals"""
    file = pd.read_excel(param_archivo, "Sheet1", skiprows=6, index_col="Time")
    use_columns = [i for i in file.columns if "Unnamed" not in i]
    positions = file.loc[:"Orders", use_columns].iloc[:-1]
    orders = file.loc["Orders":].iloc[1:].drop(["Commission", "Profit"], axis=1)
    orders.columns = orders.iloc[0].values
    orders = orders.loc[:"Deals"].iloc[:-1]
    orders.index.name = orders.index[0]
    orders = orders.iloc[1:, :-1]
    deals = file.loc["Deals":].iloc[1:]
    deals = deals.loc[:"Balance:"].iloc[:-2]
    deals.columns = deals.iloc[0].values
    deals = deals.iloc[1:, :-1]
    return positions, orders, deals


def f_pip_size(param_ins):
    """Función que expresa el número multiplicador para expresar la diferencia en pips.
    La entrada es el instrumento del que se quiere conocer el multiplicador de pips."""
    if f_initialize:  # f_initialize es la función inicializadora con la que comenzó el proyecto
        pip_size = 0.1/mt5.symbol_info(param_ins)._asdict().get("trade_tick_size")
        return pip_size
    else:
        return print("No existe esa entrada")


def f_columnas_pips(param_data):
    """Función que regresa los pips resultantes por operación con su signo incluído,
    además regresa los pips acumulados y el profit acumulado de todas las operaciones.}
    La entrada es el data en análisis."""
    pips = []
    for i in range(len(param_data)):
        if (param_data["Type"].iloc[i] == "buy"):
            pips.append((param_data["Price.1"].iloc[i] - param_data["Price"].iloc[i]) * f_pip_size(param_data["Symbol"].iloc[i]))
        elif (param_data["Type"].iloc[i] == "sell"):
            pips.append((param_data["Price"].iloc[i] - param_data["Price.1"].iloc[i]) * f_pip_size(param_data["Symbol"].iloc[i]))
        else:
            pips.append(print("Se presenta algún error"))
    param_data["Pips"] = pips
    param_data["Pips_acm"] = param_data["Pips"].cumsum()
    param_data["Profit_acm"] = param_data["Profit"].cumsum()
    return param_data