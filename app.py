# -*- coding: utf-8 -*-
"""
股票数据 API 服务
部署到 Railway
"""

from flask import Flask, jsonify, request
import akshare as ak
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "name": "股票数据API",
        "version": "1.0",
        "endpoints": ["/stock/<code>", "/health"]
    })

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/stock/<code>')
def get_stock(code):
    """获取股票K线数据"""
    try:
        # 获取参数
        start = request.args.get('start', '20240101')
        end = request.args.get('end', datetime.now().strftime('%Y%m%d'))
        
        logger.info(f"获取股票: {code}, 日期: {start} - {end}")
        
        # 转换代码格式
        symbol = code
        if symbol.startswith('sh'):
            symbol = symbol[2:]
        elif symbol.startswith('sz'):
            symbol = symbol[2:]
        
        # 获取股票信息
        stock_info = ak.stock_individual_info_em(symbol=symbol)
        name = "未知"
        for _, row in stock_info.iterrows():
            if row['item'] == '股票名称':
                name = row['value']
                break
        
        # 获取K线数据
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            start_date=start.replace('-', ''),
            end_date=end.replace('-', ''),
            adjust="qfq"
        )
        
        # 转换数据
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
        
        return jsonify({
            "code": 0,
            "data": data,
            "info": info
        })
        
    except Exception as e:
        logger.error(f"错误: {str(e)}")
        return jsonify({
            "code": 1,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
