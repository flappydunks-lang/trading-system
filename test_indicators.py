from Trading import DataManager, TechnicalAnalyzer

symbol = 'NVDA'

df = DataManager.fetch_data(symbol, '60d', '5m')
if df is None:
    print('Failed to fetch')
else:
    ind = TechnicalAnalyzer.calculate_indicators(df)
    if ind is None:
        print('Indicator calc failed')
    else:
        print('Indicators calculated:')
        print('Price:', ind.price)
        print('EMA 8/21/34:', ind.ema_8, ind.ema_21, ind.ema_34)
        print('Williams %R:', ind.williams_r)
        print('CCI:', ind.cci)
        print('Keltner U/M/L:', ind.keltner_upper, ind.keltner_middle, ind.keltner_lower)
        print('Ichimoku Tenkan/Kijun/SenkouA/SenkouB:', ind.tenkan_sen, ind.kijun_sen, ind.senkou_a, ind.senkou_b)
