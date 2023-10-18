import plotly.express as px
import plotly.offline as opy

def scatter_plot():
    fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
    div = opy.plot(fig, auto_open=False, output_type='div')
    return div