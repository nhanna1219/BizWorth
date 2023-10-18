from plotly.graph_objs import Scatter
from plotly.graph_objs import Scatter, Layout
from plotly.offline import plot
from django.shortcuts import render
import random

def home(request):
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

    return render(request, "home.html", context={'plot_div': plot_div})
