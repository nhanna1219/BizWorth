from datetime import datetime
from plotly.graph_objs import Scatter, Layout, Figure
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import plotly.express as px
from plotly.offline import plot
from main.modules import forecast
from django.shortcuts import render
from main.modules import pe, mx4, canslim
from main.common import const
import pandas as pd
import random
import json
import os
import time
import asyncio

helper_PE = pe.PEHelper()
helper_cs = canslim.CanslimHelper()
helper_mx = mx4.Mx4Helper()
helper_forcast = forecast.ForecastHelper()
class TickerData:
    def __init__(self, data_dict):
        for key, value in data_dict.items():
            setattr(self, key, value)

def get_outstanding_share_and_average_pe(ticker):
    df = pd.read_csv('main/static/data/tickers.csv', header=None)
    matching_row = df[df[0] == ticker]
    if not matching_row.empty:
        outstanding_share = matching_row.iloc[0, 2]
        pe_ratio = matching_row.iloc[0, 3]
        print(outstanding_share, pe_ratio)
        return outstanding_share, pe_ratio
    else:
        return None, None

def read_files_for_ticker(ticker, base_dir="main/static/data"):
    ticker_dir = os.path.join(base_dir, ticker)
    
    if not os.path.exists(ticker_dir):
        raise ValueError(f"No directory found for ticker: {ticker}")
    
    data = {}
    
    for file in os.listdir(ticker_dir):
        if file.endswith('.csv'):
            file_path = os.path.join(ticker_dir, file)
            data[file.split('.')[0]] = pd.read_csv(file_path)
    return data 

def plot_chart(csv_file_path, title, x_title, y_title):
    df = pd.read_csv(csv_file_path)

    fig = Figure()

    for column in df.columns[1:]:
        fig.add_trace(Scatter(x=df['Quarter'], y=df[column], mode='lines+markers', name=column))

    fig.update_layout(
        title=title,
        xaxis=dict(title=x_title),
        yaxis=dict(title=y_title),
        showlegend=True
    )

    graph_html = plot(fig, output_type='div', include_plotlyjs=False)

    return graph_html

def plot_chart_fed():
    return plot_chart('main/static/data/Fed.csv', 'Fed Interest Rate', 'Quý', 'Lãi suất')

def plot_chart_eps():
    return plot_chart('main/static/data/EPS.csv', 'Earnings Per Share (EPS)', 'Quý', 'Giá trị')

def plot_chart_lnst():
    return plot_chart('main/static/data/LNST.csv', 'Lợi nhuận sau thuế', 'Quý', 'Giá trị (đơn vị triệu đồng)')

async def trainModelAsync(tickers):
    tasks = [train_single_model_async(ticker) for ticker in tickers]
    await asyncio.gather(*tasks)

async def train_single_model_async(ticker):
    data = TickerData(read_files_for_ticker(ticker['short_name']))
    await plot_stock_price(ticker['short_name'], npat_df=data.NPAT_Q, pe_df=data.FinancialReport_Y, stock_df=data.StockPrice)
        
def plot_stock_price(ticker,npat_df,pe_df,stock_df):
    # Load the dataset containing Net Profit After Tax (NPAT) by quarter
    helper_forcast.SetDataFrame(npat_df)
    helper_forcast.FormatDate(const.DATE_MODE)
    # helper_forcast.GenerateModel(10, 10)
    # helper_forcast.SaveModel("main/static/data/_model/", f"NPAT_Model_{ticker}") 
    
    # Load the pre-trained model
    helper_forcast.LoadModel(f"main/static/data/_model/NPAT_Model_{ticker}.pkl")
    current_year = datetime.now().year

    # Get current year's NPAT data
    npat_current = npat_df[npat_df['Date'].dt.year == current_year]
    df_forcast = helper_forcast.Forecast(12 - len(npat_current), const.DATE_MODE)
    df_concat = pd.concat([npat_df, df_forcast])
    df_concat.to_csv('main/static/data/test.csv', header=None)
    npat_list = df_concat['NOPAT'].tolist()
    data_point = helper_PE.GetDataPoints(npat_list, 4)

    # Load the dataset containing the P/E historical data
    pe_last_year = pe_df.iloc[-1]["PE"]
    
    outstanding_share,pe_avg_industry = get_outstanding_share_and_average_pe(ticker)
    forecasted_stock_price = helper_PE.ForecastStockPrices(data_point[:4], outstanding_share, pe_last_year) + \
                             helper_PE.ForecastStockPrices(data_point[4:], outstanding_share, pe_avg_industry)
    f_stockPrice = [round(num / 10**3, 2) for num in forecasted_stock_price]

    # Load the dataset containing historical stock prices
    stock_df['tradingTime'] = pd.to_datetime(stock_df['tradingTime'])
    # Filter the data frame to display prices from the last year
    df_plot = stock_df[stock_df['tradingTime'].dt.year >= (current_year - 1)]
    actual_date = df_plot["tradingTime"].tolist()
    last_price_plot = df_plot["lastPrice"].tolist()
    date_range = [current_year - 1, current_year] + [i + current_year for i in range(1, 3)]
    
    # Create the plot with actual and forecasted stock prices
    fig = Figure()
    fig.add_trace(Scatter(x=actual_date, y=last_price_plot, name='Giá trị thực tế',
                          line=dict(color='firebrick', width=4)))
    fig.add_trace(Scatter(x=date_range, y=f_stockPrice, name='Giá trị dự đoán',
                          line=dict(color='darkblue', width=4, dash='dash')))
    fig.update_layout(
        title='Dự đoán giá trị cổ phiếu dựa trên tỉ lệ P/E',
        xaxis_title='Thời gian',
        yaxis_title='Giá cổ phiếu (đơn vị: nghìn VNĐ)',
        legend_title='Legend'
    )
    graph_html = plot(fig, output_type='div', include_plotlyjs=False)
    return graph_html
    
def plot_canslim(df_sale,df_financialRP,data_point=20):
    
    sales = helper_cs.GetDataPoints(df_sale['Sales'].tolist(),data_point)
    eps = helper_cs.GetDataPoints(df_financialRP['EPS'].tolist(),data_point)
    canslim_score = helper_cs.CalListCanslimScores(sales, eps)
    evaluated_score = helper_cs.EvaluateCanslimScore(canslim_score[0])

    actual_date = df_sale["Date"].iloc[-len(canslim_score):]
    
    evaluate_values = [helper_cs.EvaluateCanslimScore(i) for i in canslim_score]
    # Create the Canslim Score Plot
    fig = Figure()
    fig.add_trace(
        Scatter(
            x=actual_date,
            y=canslim_score,
            name='',
            line=dict(color='firebrick', width=4),
            hovertemplate='<b>%{customdata}</b>' +
                        '<br><i>Điểm</i>: %{y:.2f}',
            customdata=evaluate_values
        )
    )
    fig.update_layout(
        title='Điểm Canslim',
        xaxis_title='Thời gian',
        yaxis_title='Giá trị',
        legend_title='Legend',
        hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            font_family="Rockwell"
        ),
        hovermode='x unified',
    )
    graph_html = plot(fig, output_type='div', include_plotlyjs=False)
    return graph_html

def plot_4m(sale_df,financial_df,npat_df,opc_df):
    opc = opc_df["opc"].tail(10).tolist()
    eps = financial_df["EPS"].tail(10).tolist()
    bvps = financial_df["BVPS"].tail(10).tolist()
    ld = financial_df["Long-term Liabilities"].tail(10).tolist()
    assets = financial_df["Total Assests"].tail(10).tolist()
    equity = financial_df["Owner's Equity"].tail(10).tolist()
    npat = npat_df["NOPAT"].tail(10).tolist()
    sales = sale_df["Sales"].tail(10).tolist()
    
    actual_date = sale_df['Date'].tail(5).astype(str).tolist()
    
    data = mx4.Data4M(sales,eps,bvps,opc,ld,npat,assets,equity)
    mx4_score = helper_mx.CalList4MScores(helper_mx.GetDataPoints(data,5))
    evaluate_values = [helper_mx.Evaluate4MScore(i) for i in mx4_score]
    
    fig = Figure()
    fig.add_trace(
        Scatter(
            x=actual_date,
            y=mx4_score,
            mode='markers+lines',
            name='',
            line=dict(color='firebrick', width=4),
            hovertemplate='<b>%{customdata}</b>' +
                        '<br><i>Điểm</i>: %{y:.2f}',
            customdata=evaluate_values
        )
    )
    fig.update_layout(
        title='Điểm 4M',
        xaxis_title='Thời gian',
        yaxis_title='Giá trị',
        legend_title='Legend',
        hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            font_family="Rockwell"
        ),
        hovermode='x unified',
    )
    graph_html = plot(fig, output_type='div', include_plotlyjs=False)
    return graph_html

@csrf_exempt
def get_ticker_chart(request):
    # FinancialReport_Q, FinancialReport_Y,NPAT_Q,NPAT_Y,Sales_Q,Sales_Y,StockPrice,opc
    if request.method == 'POST':
        data = json.loads(request.body)
        ticker = data.get('ticker')
        data = TickerData(read_files_for_ticker(ticker))
        graph_stock_pred = plot_stock_price(ticker, npat_df=data.NPAT_Q, pe_df=data.FinancialReport_Y, stock_df=data.StockPrice)
        graph_canslim_score = plot_canslim(df_sale=data.Sales_Q,df_financialRP=data.FinancialReport_Q)
        graph_4m_score = plot_4m(sale_df=data.Sales_Y, financial_df=data.FinancialReport_Y, npat_df=data.NPAT_Y, opc_df=data.opc)
        return JsonResponse(
            {
                'graph_stock_pred': graph_stock_pred,
                'graph_canslim_score': graph_canslim_score,
                'graph_4m_score': graph_4m_score,
            })

    return JsonResponse({'error': 'Invalid request'}, status=400)

async def home(request):
    # graph_html_eps = plot_chart_eps()
    # graph_html_lnst = plot_chart_lnst()
    # graph_html_fed = plot_chart_fed()
    df = pd.read_csv(f'main/static/data/tickers.csv', header=None)
    df.columns = ['short_name', 'full_name','outstanding_share', 'pe_avg_industry']
    tickers = df.to_dict('records')
    # await trainModelAsync(tickers)
    return render(request, "home.html", {
        # 'graph_html_eps': graph_html_eps, 
        # 'graph_html_lnst': graph_html_lnst, 
        # 'graph_html_fed': graph_html_fed, 
        'tickers': tickers
    })

# shares_outstanding = 2089955445.00
#     pe_avg_industry = 33.46