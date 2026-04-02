# -*- coding: utf-8 -*-
"""
股票数据 API 服务
使用 requests 直接调用 akshare API（无需安装 akshare）
"""

from flask import Flask, jsonify, request
import requests
import pandas as pd
from datetime import datetime
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

app = Flask(__name__)

def get_stock_data_eastmoney(symbol, start, end):
    """通过东方财富API获取股票数据"""
    # 转换代码: 600519 -> 1.600519, 000001 -> 0.000001
    if symbol.startswith('6'):
        secid = f"1.{symbol}"
    else:
        secid = f"0.{symbol}"
    
    url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "secid": secid,
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "klt": "101",  # 日K
        "fqt": "1",    # 前复权
        "beg": start.replace('-', ''),
        "end": end.replace('-', ''),
        "lmt": "1000000"
    }
    
    try:
        resp = requests.get(url, params=params, timeout=30)
        data = resp.json()
        
        if data.get('data') and data['data'].get('klines'):
            klines = data['data']['klines']
            stock_name = data['data'].get('name', symbol)
            
            result = []
            for kline in klines:
                fields = kline.split(',')
                result.append({
                    "date": fields[0],
                    "open": float(fields[1]),
                    "close": float(fields[2]),
                    "high": float(fields[3]),
                    "low": float(fields[4]),
                    "volume": float(fields[5]),
                    "amount": float(fields[6])
                })
            
            # 最新数据
            latest = result[-1]
            prev_close = result[-2]['close'] if len(result) > 1 else latest['close']
            change = (latest['close'] - prev_close) / prev_close * 100
            
            return {
                "code": 0,
                "data": result,
                "info": {
                    "code": symbol,
                    "name": stock_name,
                    "latestPrice": latest['close'],
                    "change": change,
                    "volume": latest['volume'],
                    "amount": latest['amount'],
                    "high": latest['high'],
                    "low": latest['low']
                }
            }
        else:
            return {"code": 1, "error": "未找到该股票数据"}
    except Exception as e:
        return {"code": 1, "error": str(e)}

def get_stock_info_eastmoney(symbol):
    """获取股票基本信息"""
    if symbol.startswith('6'):
        secid = f"1.{symbol}"
    else:
        secid = f"0.{symbol}"
    
    url = f"https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "secid": secid,
        "fields": "f57,f58,f43,f44,f45,f46,f47,f48,f50,f107,f169,f170,f171"
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        if data.get('data'):
            d = data['data']
            return {
                "code": symbol,
                "name": d.get('f58', '未知'),
                "latestPrice": d.get('f43', 0) / 100 if d.get('f43') else 0,
                "change": d.get('f170', 0) / 100 if d.get('f170') else 0,
                "volume": d.get('f47', 0) / 100 if d.get('f47') else 0,
                "amount": d.get('f48', 0) / 1000 if d.get('f48') else 0,
            }
    except:
        pass
    
    return {"code": symbol, "name": symbol}

@app.route('/')
def index():
    return jsonify({
        "name": "股票数据API",
        "version": "1.0",
        "usage": "/stock/<code>?start=2024-01-01&end=2024-12-31"
    })

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/stock/<code>')
def get_stock(code):
    """获取股票K线数据"""
    start = request.args.get('start', '2024-01-01')
    end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
    
    logger.info(f"获取股票: {code}, 日期: {start} - {end}")
    
    result = get_stock_data_eastmoney(code, start, end)
    
    if result.get('code') == 0:
        return jsonify(result)
    else:
        return jsonify(result), 400

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
