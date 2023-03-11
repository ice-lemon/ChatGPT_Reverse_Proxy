# ChatGPT_Reverse_Proxy

这份代码主要实现了一个简单反代理，将所有请求通过代理指向目标API（OpenAI API）。此外，代理支持GET、POST、PUT、DELETE和OPTIONS方法。
每个请求都是在请求体中带有请求头和请求参数。在这个Flask框架中，每个请求都被代理处理，并将不需要的请求头滤除，然后被交给目标API处理。目标API处理完成后，会将需要的数据作为响应体返回。
最后，这个Flask应用程序会运行在0.0.0.0:9000的端口上，运行在调试模式下（如果IS_SERVERLESS不等于true），以使它能够在开发环境中调试。

#使用方法
此处以腾讯云[云函数](https://cloud.tencent.com/act/cps/redirect?redirect=10232&cps_key=800663e6ea9aa3ce68e3d1a94b81c0ff)服务为例：

##第一步：启用[云函数](https://cloud.tencent.com/act/cps/redirect?redirect=10232&cps_key=800663e6ea9aa3ce68e3d1a94b81c0ff)服务，新建一个函数服务：

[![](http://qingshengblog.oss-accelerate.aliyuncs.com/2023/03/20230311101521589.png)](http://qingshengblog.oss-accelerate.aliyuncs.com/2023/03/20230311101521589.png)

选择“**Flask 框架模版**”，点击下一步：
![file](https://qingshengblog.oss-accelerate.aliyuncs.com/2023/03/20230311111205865.png)
在基础配置中设置函数名称，选择触发器配置为如图所示：
![file](https://qingshengblog.oss-accelerate.aliyuncs.com/2023/03/20230311111436469.png)
请求方法：any
发布环境：发布
鉴权方法：免鉴权
配置完成后点击完成，稍等函数配置完成：
![file](https://qingshengblog.oss-accelerate.aliyuncs.com/2023/03/20230311111610375.png)
## 第二步：编辑云代码：
在函数服务-函数管理-函数代码中在线编辑函数代码
（在线编辑器加载有点慢，需要稍等待一会儿…约3分钟…）
在线编辑器加载完毕后，在左侧文件列表中选择“app.py”文件，删除文件内全部内容
![file](https://qingshengblog.oss-accelerate.aliyuncs.com/2023/03/20230311112024852.png)
并将如下代码复制到“app.py”文件内:
```python
import os                         # 导入系统OS模块
import requests                   # 导入请求处理Requests模块
from flask import Flask, jsonify, Response, render_template, request, url_for, send_from_directory  # 导入Flask框架相关模块
from werkzeug.utils import secure_filename  # 导入工具模块

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
app.run(port=9000, host='0.0.0.0')

```
粘贴完毕后，点击“部署”，等待部署完成（1~3分钟）

**注意：**首次部署未开通API网络，不会自动创建触发器，请在触发管理中开通相关服务，并手动创建触发器

##接口调试

部署完成后，在“触发管理”中可以看到触发器的公网访问路径，

![file](https://qingshengblog.oss-accelerate.aliyuncs.com/2023/03/20230311113642401.png)

此网址可用于端口转发，可以使用 Postman / Apipost 等工具进行测试：

**注意：** 公网访问路径带有 /release 将其去除后可正常使用

![file](https://qingshengblog.oss-accelerate.aliyuncs.com/2023/03/20230311114643148.png)
