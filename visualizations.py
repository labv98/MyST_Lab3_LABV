
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Aquí se encuentran los códigos para las visualizaciones                              -- #
# -- script: visualizations.py : python script with data visualization functions                         -- #
# -- author: labv98                                                                      -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/labv98/MyST_Lab3_LABV.git                                         -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
import plotly.graph_objects as go
from functions import *

def graf_1(param_data):
    labels = f_estadisticas_ba(param_data)['df_2_ranking']["Symbol"].to_list()
    values = f_estadisticas_ba(param_data)['df_2_ranking']["Rank%"].to_list()
    pie_chart = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0, 0, 0.2, 0],
                                       textinfo='label+percent')])
    pie_chart.update_layout(title_text = 'Gráfica 1: Ranking')
    return pie_chart.show()

def graf_2(param_data):
    df = pd.DataFrame(dict(
         y = [99779.34-206.1, 100034.64],
         x = ["2021-9-23", "2021-9-23"]))
    df_2 = pd.DataFrame(dict(
         y = [99779.34, 99779.34-206.1],
         x = ["2021-9-20", "2021-9-23"]))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.x, y=df.y, name ='Drawup',
                             line = dict(color='green', dash='dash')))
    fig.add_trace(go.Scatter(x=df_2.x, y=df_2.y, name ='Drawdown',
                             line = dict(color='red', dash='dash')))
    fig.add_trace(go.Scatter(x = f_evolucion_capital(param_data)['timestamp'],
                             y = f_evolucion_capital(param_data)['profit_acm_d'],
                             name = "Profit_acum_d",
                             line = dict(color='black')))
    fig.update_layout(title = 'Gráfica 2: DrawDown y DrawUp',
                      xaxis_title = 'Fecha',
                      yaxis_title = 'Profit $')
    return fig.show()

def graf_3(param_data):
    dic, status_quo, aversion_per, total_sen = f_be_de(param_data)
    d_e = ['status_quo', 'aversion_perdida', 'sensibilidad_decreciente']
    fig = go.Figure(data=[
          go.Bar(name='Sí', x=d_e, y=[np.array(status_quo).sum(),
                                      np.array(aversion_per).sum(),
                                      total_sen]),
          go.Bar(name='No', x=d_e, y=[len(status_quo)-np.array(status_quo).sum(),
                                      len(aversion_per)-np.array(aversion_per).sum(),
                                      len(aversion_per)-total_sen])])

    fig.update_layout(title = 'Gráfica 3: Disposition Effect',
                      yaxis_title = 'Incidencias',
                      barmode='group')
    return fig.show()
