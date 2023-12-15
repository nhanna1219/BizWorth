from plotly.graph_objs import Scatter, Layout, Figure
from plotly.offline import plot
from django.shortcuts import render
import pandas as pd
import random

def plot_div(request):
    actualBizVal = [random.randint(10, 100) for _ in range(12)]
    bizVal = [random.randint(10, 100) for _ in range(12)]
    quarter = ['Q1/2021', 'Q2/2021', 'Q3/2021', 'Q4/2021',
               'Q1/2022', 'Q2/2022', 'Q3/2022', 'Q4/2022',
               'Q1/2023', 'Q2/2023', 'Q3/2023', 'Q4/2023']

    actualValue = Scatter(x=quarter, y=actualBizVal, mode='lines', name='Actual Value Of Business',
                    opacity=0.8, marker_color='green')
    bizValue = Scatter(x=quarter, y=bizVal, mode='lines', name= 'Business Valuation',
                    opacity=0.8, marker_color='gold')

    layout = Layout(
        title="Business Valuation",
        xaxis=dict(
            title="Period",
        ),
        yaxis=dict(
            title="Stock Price"
        ),
        font=dict(
            family="monospace",
            size=14,
            color="black"
        ),
        showlegend=True,
    )
    plot_div = plot({'data': [actualValue, bizValue], 'layout': layout}, output_type='div')

    return plot_div

def plot_chart_fed(request):
    csv_file_path = 'main/static/data/Fed.csv'

    df = pd.read_csv(csv_file_path)

    df = df.dropna()

    fig = Figure()
    fig.add_trace(Scatter(x=df['Quarter'], y=df['Rate'], mode='lines', name='Fed Rate'))
    fig.update_layout(
        title='Fed Interest Rate',
        xaxis=dict(title='Quarter'),
        yaxis=dict(title='Interest Rate'),
    )
    
    graph_html_fed = plot(fig, output_type='div', include_plotlyjs=False)

    return graph_html_fed

def plot_chart_eps(request):
    csv_file_path = 'main/static/data/EPSCSV.csv'

    df = pd.read_csv(csv_file_path)

    df = df.dropna()

    fig = Figure()

    for column in df.columns[1:]:
        fig.add_trace(Scatter(x=df['Quarter'], y=df[column], mode='lines+markers', name=column))

    fig.update_layout(
        title='Earnings Per Share (EPS)',
        xaxis=dict(title='Quarter'),
        yaxis=dict(title='Values'),
        showlegend=True
    )

    graph_html_eps = plot(fig, output_type='div', include_plotlyjs=False)

    return graph_html_eps

def plot_chart_lnst(request):
    csv_file_path = 'main/static/data/LNSTCSV.csv'

    df = pd.read_csv(csv_file_path)

    df = df.dropna()

    fig = Figure()

    for column in df.columns[1:]:
        fig.add_trace(Scatter(x=df['Quarter'], y=df[column], mode='lines+markers', name=column))

    fig.update_layout(
        title='Lợi nhuận sau thuế (đơn vị triệu đồng)',
        xaxis=dict(title='Quarter'),
        yaxis=dict(title='Values'),
        showlegend=True
    )

    graph_html_lnst = plot(fig, output_type='div', include_plotlyjs=False)

    return graph_html_lnst

def home(request):
    
    graph_html_eps = plot_chart_eps(request)
    graph_html_lnst = plot_chart_lnst(request)
    graph_html_fed = plot_chart_fed(request)

    # Chart mẫu
    graph_html_div = plot_div(request)

    return render(request, "home.html", {'graph_html_div': graph_html_div, 'graph_html_eps': graph_html_eps, 'graph_html_lnst': graph_html_lnst, 'graph_html_fed': graph_html_fed})