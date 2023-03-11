import os                         # 导入系统OS模块
import requests                   # 导入请求处理Requests模块
from flask import Flask, jsonify, Response, render_template, request, url_for, send_from_directory  # 导入Flask框架相关模块
from werkzeug.utils import secure_filename  # 导入工具模块

# 环境变量SERVERLESS是否为真
IS_SERVERLESS = bool(os.environ.get('SERVERLESS'))
print(IS_SERVERLESS)

app = Flask(__name__)   # 初始化Flask应用程序

target_url = "https://api.openai.com/" # 设置目标url

# 设置路由指向，处理所有请求方法
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy(path):
    # 处理请求头中的Host
    headers = {key: value for (key, value) in request.headers if key != 'Host'}
    
    # 发起请求到目标url，并返回响应
    resp = requests.request(
        method=request.method,         # 使用与客户端相同的HTTP动词
        url=target_url + path,         # 请求的URL目标路径
        headers=headers,               # 将去除 Host 的请求头添加到目标URL请求头中
        data=request.get_data(),       # 获取客户端数据并添加到请求对应位置中
        cookies=request.cookies,       # 获取客户端cookie信息
        allow_redirects=False,         # 是否重定向
        verify=False)                  # 跳过SSl证书验证，避免HTTP 403 Forbidden等403错误

    # 处理过滤掉不需要响应头部属性
    exclude_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in exclude_headers]

    # 返回请求响应
    response = Response(resp.content, resp.status_code, headers)
    return response

# 运行应用程序
app.run(debug=IS_SERVERLESS != True, port=9000, host='0.0.0.0')
