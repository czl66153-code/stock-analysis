# -*- coding: utf-8 -*-
"""
股票数据云函数
使用akshare获取A股数据
"""

import json
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# 全局安装依赖（冷启动时执行一次）
def install_packages():
    import sys
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "akshare", "-q", "--break-system-packages"])

def main(event, context):
    """云函数入口"""
    
    # 安装依赖（首次运行）
    try:
        import akshare as ak
    except ImportError:
        logger.info("Installing akshare...")
        install_packages()
        import akshare as ak
    
    # 获取请求参数
    path_params = event.get("pathParameters", {})
    stock_code = path_params.get("stockcode", "")
    query_params = event.get("queryStringParameters", {}) or {}
    start_date = query_params.get("start", "20240101")
    end_date = query_params.get("end", datetime.now().strftime("%Y%m%d"))
    
    logger.info(f"Request: stock={stock_code}, start={start_date}, end={end_date}")
    
    try:
        # 转换代码格式 (sh600519 -> 600519, sz000001 -> 000001)
        symbol = stock_code
        if symbol.startswith('sh'):
            symbol = symbol[2:]
        elif symbol.startswith('sz'):
            symbol = symbol[2:]
        
        # 获取股票名称
        stock_info = ak.stock_individual_info_em(symbol=symbol)
        name = "未知"
        for _, row in stock_info.iterrows():
            if row['item'] == '股票名称':
                name = row['value']
                break
        
        # 获取K线数据
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            start_date=start_date.replace('-', ''),
            end_date=end_date.replace('-', ''),
            adjust="qfq"  # 前复权
        )
        
        # 转换数据格式
        data = []
        for _, row in df.iterrows():
            data.append({
                "date": str(row['日期']),
                "open": float(row['开盘']),
                "high": float(row['最高']),
                "low": float(row['最低']),
                "close": float(row['收盘']),
                "volume": float(row['成交量']),
                "amount": float(row['成交额'])
            })
        
        # 最新数据
        latest = df.iloc[-1]
        info = {
            "code": symbol,
            "name": name,
            "latestPrice": float(latest['收盘']),
            "change": float(latest['涨跌幅']),
            "volume": float(latest['成交量']),
            "amount": float(latest['成交额']),
            "high": float(latest['最高']),
            "low": float(latest['最低'])
        }
        
        logger.info(f"Success: {len(data)} records, latest price: {info['latestPrice']}")
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "code": 0,
                "data": data,
                "info": info
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "code": 1,
                "error": str(e)
            }, ensure_ascii=False)
        }
