
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

# ---- PARTE 1 ESTADÍSTICA DESCRIPTIVA ----


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

def f_columnas_tiempos(param_data):
    """Función que regresa una columna que incluye el valor en segundos
    en los que transcurrio cierta operación"""
    param_data['Time'] = param_data.index
    param_data['Time_1'] = pd.to_datetime(param_data['Time'])
    param_data['Time_2'] = pd.to_datetime(param_data["Time.1"])
    param_data['Get_time'] = (param_data['Time_2']-param_data['Time_1']).dt.total_seconds()
    return pd.DataFrame(param_data['Get_time'])


def f_estadisticas_ba(param_data):
    """Función que se le indica la data con la que se está trabajando y regresa 2 tablas,
    una que muestra las operaciones ganadoras y perdedoras así como sus efectividades y la otra
    regresa el raking en porcentaje propio de las operaciones realizadas."""
    d1 = {'Ops totales': len(param_data),
          'Ganadoras': len(param_data[param_data["Profit"] >= 0]),
          'Ganadoras_c': len(param_data[(param_data["Profit"] >= 0) & (param_data["Type"] == "buy")]),
          'Ganadoras_v': len(param_data[(param_data["Profit"] >= 0) & (param_data["Type"] == "sell")]),
          'Perdedoras': len(param_data[param_data["Profit"] <= 0]),
          'Perdedoras_c': len(param_data[(param_data["Profit"] <= 0) & (param_data["Type"] == "buy")]),
          'Perdedoras_v': len(param_data[(param_data["Profit"] <= 0) & (param_data["Type"] == "sell")]),
          'Mediana_profit': (np.percentile(param_data["Profit"], 50)),
          'Mediana_pips': (np.percentile(param_data["Pips"], 50))}
    d1_b = {'r_efectividad': d1['Ganadoras'] / d1['Ops totales'],
            'r_proporcion': d1['Ganadoras'] / d1['Perdedoras'],
            'r_efectividad_c': d1['Ganadoras_c'] / d1['Ops totales'],
            'r_efectividad_v': d1['Ganadoras_v'] / d1['Ops totales']}
    df_1 = pd.DataFrame.from_dict(d1, orient='index', columns=['Valor'])
    df_2 = pd.DataFrame.from_dict(d1_b, orient='index', columns=['Valor'])
    df_1_tabla = pd.concat([df_1, df_2], ignore_index=False)

    sym = np.array(param_data["Symbol"])
    a = [(len(param_data[(param_data["Profit"] > 0) & (param_data["Symbol"] == sym[i])]) / len(
        param_data[param_data["Symbol"] == sym[i]])) for i in range(len(sym))]
    d2 = {'Symbol': sym,
          'Rank%': np.array(a) * 100}
    df_2_ranking = pd.DataFrame.from_dict(d2)

    tables = {'df_1_tabla': df_1_tabla,
              'df_2_ranking': df_2_ranking}

    return tables

# ---- PARTE 2  MÉTRICAS DE ATRIBUCIÓN AL DESEMPEÑO ----

def f_evolucion_capital(param_data):
    """Función a la que se le ingresa el data en análisis y regresa un DataFrame
    que incluye las fechas que se tuvieron de operación, las ganancias y las
    ganancias acumuladas en esos periodos."""
    # Quitando fines de semana
    pd.bdate_range(start=param_data['Time_1'].iloc[0], end=param_data['Time_1'].iloc[-1], freq="B")
    # Groupby para seleccionar las fechas concatenadas
    sum_profits = param_data.groupby(['Time_1']).agg({'Profit': 'sum'}).reset_index()
    sum_profits['profit_acm_d'] = sum_profits['Profit'].cumsum()+100000
    sum_profits.columns = ['timestamp', 'profit_d', 'profit_acm_d']
    return sum_profits

def f_estadisticas_mad(param_data):
    """Función que retorna los ratios de Sharpe y el DrawUp y DrawDown en las fechas
    donde se presentó la mayor o menor pérdida flotante según correspónda.
    Esta función retorna un DataFrame con esa información de manera muy visual y explicativa."""
    # Sharpe ratio original
    ret = f_evolucion_capital(param_data)['profit_acm_d'].pct_change().dropna()
    mean_ret = np.mean(ret)
    rf = 0.05
    desvest = np.std(ret)
    sharpe_rat = (mean_ret - rf)/desvest
    # Sharpe ratio actualizado
    r_trader = mean_ret
    benchmarck = yf.download("^GSPC", start=f_evolucion_capital(positions)['timestamp'].iloc[0], end=f_evolucion_capital(positions)['timestamp'].iloc[-1])
    ret_bench = benchmarck['Adj Close'].pct_change().dropna()
    r_benchmarck = np.mean(ret_bench)
    desvest_shactual = np.std(r_trader-r_benchmarck)
    sharpe_rat_actual = (r_trader - r_benchmarck)/desvest_shactual
    # Drawdown
    drawdown_cap = param_data['Profit'].min()
    a = param_data['Time'].where(param_data['Profit'] == drawdown_cap).dropna()
    b = param_data['Time_2'].where(param_data['Profit'] == drawdown_cap).dropna()
    # Drawup
    drawup_cap = param_data['Profit'].max()
    c = param_data['Time'].where(param_data['Profit'] == drawup_cap).dropna()
    d = param_data['Time_2'].where(param_data['Profit'] == drawup_cap).dropna()
    # Iniciar con las listas de los datos
    est_mad = {'Métrica' : ['sharpe_original', 'sharpe_actualizado', 'drawdown_capi', 'drawdown_capi',
                          'drawdown_capi', 'drawup_capi', 'drawup_capi', 'drawup_capi'],
               '' : ['Cantidad', 'Cantidad', 'Fecha Inicial', 'Fecha Final',
                   'DrawDown $ (capital)', 'Fecha Inicial', 'Fecha Final', 'DrawUp $ (capital)'],
               'Valor' : [sharpe_rat, sharpe_rat_actual, a.iloc[0], b.iloc[0], drawdown_cap,
                         c.iloc[0], d.iloc[0], drawup_cap],
               'Descripción' : ['Sharpe Ratio Fórmula Original', 'Sharpe Ratio Fórmula Ajustada',
                               'Fecha inicial del DrawDown de Capital', 'Fecha final del DrawDown de Capital',
                               'Máxima pérdida flotante registrada', 'Fecha inicial del DrawUp de Capital',
                               'Fecha final del DrawUp de Capital', 'Máxima ganancia flotante registrada']
              }
    # Crear DataFrame
    df_est_mad = pd.DataFrame(est_mad)
    return df_est_mad

# ---- PARTE 3  BEHAVIORAL FINANCE ----

def f_be_de(param_data):
    """Función que regresa el diccionario con la información pertinente al behavioral finance por cada
    ocurrencia que se presenta en el archivo del usuario. Asimismo regresa valores que se utilizarán más
    tarde en la creación de las visualizaciones."""
    param_data["Ratio"] = (param_data["Profit"] / param_data["Profit_acm"]) * 100
    ganadoras = param_data[param_data["Profit"] > 0]
    anclas = pd.DataFrame(ganadoras)
    df_gan = []
    ocurrencias = []
    for i in range(len(anclas)):
        ocu = param_data[(param_data["Time"] <= anclas["Time_2"][i])
                         & (param_data["Time_2"] > anclas["Time_2"][i])
                         & (param_data["Profit"] < 0)]
        df_gan.append(ocu)
        ocurrencias.append(len(ocu))

    sub = []
    for i in range(len(df_gan)):
        a = df_gan[i]
        b = a[a.Profit == a["Profit"].min()]
        sub.append(b)
    df_uni_ancla = pd.concat(sub)

    # DataFrame de las anclas como se pide
    df_anclas = pd.DataFrame(anclas, columns=["Profit", "Ratio"])

    anclas["Time_2"] = pd.to_datetime(anclas["Time_2"])
    pf = []
    for i in range(len(df_uni_ancla)):
        for j in range(len(anclas)):
            price = mt5.copy_ticks_from(df_uni_ancla["Symbol"][i],
                                        anclas["Time_2"][j],
                                        1,
                                        mt5.TIMEFRAME_M5)

        if df_uni_ancla["Type"][j] == "buy":
            p_f = price[0][1]
        else:
            p_f = price[0][2]
        pf.append(p_f)
    df_uni_ancla["Price_down"] = pf

    def f_pips2(df_uni_ancla):
        df_uni_ancla["Pips2"] = [(df_uni_ancla['Price_down'].iloc[i] - df_uni_ancla['Price'].iloc[i]) * f_pip_size(
            df_uni_ancla['Symbol'].iloc[i])
                                 if df_uni_ancla['Type'].iloc[i] == 'buy'
                                 else (df_uni_ancla['Price'].iloc[i] - df_uni_ancla['Price_down'].iloc[i]) * f_pip_size(
            df_uni_ancla['Symbol'].iloc[i])
                                 for i in range(len(df_uni_ancla))]
        return df_uni_ancla

    perdedoras = f_pips2(df_uni_ancla)
    perdedoras["Profit_perdedora"] = (perdedoras["Profit"] / perdedoras["Pips"]) * perdedoras["Pips2"]
    perdedoras = perdedoras[perdedoras["Profit_perdedora"] < 0]

    status_quo = []
    aversion_per = []

    for i in range(len(perdedoras)):
        if perdedoras["Profit_perdedora"][i] / anclas["Profit_acm"][i] < anclas["Profit"][i] / anclas["Profit_acm"][i]:
            status_quo.append(1)
        else:
            status_quo.append(0)
        if perdedoras["Profit_perdedora"][i] / anclas["Profit"][i] > 2:
            aversion_per.append(1)
        else:
            aversion_per.append(0)

        sens_decreciente = 0
        if anclas["Profit_acm"][0] < anclas["Profit_acm"][-1]:
            sens_decreciente += 1
        if anclas["Profit"][-1] > anclas["Profit"][0] and perdedoras["Profit_perdedora"][-1] > \
                perdedoras["Profit_perdedora"][0]:
            sens_decreciente += 1
        if perdedoras["Profit_perdedora"][-1] / anclas["Profit"][-1] > 2:
            sens_decreciente += 1
        if sens_decreciente >= 2:
            sens_dec_comp = "Tiene sensibilidad decreciente"
        else:
            sens_dec_comp = "No tiene sensibilidad decreciente"

        # Sensibilidad para la gráfica 3
        total_sen = 0
        for i in range(1, len(perdedoras)):
            sen_graf = 0
            if anclas["Profit_acm"][i - 1] < anclas["Profit_acm"][i]:
                sen_graf += 1
            if anclas["Profit"][i] > anclas["Profit"][i - 1] and perdedoras["Profit_perdedora"][i] > \
                    perdedoras["Profit_perdedora"][i - 1]:
                sen_graf += 1
            if perdedoras["Profit_perdedora"][i] / anclas["Profit"][i] > 2:
                sen_graf += 1
            if sen_graf >= 2:
                total_sen += 1
            else:
                total_sen = total_sen

        d = {'Ocurrencias': len(ocurrencias),
             'Status_quo': round((np.array(status_quo).sum() / len(status_quo) * 100), 2).astype(str) + "%",
             'Aversión_perdida': (np.array(aversion_per).sum() / len(aversion_per) * 100).astype(str) + "%",
             'Sensibilidad_decreciente': sens_dec_comp}

        dic = {"Ocurrencias": {
            "Cantidad": len(ocurrencias)}}
        for i in range(len(anclas)):
            dic[f"Ocurrencia_{i + 1}"] = {'Timestamp': [anclas["Time_2"][i]],
                                          'Operaciones': {
                                              'Ganadora': {
                                                  'Instrumento': anclas['Symbol'][i],
                                                  'Volumen': anclas['Volume'][i],
                                                  'Sentido': anclas['Type'][i],
                                                  'Profit_ganadora': anclas["Profit"][i]},
                                              'Perdedora': {
                                                  'Instrumento': perdedoras['Symbol'][i],
                                                  'Volumen': perdedoras['Volume'][i],
                                                  'Sentido': perdedoras['Type'][i],
                                                  'Profit_perdedora': perdedoras["Profit_perdedora"][i]},

                                              'Ratio_cp_profit_acm': {perdedoras["Profit_perdedora"][i] /
                                                                      anclas["Profit_acm"][i]},
                                              'Ratio_cg_profit_acm': {anclas["Profit"][i] /
                                                                      anclas["Profit_acm"][i]},
                                              'Ratio_cp_cg': {perdedoras["Profit_perdedora"][i] /
                                                              anclas["Profit"][i]}
                                          }}
        dic["df"] = {'Dataframe': d}
    return dic, status_quo, aversion_per, total_sen
