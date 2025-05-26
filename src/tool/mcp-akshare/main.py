#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AKShare MCP Server

这是一个基于AKShare的股票数据MCP服务器，使用FastMCP框架构建。
它提供了对中国股票市场数据的访问，通过MCP协议暴露AKShare的API。
"""

import akshare as ak
import pandas
from fastmcp import FastMCP
import datetime

MAX_DATA_ROW = 50

# 创建MCP服务器实例
mcp = FastMCP("AKShare股票数据服务", dependencies=["akshare>=1.16.76"])
# 工具函数：获取当前时间
@mcp.tool()
def get_current_time() -> dict:
    """获取当前时间
    
    获取当前时间数据
    
    Returns:
        dict: 包含当前时间的字典
    """
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"current_time": current_time}

# 工具函数：上海证券交易所股票数据总貌
@mcp.tool()
def stock_sse_summary() -> dict:
    """获取上海证券交易所-股票数据总貌
    
    数据来源: 上海证券交易所-市场数据-股票数据总貌
    网址: http://www.sse.com.cn/market/stockdata/statistic/
    
    Returns:
        dict: 包含上海证券交易所股票数据总貌的字典
    """
    result = ak.stock_sse_summary()
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]

    return result.to_dict(orient="records")
# 工具函数：深圳证券交易所证券类别统计
@mcp.tool()
def stock_szse_summary(date: str) -> dict:
    """获取深圳证券交易所-市场总貌-证券类别统计
    
    数据来源: 深圳证券交易所-市场总貌
    网址: http://www.szse.cn/market/overview/index.html
    
    Args:
        date: 统计日期，格式为YYYYMMDD，如"20200619"
        
    Returns:
        dict: 包含证券类别统计数据的字典，包括数量、成交金额、总市值和流通市值
    """
    result = ak.stock_szse_summary(date=date)
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")

# 工具函数：深圳证券交易所地区交易排序
@mcp.tool()
def stock_szse_area_summary(date: str) -> dict:
    """获取深圳证券交易所-市场总貌-地区交易排序
    
    数据来源: 深圳证券交易所-市场总貌
    网址: http://www.szse.cn/market/overview/index.html
    
    Args:
        date: 统计年月，格式为YYYYMM，如"202203"
        
    Returns:
        dict: 包含地区交易排序数据的字典，包括序号、地区、各类交易额及占比
    """
    result = ak.stock_szse_area_summary(date=date)
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")

# 工具函数：深圳证券交易所股票行业成交数据
@mcp.tool()
def stock_szse_sector_summary(symbol: str, date: str) -> dict:
    """获取深圳证券交易所-统计资料-股票行业成交数据
    
    数据来源: 深圳证券交易所-统计资料
    网址: http://docs.static.szse.cn/www/market/periodical/month/W020220511355248518608.html
    
    Args:
        symbol: 统计周期，可选值: "当月" 或 "当年"
        date: 统计年月，格式为YYYYMM，如"202501"
        
    Returns:
        dict: 包含股票行业成交数据的字典，包括交易天数、成交金额、成交股数、成交笔数等
    """
    result = ak.stock_szse_sector_summary(symbol=symbol, date=date)
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")

# 工具函数：风险警示板股票行情
@mcp.tool()
def stock_zh_a_st_em() -> dict:
    """获取风险警示板股票行情数据
    
    数据来源: 东方财富网-行情中心-沪深个股-风险警示板
    网址: https://quote.eastmoney.com/center/gridlist.html#st_board
    
    Returns:
        dict: 包含风险警示板股票行情数据的字典，包括代码、名称、最新价、涨跌幅等完整行情指标
    """
    result = ak.stock_zh_a_st_em()
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")

# 工具函数：新股行情数据
@mcp.tool()
def stock_zh_a_new_em() -> dict:
    """获取新股板块股票行情数据
    
    数据来源: 东方财富网-行情中心-沪深个股-新股
    网址: https://quote.eastmoney.com/center/gridlist.html#newshares
    
    Returns:
        dict: 包含新股板块股票行情数据的字典，包括代码、名称、最新价、涨跌幅等完整行情指标
    """
    result = ak.stock_zh_a_new_em()
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")

# 工具函数：新股上市首日数据
@mcp.tool()
def stock_xgsr_ths() -> dict:
    """获取新股上市首日数据
    
    数据来源: 同花顺-数据中心-新股数据-新股上市首日
    网址: https://data.10jqka.com.cn/ipo/xgsr/
    
    Returns:
        dict: 包含新股上市首日数据的字典，包括发行价、首日价格表现、涨跌幅及破发情况
    """
    result = ak.stock_xgsr_ths()
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")

# 工具函数：科创板股票历史行情数据
@mcp.tool()
def stock_zh_kcb_daily(symbol: str, adjust: str = "") -> dict:
    """获取科创板股票历史行情数据
    
    数据来源: 新浪财经-科创板股票
    示例网址: https://finance.sina.com.cn/realstock/company/sh688001/nc.shtml
    
    Args:
        symbol: 带市场标识的股票代码，如"sh688008"
        adjust: 复权类型，可选值: 
               ""(默认): 不复权
               "qfq": 前复权
               "hfq": 后复权
               "hfq-factor": 后复权因子
               "qfq-factor": 前复权因子
        
    Returns:
        dict: 包含科创板股票历史行情数据的字典，包括日期、价格、成交量等
    """
    result = ak.stock_zh_kcb_daily(symbol=symbol, adjust=adjust)
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")

# 工具函数：A+H股历史行情数据
@mcp.tool()
def stock_zh_ah_daily(symbol: str, start_year: str, end_year: str, adjust: str = "") -> dict:
    """获取A+H股历史行情数据
    
    数据来源: 腾讯财经-A+H股数据
    示例网址: https://gu.qq.com/hk02359/gp
    
    Args:
        symbol: 港股股票代码，如"02318"(可通过ak.stock_zh_ah_name()获取)
        start_year: 开始年份，如"2000"
        end_year: 结束年份，如"2019"
        adjust: 复权类型，可选值: 
               ""(默认): 不复权
               "qfq": 前复权
               "hfq": 后复权
        
    Returns:
        dict: 包含A+H股历史行情数据的字典，包括日期、价格、成交量等
    """
    result = ak.stock_zh_ah_daily(symbol=symbol, start_year=start_year, end_year=end_year, adjust=adjust)
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")

# 工具函数：美股历史行情数据
@mcp.tool()
def stock_us_hist(symbol: str, period: str = "daily", start_date: str = "", end_date: str = "", adjust: str = "") -> dict:
    """获取美股历史行情数据
    
    数据来源: 东方财富网-美股
    示例网址: https://quote.eastmoney.com/us/ENTX.html#fullScreenChart
    
    Args:
        symbol: 美股代码(可通过ak.stock_us_spot_em()获取)
        period: 时间周期，可选值: 'daily'(日线), 'weekly'(周线), 'monthly'(月线)
        start_date: 开始日期，格式为YYYYMMDD，如"20210101"
        end_date: 结束日期，格式为YYYYMMDD，如"20210601"
        adjust: 复权类型，可选值: 
               ""(默认): 不复权
               "qfq": 前复权
               "hfq": 后复权
        
    Returns:
        dict: 包含美股历史行情数据的字典，包括日期、价格、成交量等
    """
    result = ak.stock_us_hist(symbol=symbol, period=period, start_date=start_date, end_date=end_date, adjust=adjust)
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")

# 工具函数：美股分时行情数据
@mcp.tool()
def stock_us_hist_min_em(symbol: str, start_date: str = "1979-09-01 09:32:00", end_date: str = "2222-01-01 09:32:00") -> dict:
    """获取美股分时行情数据
    
    数据来源: 东方财富网-美股分时行情
    示例网址: https://quote.eastmoney.com/us/ATER.html
    
    Args:
        symbol: 美股代码(可通过ak.stock_us_spot_em()获取)，如"105.ATER"
        start_date: 开始日期时间，格式为"YYYY-MM-DD HH:MM:SS"，默认"1979-09-01 09:32:00"
        end_date: 结束日期时间，格式为"YYYY-MM-DD HH:MM:SS"，默认"2222-01-01 09:32:00"
        
    Returns:
        dict: 包含美股分时行情数据的字典，包括时间、价格、成交量等
    """
    result = ak.stock_us_hist_min_em(symbol=symbol, start_date=start_date, end_date=end_date)
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")

# 工具函数：A股分时行情数据
@mcp.tool()
def stock_bid_ask_em(symbol: str) -> dict:
    """获取A股分时行情数据
    
    数据来源: 东方财富-股票行情报价
    示例网址: https://quote.eastmoney.com/sz000001.html
    
    Args:
        symbol: 股票代码，如"000001"
        
    Returns:
        dict: 包含股票行情报价数据的字典，包括买卖盘口等详细信息
    """
    result = ak.stock_bid_ask_em(symbol=symbol)
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")
# 工具函数：港股分时行情数据
@mcp.tool()
def stock_hk_hist_min_em(symbol: str, period: str = "5", adjust: str = "", 
                        start_date: str = "1979-09-01 09:32:00", 
                        end_date: str = "2222-01-01 09:32:00") -> dict:
    """获取港股分时行情数据
    
    数据来源: 东方财富网-港股分时行情
    示例网址: http://quote.eastmoney.com/hk/00948.html
    
    Args:
        symbol: 港股代码(可通过ak.stock_hk_spot_em()获取)，如"01611"
        period: 时间周期，可选值: '1'(1分钟), '5'(5分钟), '15'(15分钟), '30'(30分钟), '60'(60分钟)
        adjust: 复权类型，可选值: 
               ""(默认): 不复权
               "qfq": 前复权
               "hfq": 后复权
        start_date: 开始日期时间，格式为"YYYY-MM-DD HH:MM:SS"，默认"1979-09-01 09:32:00"
        end_date: 结束日期时间，格式为"YYYY-MM-DD HH:MM:SS"，默认"2222-01-01 09:32:00"
        
    Returns:
        dict: 包含港股分时行情数据的字典，包括时间、价格、成交量等
    """
    result = ak.stock_hk_hist_min_em(symbol=symbol, period=period, adjust=adjust,
                                   start_date=start_date, end_date=end_date)
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")

# 工具函数：上市公司主营构成
@mcp.tool()
def stock_zygc_em(symbol: str) -> dict:
    """获取上市公司主营构成数据
    
    数据来源: 东方财富网-个股-主营构成
    示例网址: https://emweb.securities.eastmoney.com/PC_HSF10/BusinessAnalysis/Index?type=web&code=SH688041
    
    Args:
        symbol: 带市场标识的股票代码，如"SH688041"(上海)或"SZ000001"(深圳)
        
    Returns:
        dict: 包含公司主营构成数据的字典，包括收入、成本、利润及比例等财务指标
    """
    result = ak.stock_zygc_em(symbol=symbol)
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")

# 工具函数：主力控盘与机构参与度
@mcp.tool()
def stock_comment_detail_zlkp_jgcyd_em(symbol: str) -> dict:
    """获取股票主力控盘与机构参与度数据
    
    数据来源: 东方财富网-数据中心-特色数据-千股千评
    示例网址: https://data.eastmoney.com/stockcomment/stock/600000.html
    
    Args:
        symbol: 股票代码，如"600000"
        
    Returns:
        dict: 包含主力控盘和机构参与度数据的字典，机构参与度单位为%
    """
    result = ak.stock_comment_detail_zlkp_jgcyd_em(symbol=symbol)
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")

# 工具函数：个股新闻资讯
@mcp.tool()
def stock_news_em(symbol: str) -> dict:
    """获取个股新闻资讯数据
    
    数据来源: 东方财富-个股新闻
    网址: https://so.eastmoney.com/news/s
    
    Args:
        symbol: 股票代码或关键词，如"300059"
        
    Returns:
        dict: 包含个股新闻资讯的字典，包括标题、内容、发布时间等
    """
    result = ak.stock_news_em(symbol=symbol)
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")

# 工具函数：财经内容精选
@mcp.tool()
def stock_news_main_cx() -> dict:
    """获取财新网财经内容精选数据
    
    数据来源: 财新网-财新数据通
    网址: https://cxdata.caixin.com/pc/
    
    Returns:
        dict: 包含财经内容精选的字典，包括标签、摘要、发布时间等
    """
    result = ak.stock_news_main_cx()
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")

# 工具函数：个股资金流数据
@mcp.tool()
def stock_fund_flow_individual(symbol: str) -> dict:
    """获取个股资金流数据
    
    数据来源: 同花顺-数据中心-资金流向
    网址: https://data.10jqka.com.cn/funds/ggzjl/#refCountId=data_55f13c2c_254
    
    Args:
        symbol: 时间周期，可选值: 
               "即时"(默认), 
               "3日排行", 
               "5日排行", 
               "10日排行", 
               "20日排行"
        
    Returns:
        dict: 包含个股资金流数据的字典，包括流入流出资金、净额等
    """
    result = ak.stock_fund_flow_individual(symbol=symbol)
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")

# 工具函数：雪球股票热度关注排行榜
@mcp.tool()
def stock_hot_follow_xq(symbol: str) -> dict:
    """获取雪球股票热度关注排行榜数据
    
    数据来源: 雪球-沪深股市-热度排行榜
    网址: https://xueqiu.com/hq
    
    Args:
        symbol: 排行类型，可选值: 
               "最热门"(默认), 
               "本周新增"
        
    Returns:
        dict: 包含股票热度关注数据的字典，包括关注人数、最新价等
    """
    result = ak.stock_hot_follow_xq(symbol=symbol)
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")

# 工具函数：百度热搜股票数据
@mcp.tool()
def stock_hot_search_baidu(symbol: str, date: str, time: str) -> dict:
    """获取百度热搜股票数据
    
    数据来源: 百度股市通-热搜股票
    网址: https://gushitong.baidu.com/expressnews
    
    Args:
        symbol: 市场类型，可选值: 
               "A股"(默认), 
               "全部", 
               "港股", 
               "美股"
        date: 查询日期，格式为YYYYMMDD，如"20230421"
        time: 时间周期，可选值: 
              "今日"(默认), 
              "1小时"
        
    Returns:
        dict: 包含热搜股票数据的字典，包括股票名称、涨跌幅、所属板块等
    """
    result = ak.stock_hot_search_baidu(symbol=symbol, date=date, time=time)
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")

# 工具函数：富途牛牛快讯数据
@mcp.tool()
def stock_info_global_futu() -> dict:
    """获取富途牛牛快讯数据
    
    数据来源: 富途牛牛-快讯
    网址: https://news.futunn.com/main/live
    
    Returns:
        dict: 包含最近50条快讯数据的字典，包括标题、内容、发布时间等
    """
    result = ak.stock_info_global_futu()
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")
# 工具函数：A+H股实时行情数据
@mcp.tool()
def stock_zh_ah_spot() -> dict:
    """获取A+H股实时行情数据
    
    数据来源: 腾讯财经-A+H股数据
    网址: https://stockapp.finance.qq.com/mstats/#mod=list&id=hk_ah&module=HK&type=AH
    
    Returns:
        dict: 包含所有A+H上市公司实时行情数据的字典，包括代码、名称、价格、成交量等
    """
    result = ak.stock_zh_ah_spot()
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")

# 工具函数：科创板实时行情数据
@mcp.tool()
def stock_zh_kcb_spot() -> dict:
    """获取科创板实时行情数据
    
    数据来源: 新浪财经-科创板
    网址: http://vip.stock.finance.sina.com.cn/mkt/#kcb
    
    Returns:
        dict: 包含所有科创板上市公司实时行情数据的字典，包括代码、价格、成交量、市值等
    """
    result = ak.stock_zh_kcb_spot()
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")

# 工具函数：美股实时行情数据
@mcp.tool()
def stock_us_spot_em() -> dict:
    """获取美股实时行情数据
    
    数据来源: 东方财富网-美股
    网址: https://quote.eastmoney.com/center/gridlist.html#us_stocks
    
    Returns:
        dict: 包含所有美股上市公司实时行情数据的字典，包括代码、价格、成交量、市值等
    """
    result = ak.stock_us_spot_em()
    if type(result) is pandas.core.frame.DataFrame:
        result = result[:min(MAX_DATA_ROW, len(result))]
    return result.to_dict(orient="records")

def main():
    mcp.run()

# 主函数
if __name__ == "__main__":
    main()
