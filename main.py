
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Aquí se encuentra el main del laboratorio 3                                             -- #
# -- script: main.py : python script with the main functionality                                         -- #
# -- author: labv98                                                                       -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/labv98/MyST_Lab3_LABV.git                                           -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

from functions import *
from visualizations import *

# Por si existe algún warning
import warnings
warnings.simplefilter("ignore")

# ---- PARTE 1 ESTADÍSTICA DESCRIPTIVA ----

mt5, df_deals, df_orders = f_initialize("C:\Program Files\FxPro_MetaTrader5\\terminal64.exe", 5400340, "B31gdeC6", "FxPro-MT5")
print(mt5)

df_deals.head()

df_orders.head()

positions, orders, deals = f_leer_archivo("C:/Users/Cesar/PycharmProjects/MyST_Lab3_LABV/ReportHistory_Alejandra.xlsx")

print(positions)

orders.head()

deals.head()

f_pip_size("CADJPY")

f_columnas_tiempos(positions)

f_columnas_pips(positions)

print(f_estadisticas_ba(positions)['df_1_tabla'])

print(f_estadisticas_ba(positions)['df_2_ranking'])

# ---- PARTE 2  MÉTRICAS DE ATRIBUCIÓN AL DESEMPEÑO ----

# Pasar la fecha a formato str Y,m,d (fuera de la función porque solo se convierte una vez y
# la función se manda llamar posteriormente)
positions['Time_1'] = [i.strftime('%Y-%m-%d') for i in positions['Time_1']]

f_evolucion_capital(positions)

f_estadisticas_mad(positions)

# ---- PARTE 3  BEHAVIORAL FINANCE ----

# Pasar la fecha a formato str Y,m,d, H,M,S (fuera de la función porque solo se convierte una vez y
# la función se manda llamar posteriormente)
positions['Time_2'] = [i.strftime("%Y/%m/%d, %H:%M:%S") for i in positions['Time_2']]

dic, status_quo, aversion_per, total_sen = f_be_de(positions)
print(dic)

# Pasando a DataFrame lo final del dic con los resultados
bf = pd.DataFrame.from_dict(dic["df"], orient='index')
print(bf)

# ---- PARTE 4  VISUALIZACIONES ----

graf_1(positions)

graf_2(positions)

graf_3(positions)
