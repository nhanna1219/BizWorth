from datetime import datetime
import threading
from plotly.graph_objs import Scatter, Layout, Figure
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import plotly.express as px
from plotly.offline import plot
from main.modules import forecast
from django.shortcuts import render
from main.modules import pe, mx4, canslim
from main.modules import format_json as fmt
from main.common import const
import pandas as pd
import random
import json
import os
import time
import asyncio
import requests
import re

helper_PE = pe.PEHelper()
helper_cs = canslim.CanslimHelper()
helper_mx = mx4.Mx4Helper()
helper_forcast = forecast.ForecastHelper()
tickerData = None

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
        fig.add_trace(Scatter(x=df['Quarter'], y=df[column], mode='lines+markers', name=column,
                              line=dict(width=3)))

    fig.update_layout(
        template='gridon',
        title={
            'text': f"<b>{title}</b>",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis=dict(
            title='<i>Thời gian</i>',
            titlefont=dict(
                size=11
            )
        ),
        yaxis=dict(
            title='<i>Giá cổ phiếu (đơn vị: nghìn VNĐ)</i>',
            titlefont=dict(
                size=11
            )
        ),
        margin=dict(
            l=130,  
            b=130,  
        ),
        legend_title='Legend',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Rockwell"
        ),
        hovermode='x unified',
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
    npat_df_copy = npat_df.copy()
    helper_forcast.SetDataFrame(npat_df_copy)
    helper_forcast.FormatDate(const.DATE_MODE)
    # helper_forcast.GenerateModel(10, 10)
    # helper_forcast.SaveModel("main/static/data/_model/", f"NPAT_Model_{ticker}") 
    
    # Load the pre-trained model
    helper_forcast.LoadModel(f"main/static/data/_model/NPAT_Model_{ticker}.pkl")
    current_year = datetime.now().year

    # Get current year's NPAT data
    npat_current = npat_df_copy[npat_df_copy['Date'].dt.year == current_year]
    if npat_current.empty:
        current_year -= 1
        npat_current = npat_df_copy[npat_df_copy['Date'].dt.year == (current_year)]
        
    df_forcast = helper_forcast.Forecast(12 - len(npat_current), const.DATE_MODE)
    df_concat = pd.concat([npat_df, df_forcast])
    npat_list = df_concat['NOPAT'].tolist()
    # npat_list = [x / 1e9 for x in npat_list]
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
    date_range = [f"{year}-12-31" for year in date_range]
    
    # Create the plot with actual and forecasted stock prices
    fig = Figure()
    fig.add_trace(Scatter(x=actual_date, y=last_price_plot, name='Giá trị thực tế',
                          line=dict(color='#1f77b4', width=3)))
    fig.add_trace(Scatter(x=date_range, y=f_stockPrice, name='Giá trị dự đoán',
                          line=dict(color='firebrick', width=3, dash='dash')))
    
    fig.update_layout(
        template='gridon',
        title={
            'text': "<b>Dự đoán giá trị cổ phiếu dựa trên tỉ lệ P/E</b>",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis=dict(
            title='<i>Thời gian</i>',
            titlefont=dict(
                size=11
            )
        ),
        yaxis=dict(
            title='<i>Giá cổ phiếu (đơn vị: nghìn VNĐ)</i>',
            titlefont=dict(
                size=11
            )
        ),
        margin=dict(
            l=110,  
            b=110,  
        ),
        legend_title='Legend',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Rockwell"
        ),
        hovermode='x unified',
    )
    graph_html = plot(fig, output_type='div', include_plotlyjs=False)
    return graph_html
    
def plot_canslim(df_sale,df_financialRP,data_point=None,redraw=False):
    # Check on max data point
    max_data_point_sales = helper_cs.CountDataPoints(df_sale['Sales'])
    max_data_point_eps = helper_cs.CountDataPoints(df_financialRP['EPS'])
    max_data_point = min(max_data_point_sales, max_data_point_eps)
    if data_point is None:
        data_point = max_data_point
    sales = helper_cs.GetDataPoints(df_sale['Sales'].tolist(),data_point)
    eps = helper_cs.GetDataPoints(df_financialRP['EPS'].tolist(),data_point)
    canslim_score = helper_cs.CalListCanslimScores(sales, eps)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
    evaluated_score = helper_cs.EvaluateCanslimScore(canslim_score[0])

    actual_date = df_sale["Date"].iloc[-len(canslim_score):]
    
    evaluate_values = [helper_cs.EvaluateCanslimScore(i) for i in canslim_score]
    if redraw:
        return {
            'actual_date': actual_date.tolist(),
            'canslim_score': canslim_score,
            'custom_data': evaluate_values
        }
    else:
        # Create the Canslim Score Plot
        fig = Figure()
        fig.add_trace(
            Scatter(
                x=actual_date,
                y=canslim_score,
                name='',
                line=dict(color='#1f77b4', width=3),
                hovertemplate='<b>%{customdata}</b>' +
                            '<br><i>Điểm</i>: %{y:.2f}',
                customdata=evaluate_values
            )
        )
        fig.update_layout(
            template='gridon',
            title={
                'text': "<b>Điểm Canslim</b>",
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis=dict(
                title='<i>Thời gian</i>',
                titlefont=dict(
                    size=11
                ),
                type='category'
            ),
            yaxis=dict(
                title='<i>Giá trị</i>',
                titlefont=dict(
                    size=11
                )
            ),
             margin=dict(
                l=110,  
                b=110,  
            ),
            legend_title='Legend',
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Rockwell"
            ),
            hovermode='x unified',
        )
        graph_html = plot(fig, output_type='div', include_plotlyjs=False)
        return graph_html, max_data_point

def plot_4m(sale_df,financial_df,npat_df,opc_df,data_point=None,redraw=False):
    lengths = [
        len(opc_df["opc"]),
        len(financial_df["EPS"]),
        len(financial_df["BVPS"]),
        len(financial_df["Long-term Liabilities"]),
        len(financial_df["Total Assests"]),
        len(financial_df["Owner's Equity"]),
        len(npat_df["NOPAT"]),
        len(sale_df["Sales"])
    ]

    # Find the minimum length
    min_length = min(lengths)

    # Trim each DataFrame to the minimum length
    opc = opc_df["opc"].tail(min_length).tolist()
    eps = financial_df["EPS"].tail(min_length).tolist()
    bvps = financial_df["BVPS"].tail(min_length).tolist()
    ld = financial_df["Long-term Liabilities"].tail(min_length).tolist()
    assets = financial_df["Total Assests"].tail(min_length).tolist()
    equity = financial_df["Owner's Equity"].tail(min_length).tolist()
    npat = npat_df["NOPAT"].tail(min_length).tolist()
    sales = sale_df["Sales"].tail(min_length).tolist()

    data = mx4.Data4M(sales,eps,bvps,opc,ld,npat,assets,equity)
    max_data_point = helper_mx.CountDataPoints(data)
    if data_point is None:
        data_point = max_data_point
    
    actual_date = sale_df['Date'].tail(data_point).astype(str).tolist()
    mx4_score = helper_mx.CalList4MScores(helper_mx.GetDataPoints(data,data_point))
    evaluate_values = [helper_mx.Evaluate4MScore(i) for i in mx4_score]
    if redraw:
        return {
            'actual_date': actual_date,
            'mx4_score': mx4_score,
            'custom_data': evaluate_values
        }
    else:
        fig = Figure()
        fig.add_trace(
            Scatter(
                x=actual_date,
                y=mx4_score,
                mode='markers+lines',
                name='',
                line=dict(color='#1f77b4', width=3),
                hovertemplate='<b>%{customdata}</b>' +
                            '<br><i>Điểm</i>: %{y:.2f}',
                customdata=evaluate_values
            )
        )
        fig.update_layout(
            template='gridon',
            title={
                'text': "<b>Điểm 4M</b>",
                'y':0.9,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis=dict(
                title='<i>Thời gian</i>',
                titlefont=dict(
                    size=11
                ),
                type='category'
            ),
            yaxis=dict(
                title='<i>Giá trị</i>',
                titlefont=dict(
                    size=11
                )
            ),
            margin=dict(
                l=110,  
                b=110,  
            ),
            legend_title='Legend',
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Rockwell"
            ),
            hovermode='x unified',
        )
        graph_html = plot(fig, output_type='div', include_plotlyjs=False)
        return graph_html, max_data_point

@csrf_exempt
def read_all_csv(request):
    global tickerData
    if request.method == 'POST':
        data = json.loads(request.body)
        ticker = data.get('ticker')
        tickerData = TickerData(read_files_for_ticker(ticker))
        return JsonResponse({
            "success": "True"
        })
    

@csrf_exempt
def get_ticker_chart(request):
    # FinancialReport_Q, FinancialReport_Y,NPAT_Q,NPAT_Y,Sales_Q,Sales_Y,StockPrice,opc
    global tickerData
    if request.method == 'POST':
        data = json.loads(request.body)
        ticker = data.get('ticker')
        graph_stock_pred = plot_stock_price(ticker, npat_df=tickerData.NPAT_Q, pe_df=tickerData.FinancialReport_Y, stock_df=tickerData.StockPrice)
        graph_canslim_score, cs_max_data_point = plot_canslim(df_sale=tickerData.Sales_Q,df_financialRP=tickerData.FinancialReport_Q)
        graph_4m_score, mx4_max_data_point = plot_4m(sale_df=tickerData.Sales_Y, financial_df=tickerData.FinancialReport_Y, npat_df=tickerData.NPAT_Y, opc_df=tickerData.opc)
        return JsonResponse(
            {
                'graph_stock_pred': graph_stock_pred,
                'graph_canslim_score': graph_canslim_score,
                'cs_max_data_point': cs_max_data_point,
                'graph_4m_score': graph_4m_score,
                'mx4_max_data_point': mx4_max_data_point,
            })

    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def update_canslim_point(request):
    global tickerData
    if request.method == 'POST':
        data = json.loads(request.body)
        data_point = data.get('data_point')
        update_data = plot_canslim(df_sale=tickerData.Sales_Q,df_financialRP=tickerData.FinancialReport_Q,data_point=data_point,redraw=True)
        update_dates = update_data['actual_date']
        update_canslim_point = update_data['canslim_score']
        custom_data = update_data['custom_data']
        return JsonResponse(
            {
                'update_dates': update_dates,
                'update_canslim_scores': update_canslim_point,
                'custom_data': custom_data
            })

@csrf_exempt
def update_mx4_point(request):
    global tickerData
    if request.method == 'POST':
        data = json.loads(request.body)
        data_point = data.get('data_point')
        update_data = plot_4m(sale_df=tickerData.Sales_Y,financial_df=tickerData.FinancialReport_Y,npat_df=tickerData.NPAT_Y,opc_df=tickerData.opc,data_point=data_point,redraw=True)
        update_dates = update_data['actual_date']
        update_mx4_point = update_data['mx4_score']
        custom_data = update_data['custom_data']
        return JsonResponse(
            {
                'update_dates': update_dates,
                'update_mx4_point': update_mx4_point,
                'custom_data': custom_data
            })
  
@csrf_exempt
def get_business_info(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ticker = data.get('ticker')
        url = f"https://fwtapi3.fialda.com/api/services/app/StockInfo/GetCompanyProfile?symbol={ticker}"
        header = {
                "Accept": "*/*",
                "Content-Type": "application/json",
                "User-Agent": "PostmanRuntime/7.35.0",
                "Connection": "keep-alive"
            }  
        response = requests.get(url, headers=header)
        obj = response.json()
        business_profile = obj['result']
        about = business_profile['aboutCompany']
        history = business_profile['history']
        prospect = business_profile['businessProspect']
                
        return JsonResponse(
            {
                'about': about,
                'history': history,
                'prospect': prospect
            })

@csrf_exempt
def get_financial_report(request):
    if request.method == 'GET':
        graph_html_eps = plot_chart_eps()
        graph_html_lnst = plot_chart_lnst()
        graph_html_fed = plot_chart_fed()
        
        return JsonResponse({
            'graph_html_eps': graph_html_eps, 
            'graph_html_lnst': graph_html_lnst, 
            'graph_html_fed': graph_html_fed,
        })

@csrf_exempt
def get_rate_table(request):
    global tickerData
    if request.method == 'POST':
        frqDF = tickerData.FinancialReport_Q.copy()
        npatDF = tickerData.NPAT_Q.copy()
        npatDF['NOPAT'] *= 1e9
        saleDF = tickerData.Sales_Q
        
        dropdown_json = get_dropdown_rate_tbl(frqDF, npatDF, saleDF)
        
        frqDF = frqDF[["Duration", "EPS"]]
        convert_format = lambda x: re.sub(r"(\d+) - Q(\d+)", r"Q\2/\1", x)
        frqDF["Duration"] = frqDF["Duration"].apply(convert_format)
        yearsFrq, resfrqDF = fmt.FormatRateDF(frqDF)
        resfrqDF = fmt.SplitRateDF(resfrqDF, yearsFrq[-1])
        jsonfrq = fmt.FormatRateTable(resfrqDF)
        
        yearsNpat, resNpatDF = fmt.FormatRateDF(npatDF)
        resNpatDF = fmt.SplitRateDF(resNpatDF, yearsNpat[-1])
        jsonNpat = fmt.FormatRateTable(resNpatDF)
        
        saleDF["Sales"] = saleDF["Sales"].astype(float)
        yearsSales, resSaleDF = fmt.FormatRateDF(saleDF)
        resSaleDF = fmt.SplitRateDF(resSaleDF, yearsSales[-1])
        jsonSale = fmt.FormatRateTable(resSaleDF)
        
        return JsonResponse(
            {
                "dropdown_json": dropdown_json,
                "frq_years": jsonfrq[0],
                "frq_data": jsonfrq[1],
                "npat_years": jsonNpat[0],
                "npat_data": jsonNpat[1],
                "sales_years": jsonSale[0],
                "sales_data": jsonSale[1],
            }, safe=False)
        
def get_dropdown_rate_tbl(frqDF, npatDF, saleDF):
    frqDF = frqDF[["Duration", "EPS"]]
    convert_format = lambda x: re.sub(r"(\d+) - Q(\d+)", r"Q\2/\1", x)
    frqDF["Duration"] = frqDF["Duration"].apply(convert_format)
    
    yearsFrq, _ = fmt.FormatRateDF(frqDF)
    
    yearsNpat, _ = fmt.FormatRateDF(npatDF)
    
    yearsSales, _ = fmt.FormatRateDF(saleDF)
    return{
            "yearsFrq": yearsFrq.tolist(),
            "yearsNpat": yearsNpat.tolist(),
            "yearsSales": yearsSales.tolist(),
        }
  
@csrf_exempt  
def filter_data_tbl(request):
    global tickerData
    if request.method == 'POST':
        frqDF = tickerData.FinancialReport_Q
        npatDF = tickerData.NPAT_Q.copy()
        npatDF['NOPAT'] *= 1e9
        saleDF = tickerData.Sales_Q

        data = json.loads(request.body)
        btnId = data.get('btnId')
        selectedYear = data.get('selectedYear')
        
        if btnId == 'dropdownEPS':
            frqDF = frqDF[["Duration", "EPS"]]
            convert_format = lambda x: re.sub(r"(\d+) - Q(\d+)", r"Q\2/\1", x)
            frqDF["Duration"] = frqDF["Duration"].apply(convert_format)
            yearsFrq, resfrqDF = fmt.FormatRateDF(frqDF)
            resfrqDF = fmt.SplitRateDF(resfrqDF, selectedYear)
            jsonData = fmt.FormatRateTable(resfrqDF)
        elif btnId == 'dropdownNpat':
            yearsNpat, resNpatDF = fmt.FormatRateDF(npatDF)
            resNpatDF = fmt.SplitRateDF(resNpatDF, selectedYear)
            jsonData = fmt.FormatRateTable(resNpatDF)
            
        elif btnId == 'dropdownSales':
            yearsSales, resSaleDF = fmt.FormatRateDF(saleDF)
            resSaleDF = fmt.SplitRateDF(resSaleDF, selectedYear)
            jsonData = fmt.FormatRateTable(resSaleDF)
        
        return JsonResponse(
            {
                "years": jsonData[0],
                "data": jsonData[1]
            })

@csrf_exempt 
def get_balance_sheet(request):
    global tickerData
    if request.method == "POST":
        balance_sheet = tickerData.balanceSheet
        
        time, bsDF = fmt.FormatBSDF(balance_sheet)
        bsDF = fmt.SplitBSDF(bsDF, time[-1])
        bsDF[time[-1]] = bsDF[time[-1]].astype(float) 
        bsDF["Color"] = bsDF["Color"].astype(float)
        jsonData = fmt.FormatBSTable(bsDF)
        
        return JsonResponse(
            {
                "years": time,
                "data": jsonData,
            }, safe=False)
   
@csrf_exempt      
def filter_balance_sheet(request):
    global tickerData
    if request.method == 'POST':
        data = json.loads(request.body)
        selectedYear = data.get('selectedYear')
        time, bsDF = fmt.FormatBSDF(tickerData.balanceSheet)
        bsDF = fmt.SplitBSDF(bsDF, selectedYear)
        bsDF[selectedYear] = bsDF[selectedYear].astype(float) 
        bsDF["Color"] = bsDF["Color"].astype(float)
        jsonData = fmt.FormatBSTable(bsDF)
        
        return JsonResponse(
            {
                "data": jsonData
            })

@csrf_exempt      
def get_operation_result(request):
    global tickerData
    if request.method == "POST":
        operation_result = tickerData.businessOperationResult
        money_exchange = tickerData.moneyExchange
        
        yearsBR, brDF = fmt.FormatBRDF(operation_result, money_exchange, True)
        resBRDF = fmt.SplitBRDF(brDF, yearsBR[-1])
        jsonBR = fmt.FormatBRTable(resBRDF)

        return JsonResponse(
            {
                "dropdown_json": yearsBR,
                "years": jsonBR[0],
                "data": jsonBR[1],
            },
            safe=False,
        )
        
@csrf_exempt      
def filter_operation_result(request):
    global tickerData
    if request.method == 'POST':
        data = json.loads(request.body)
        selectedYear = data.get('selectedYear')
        
        yearsBR, brDF = fmt.FormatBRDF(
            tickerData.businessOperationResult, tickerData.moneyExchange, False
        )
        resBRDF = fmt.SplitBRDF(brDF, selectedYear)
        jsonBR = fmt.FormatBRTable(resBRDF)

        return JsonResponse({"years": jsonBR[0], "data": jsonBR[1]})
        
@csrf_exempt      
def get_financial_fig(request):
    if request.method == "POST":
        tickersData = []
        tickerNames = []
        
        df = pd.read_csv(f'main/static/data/tickers.csv', header=None)
        df.columns = ['short_name', 'full_name','outstanding_share', 'pe_avg_industry']
        tickers = df.to_dict('records')
        for ticker in tickers:
            tickerNames.append(ticker["short_name"])
            tickersData.append(TickerData(read_files_for_ticker(ticker["short_name"])))
        
        time = fmt.GetFIOptions(tickersData)
        jsonff = fmt.FormatFITable(tickersData, tickerNames, time[-1])
        
        return JsonResponse(
            {
                "data": jsonff,
                "dropdown_json": time,
                "stocks": tickerNames
            }, safe=False)
        
@csrf_exempt      
def filter_financial_fig(request):
    global tickerData
    if request.method == 'POST':
        data = json.loads(request.body)
        selectedQuarter = data.get('selectedQuarter')
        
        tickersData = []
        tickerNames = []
        df = pd.read_csv(f'main/static/data/tickers.csv', header=None)
        df.columns = ['short_name', 'full_name','outstanding_share', 'pe_avg_industry']
        tickers = df.to_dict('records')
        for ticker in tickers:
            tickerNames.append(ticker["short_name"])
            tickersData.append(TickerData(read_files_for_ticker(ticker["short_name"])))
        
        jsonff = fmt.FormatFITable(tickersData, tickerNames, selectedQuarter)
        
        return JsonResponse(
            {
                "data": jsonff,
                "stocks": tickerNames
            })

def home(request):
    df = pd.read_csv(f'main/static/data/tickers.csv', header=None)
    df.columns = ['short_name', 'full_name','outstanding_share', 'pe_avg_industry']
    tickers = df.to_dict('records')
    
    # await trainModelAsync(tickers)
    return render(request, "home.html", {
        'tickers': tickers
    })
