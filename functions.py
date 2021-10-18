
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Estas son las funciones que se necesitan para el laboratorio 3 de MyST                                                         -- #
# -- script: functions.py : python script with general functions                                         -- #
# -- author: labv98                                                                  -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/labv98/MyST_Lab3_LABV.git                                                                    -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

# Librerías a utilizar
import numpy as np
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime

# ----PARTE 1 ESTADÍSTICA DESCRIPTIVA----

# Función que lee los archivos en excel
def f_leer_archivo(param_archivo):
    """Función a la que se le ingresa el path del archivo .xlsx y
        regresa los dataframes de positions and orders"""
    positions = pd.read_excel(param_archivo,"Sheet1", skiprows = 6, nrows = 14, usecols = "A:M")
    orders = pd.read_excel(param_archivo,"Sheet1", skiprows = 22, nrows = 30, usecols = "A:J")
    return display(positions, orders)

# Función que lee los archivos desde Metatrader 5
def f_initialize(path,login,password,server):
    """Función a la que se le ingresa el path de la terminal de mt5,
        así como tu usuario, contraseña y servidor para poder acceder a la cuenta"""
    ini = mt5.initialize(path=path, login=login, password=password, server=server)
    if not ini:
        print("No se inicializó = ", mt5.last_error())
    else:
        print("Cuenta inicializada =", mt5.account_info())
        hist_deals = mt5.history_deals_get(datetime(2021,1,1), datetime.now())
        df_deals = pd.DataFrame(list(hist_deals), columns=hist_deals[0]._asdict().keys())
        hist_orders = mt5.history_orders_get(datetime(2021,1,1), datetime.now())
        df_orders = pd.DataFrame(list(hist_orders), columns=hist_orders[0]._asdict().keys())
        df_deals.to_excel("Report_DEALS_user.xlsx")
        df_orders.to_excel("Report_ORDERS_user.xlsx")
    return mt5, display(df_deals), display(df_orders)