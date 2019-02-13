import pandas as pd
import numpy as np
import copy
import datetime as dt
import xlrd

price_dir_path = "blog/stock_price"

status_file_path = "blog/株式ステータス.xls"
status_df = pd.read_excel(status_file_path).set_index("コード")

def get_one_class_data(original_df, classification_column, class_name): #数値で分ける機能消した
    class_series = original_df[classification_column]
    df = original_df[class_series==class_name]
    return df

def get_market_codes(market):
    return list(get_one_class_data(status_df, "市場・商品区分", market).index)

def read_prices(code, year=None, show_date=False, candle=False): #一回スタートエンド廃止
    none = pd.Series()
    try: #データを検索
        csv_file_path = "{}/{}.csv".format(price_dir_path, code)
        if candle == True:
            name, usecol = None, [0,5]
        elif candle == False:
            name, usecol = ['Adj Close'], None
        data = pd.read_csv(csv_file_path, index_col=0, names=['Adj Close'], usecols=None)
        data.index.name = "Date"
        series = pd.Series(data['Adj Close'], index=data.index)
    except FileNotFoundError: #無ければnoneを返す
        return none

    if year == "latest":
        year = dt.date.today().year - 1
    if year != None:
        start = dt.date(int(year),1,1)
        end = dt.date(int(year),12,31)

    first, last = list(data.index)[0], list(data.index)[-1]#デフォルトにしたい
    first = dt.date(int(first[:4]), int(first[5:7]), int(first[-2:])) #存在する最初と最後の日の処理
    last = dt.date(int(last[:4]), int(last[5:7]), int(last[-2:]))

    if start > last: #開始が遅すぎるときにnoneを返す
        return none
    if first > end: #終了が早すぎるときにnoneを返す
        return none

    real_start, real_end = None, None
    while real_start == None: #実際にある開始と終了が見つかるまで探す
        start_index = "{}-".format(start.year) + "%02d"%start.month + "-%02d"%start.day
        if start_index in data.index:
            real_start = start_index
        else:
            start = start + dt.timedelta(days=1)
    while real_end == None:
        end_index = "{}-".format(end.year) + "%02d"%end.month + "-%02d"%end.day
        if end_index in data.index:
            real_end = end_index
        else:
            end = end - dt.timedelta(days=1)
    if show_date == True:
        print("開始：{} 終了：{}".format(real_start, real_end))
    return series[real_start:real_end]

def get_change_rate(stock_prices):
    try:
        first = stock_prices[0]
        last = stock_prices[-1]
        rate = (last/first - 1)*100
        return rate
    except:
        return np.nan

def get_max_change_rate(stock_prices):
    try:
        s = stock_prices.reset_index(drop=True)
        if s[s==max(s)].index[0] > s[s==min(s)].index[0]:
            rate = (max(s)/min(s)-1)*100
        elif s[s==max(s)].index[0] < s[s==min(s)].index[0]:
            rate = (min(s)/max(s)-1)*100
        else:
            rate = 0
        return rate
    except:
        return np.nan

def judge_up_down(stock_prices):
    change_rate = get_change_rate(stock_prices)
    try:
        if change_rate > 0:
            return "上昇"
        elif change_rate < 0:
            return "下落"
        else:
            return "一定"
    except:
        return np.nan

def scan_variables(column_list, stock_prices, about): #アプリならスキャン制は非効率かも
    if "騰落率（％）" in column_list:
        column_list[column_list.index("騰落率（％）")] = get_change_rate(stock_prices)
    if "最大変動率（％）" in column_list:
        column_list[column_list.index("最大変動率（％）")] = get_max_change_rate(stock_prices)
    if "カウント" in column_list:
        column_list[column_list.index("カウント")] = 1
    if "上昇or下落" in column_list:
        column_list[column_list.index("上昇or下落")] = judge_up_down(stock_prices)
    if about == True:
        for data in column_list:
            try:
                column_list[column_list.index(data)] = np.round(data, decimals=1)
            except:
                pass

def scan_statuses(column_list, code):
    for column in column_list:
        if column in status_df.columns:
            column_list[column_list.index(column)] = status_df[column][code]

def scan_report_data(column_list, report):
    for column in column_list:
        if column in report.index:
            column_list[column_list.index(column)] = report.loc[column]

def get_multiple_data(codes, column_list, year=None, about=False, p=True, r=False, s=False):
    df = pd.DataFrame(columns=["銘柄名"]+column_list)
    for code in codes:
        data_list = copy.deepcopy(column_list)
        if p == True:
            prices = read_prices(code, year)
            scan_variables(data_list, prices, about)
        if r == True:
            report = read_one_year_report(code, year)
            scan_report_data(data_list, report)
        if s == True:
            scan_statuses(data_list, code)
        code = int(code)
        try:
            name = status_df["銘柄名"][code]
        except:
            name = "データなし"
        series = pd.Series([name]+data_list, ["銘柄名"]+column_list)
        df.loc[code] = series
    return df

def get_historical_data(codes, column, start_year, end_year, about=False):
    df = pd.DataFrame(columns=["銘柄名"]+list(range(start_year, end_year+1)))
    for code in codes:
        series = pd.Series(index=range(start_year, end_year+1))
        code = int(code)
        series["銘柄名"] = status_df["銘柄名"][code]
        for year in range(start_year, end_year+1):
            prices = read_prices(code, year)
            data_list = copy.deepcopy([column])
            scan_variables(data_list, prices, about)
            series[year] = data_list[0]
        df.loc[code] = series
    return df

def get_average(df, column_name):
    series = df[column_name]
    number_list = [data for data in series if type(data) == float or type(data) == int] #簡単な抽出法調べる
    average = np.nanmean(number_list)
    return average

def get_sum(df, column_name):
    series = df[column_name]
    number_list = [data for data in series if type(data) == float or type(data) == int] #簡単な抽出法調べる
    sum = np.nansum(number_list)
    return sum

def get_proportion(df, column_name, hit_class):
    series = df[column_name]
    if len(series) == 0:
        return 0
    hit_series = df.loc[series==hit_class, column_name]
    proportion = len(hit_series)/len(series)*100
    return proportion

def scan_class_variables(df, column_list, about):
    if "平均騰落率（％）" in column_list:
        column_list[column_list.index("平均騰落率（％）")] = get_average(df, "騰落率（％）")
    if "企業数（社）" in column_list:
        column_list[column_list.index("企業数（社）")] = get_sum(df, "カウント")
    if "上昇株割合（％）" in column_list:
        column_list[column_list.index("上昇株割合（％）")] = get_proportion(df, "上昇or下落", "上昇")
    if about == True:
        for data in column_list:
            try:
                column_list[column_list.index(data)] = np.round(data, decimals=1)
            except:
                pass

def convert_number_into_class(codes, classification_column, source_df, border_list):
    border_list.sort(reverse=True)
    class_list =["{}以上".format(border_list[0])]+["{}以上{}未満".format(border_list[i+1], border_list[i]) for i in range(len(border_list)-1)]+["{}未満".format(border_list[-1])]
    for code in codes:
        data = source_df.loc[code,classification_column]
        if np.isnan(data):
            continue
        if data >= border_list[0]:
            source_df.loc[code,classification_column] = class_list[0]
            continue
        i = 0
        for i in range(len(border_list)-1):
            if data < border_list[i]:
                source_df.loc[code,classification_column] = class_list[i+1]
    return class_list

def compare_class_data(codes, classification_column, column_list, year=None, start=None, end=None, border_list=None, about=True, output=False):
    column_dict = {"平均騰落率（％）":"騰落率（％）", #元となるデータフレームを作成
                   "企業数（社）":"カウント",
                   "上昇株割合（％）":"上昇or下落"}
    pre_list = [classification_column] + [column_dict[column] for column in column_list]
    pre_list = sorted(set(pre_list), key= pre_list.index)
    source_df = get_multiple_data(codes, pre_list, year, start, end, about=False)

    class_series = source_df[classification_column]  #クラスを作成
    if border_list == None:
        class_list = list(set(class_series))
    else:
        class_list = convert_number_into_class(codes, classification_column, source_df, border_list)
    class_series = source_df[classification_column]

    df = pd.DataFrame(columns=column_list) #クラスごとにデータフレームを作成し、クラス名と出力した変数群を最終データフレームへ納める
    for class_label in class_list:
        one_class_df = source_df[class_series==class_label]
        data_list = copy.deepcopy(column_list)
        scan_class_variables(one_class_df, data_list, about)
        df.loc[class_label] = data_list
    df.index.name = classification_column
    df.name = "{}から{}までの{}での比較".format(start, end, classification_column)
    if output == True:
        df.to_excel("{}\\{}.xls".format(document_path, df.name))
    return df

#start, end = "2017-11-11", "2018-11-11"
#compare_class_data(mam, "最大変動率（％）", ["企業数（社）","上昇株割合（％）","平均騰落率（％）"], 2018, border_list= [150, 100, 0, -75, -50])
#get_multiple_data(jg, ["騰落率（％）"], 2013)
