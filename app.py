from numpy import mod
import streamlit as st
import pandas as pd
import datetime
from name import companyinfo
import matplotlib.pyplot as plt
from selenium import webdriver
import plotly.figure_factory as ff
import cufflinks as cf
import os.path
import time
import webbrowser

cf.set_config_file(theme='pearl',sharing='public',offline=True, world_readable=True)
# dimensions=(900,1500)

if 'key' not in st.session_state:
    st.session_state.key = set()

nbMonth = 6
nbDays = 6 * 30
# App title
st.markdown('''
# Price App
Shown are the price data for query companies!

**Credits**
- App built by [Tung DAO]()
- Built in `Python` using `streamlit`
''')
st.write('---')
# Sidebar
st.sidebar.subheader('Query parameters')
today = datetime.date.today()
passDays = datetime.timedelta(nbDays)

start_date = st.sidebar.date_input("Start date", today - passDays)
end_date = st.sidebar.date_input("End date", today)

# def get_indicators(data):
#     # Get MACD
#     data["macd"], data["macd_signal"], data["macd_hist"] = talib.MACD(data['Close'] / 1000)

#     # Get MA20 and MA50
#     data["ma20"] = talib.MA(data["Close"] / 1000, timeperiod=20)
#     data["ma50"] = talib.MA(data["Close"] / 1000, timeperiod=50)

#     # Get RSI
#     data["rsi"] = talib.RSI(data["Close"] / 1000)
    
#      # Get A/D Line
#     data["ad"] = talib.AD(data["High"] / 1000, data["Low"] / 1000, data["Close"] / 1000, data["Volume"] / 1000000)
#     return data
def plot_chart(data, n):
    # Filter number of observations to plot
    data = data.iloc[-n:]
    # Create figure and set axes for subplots
    fig, (ax_ma, ax_rsi, ax_macd) = plt.subplots(3,1,sharex=True)
    fig.set_size_inches(1, 8)
     
    # Plot candlestick chart
    ax_ma.plot(data.index,data['Close'] / 1000, color='blue', label='Daily Close Price')
    ax_ma.plot(data.index, data["ma20"], label="MA20")
    ax_ma.plot(data.index, data["ma50"], label="MA50")

    # Plot MACD
    ax_macd.plot(data.index, data["macd"], label="macd")
    ax_macd.bar(data.index, data["macd_hist"], label="hist")
    ax_macd.plot(data.index, data["macd_signal"], label="signal")
    ax_macd.set_ylabel('MACD')
    # Plot RSI
    # Above 70% = overbought, below 30% = oversold
    ax_rsi.set_ylabel("(%)")
    ax_rsi.plot(data.index, [70] * len(data.index), label="overbought")
    ax_rsi.plot(data.index, [30] * len(data.index), label="oversold")
    ax_rsi.plot(data.index, data["rsi"], label="rsi")
    
    # Accumulation / Distribution Line
    # ax_ad.set_ylabel("(%)")
    # ax_ad.plot(data.index, data["ad"], label="ad")

    
    st.plotly_chart(fig, use_container_width=True, width= 800, height = 700)
    st.bar_chart(data["Volume"])

# @st.cache
def load_data2(ticker, start, end):
    url = 'https://finance.vietstock.vn/data/ExportTradingResult?Code={}&FromDate={}&ToDate={}&ExportType=text'.format(ticker, start, end)
    #webbrowser.open(url)
    # driver=webdriver.Chrome()
    # driver.get(url)

    # webbrowser.register('chrome',
	# None,
	# webbrowser.BackgroundBrowser("C://Program Files//Google//Chrome//Application//chrome.exe"))
    # webbrowser.get('chrome').open(url)

    downloads_dir = 'C:\\Users\\PC\Downloads\\' #os.path.expanduser("~") + "/Downloads/"
    fileNameOrigin = '{}-{}.txt'.format(ticker, str(end).replace('-',''))
    filePathOrigin = '{}{}'.format(downloads_dir,fileNameOrigin)
    text = 'Download [{ticker}]({url})'.format(ticker=ticker,url=url)
    st.markdown(text,unsafe_allow_html=True)


    uploaded_file = st.file_uploader("Choose a file")
    #if uploaded_file is not None:
        # To read file as bytes:
    #    bytes_data = uploaded_file.getvalue()
    #    st.write(bytes_data)

        # To convert to a string based IO:
       #stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
       # st.write(stringio)

     # To read file as string:
    #    string_data = stringio.read()
    #    st.write(string_data)

     # Can be used wherever a "file-like" object is accepted:
    #    dataframe = pd.read_csv(uploaded_file)
    #    st.write(dataframe)
    # while not os.path.exists (filePathOrigin):   
    #     time.sleep(1)
    #if os.path.isfile (filePathOrigin):     
    tickerDf = pd.read_csv(uploaded_file, usecols=[0,2,3,4,5,6])    
    tickerDf.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    tickerDf['date'] = pd.to_datetime(tickerDf['date'], format='%m/%d/%Y')
    tickerDf['open'] = tickerDf['open'] / 1000
    tickerDf['high'] = tickerDf['high'] /1000
    tickerDf['low'] = tickerDf['low'] /1000
    tickerDf['close'] = tickerDf['close'] / 1000
    tickerDf['volume'] = tickerDf['volume'] / 10000
    tickerDf.set_index('date', inplace=True)        
    return tickerDf     
tickerSymbol= st.sidebar.selectbox('Ticker', companyinfo.keys(),index=list(companyinfo.keys()).index('ORS')) # Select ticker symbol
tickerName = st.sidebar.text(companyinfo.get(tickerSymbol))

st.session_state.key.add(tickerSymbol)

cols = st.sidebar.columns(4)
for index, key in enumerate(st.session_state.key, start=1):
    if index % 4 == 1:
        button_start = cols[0].button(key)
        if button_start:
            tickerSymbol = key
    if index % 4 == 2:
        button_start = cols[1].button(key)
        if button_start:
            tickerSymbol = key
    if index % 4 == 3:
        button_start = cols[2].button(key)
        if button_start:
            tickerSymbol = key
    if index % 4 == 0:
        button_start = cols[3].button(key)
        if button_start:
            tickerSymbol = key
try:  
    tickerDf = load_data2(tickerSymbol, start_date, end_date)
    tickerDf = tickerDf.loc[(tickerDf.index >= pd.to_datetime(start_date)) & (tickerDf.index <= pd.to_datetime(end_date))]
    st.text('Data valid only until {}'.format(tickerDf.index[-1]))
    # # # Ticker data
    st.header('**Ticker data**')
    st.write(tickerDf.tail(121))    
    st.header('**Charts**')
    qf=cf.QuantFig(tickerDf, title='First Quant Figure',legend='top')
    # Adding a resistance level
    # qf.add_resistance(date='2021-02-17', on='close', color='orange')

    # Adding a support level
    # qf.add_support('17Sep21', on='low', color='blue')

   
    # # qf.add_dmi()
    # # Adding CCI to the figure
    # # qf.add_ema()
    # 
    # qf.add_resistance(tickerDf['date'])
    # qf.add_support(tickerDf.index)
    # qf.add_trendline()
    # qf.add_cci(periods=20, yTitle='CCI')
    qf.add_volume()
    qf.add_bollinger_bands(periods=20, boll_std=2 ,colors=['orange','grey'], fill=True)
    qf.add_sma([10,20],width=2,color=['green','lightgreen'],legendgroup=True)
    qf.add_rsi(periods=20,color='java')
    qf.add_ema(periods=10, color='blue')
    qf.add_macd()
    fig = qf.iplot(asFigure=True, up_color='green', down_color='red')    
   
    st.plotly_chart(fig) 
    
    st.write('---')
except Exception as e:
    st.text(e)
    st.header('**NO data**')    
    st.write('---')

