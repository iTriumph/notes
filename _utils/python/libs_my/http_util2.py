#!python
# -*- coding:utf-8 -*-
"""
http请求公用函数(http请求处理)
Created on 2019/3/13
Updated on 2019/3/13
@author: Holemar
"""
import sys
import time
import urllib
import urllib2
import logging
import threading

from . import str_util

__all__= ('init', 'get', 'post', 'put', 'delete', 'patch', 'options', 'send', 'multiple_send', 'url_encode', 'getRequestParams')
logger = logging.getLogger('libs_my.http_util')


# 请求默认值
CONFIG = {
    'timeout' : 30, # {int} 请求超时时间(单位:秒,设为 None 则是不设置超时时间)
    'warning_time' : 5, # {int} 运行时间过长警告(超过这时间的将会警告,单位:秒)
    'send_json' : False, # {bool} 提交参数是否需要 json 化
    'return_json' : False, # {bool} 返回结果是否需要 json 化
    'threads' : False, # {bool} 是否发起多线程去请求,将会不再接收返回值(可节省等待请求返回的时间)
    'gzip' : False, # {string} 使用的压缩模式,值可为: gzip, deflate (值为 False 时不压缩,默认:不压缩)
    'repeat_time' : 1, # {int|long|float} 提交请求的最大次数,默认只提交1次。(1表示只提交一次,失败也不再重复提交； 2表示允许重复提交2次,即第一次失败时再来一次,3表示允许重复提交3次...)
    'judge' : (lambda result: result!=None), # {lambda} 判断返回值是否正确的函数(默认只要正常返回就认为正确, 当 repeat_time 参数大于 1 时不正确的返回值会自动再提交一次, 直至 repeat_time < 1 或者返回正确时为止)
    'headers':{}, # {dict} 请求的头部信息
}


def init(**kwargs):
    """
    设置get和post函数的默认参数值
    :param {int} timeout: 请求超时时间(单位:秒,设为 None 则是不设置超时时间)
    :param {int} warning_time: 运行时间过长警告(超过这时间的将会警告,单位:秒)
    :param {bool} send_json: 提交参数是否需要 json 化
    :param {bool} return_json: 返回结果是否需要 json 化
    :param {bool} threads: 是否发起多线程去请求,将会不再接收返回值(可节省等待请求返回的时间)
    :param {bool} gzip : 使用的压缩模式,值可为: gzip, deflate (值为 False 时不压缩,默认:不压缩)
    :param {int|long|float} repeat_time: 提交请求的最大次数,默认只提交1次。(1表示只提交一次,失败也不再重复提交； 2表示允许重复提交2次,即第一次失败时再来一次,3表示允许重复提交3次...)
    :param {lambda} judge: 判断返回值是否正确的函数(默认只要正常返回就认为正确, 当 repeat_time 参数大于 1 时不正确的返回值会自动再提交一次, 直至 repeat_time < 1 或者返回正确时为止)
    :param {dict} headers: 请求的头部信息
    """
    global CONFIG
    CONFIG.get('headers', {}).update(kwargs.pop('headers', {}))
    CONFIG.update(kwargs)


def send(url, param=None, method='GET', **kwargs):
    """
    发出请求获取网页内容
    :param {string} url: 要获取内容的网页地址(GET请求时可直接将请求参数写在此url上)
    :param {dict|string} param: 要提交到网页的参数(get请求时会拼接到 url 上)
    :param {string} method: 提交方式,目前只支持 GET 和 POST 两种
    :param {int} timeout: 请求超时时间(单位:秒,设为 None 则是不设置超时时间)
    :return {string}: 返回获取的页面内容字符串
    """
    global CONFIG
    timeout = kwargs.get('timeout', CONFIG.get('timeout', None)) # 超时时间
    # 提交请求
    try:
        response = urllib2.urlopen(url=url, data=param, timeout=timeout)
        res = response.read()
        status_code = response.getcode() # 响应状态码,不是 200 时直接就报异常了
        response.close()
    except urllib2.HTTPError as e:
        status_code = e.code
        res = e.read()
    return status_code, res


def multiple_send(url, param=None, method='GET', **kwargs):
    u"""
    发出请求获取网页内容(会要求服务器使用gzip压缩返回结果,也会提交文件等内容,需要服务器支持这些功能)
    :param {string} url: 要获取内容的网页地址(GET请求时可直接将请求参数写在此url上)
    :param {dict|string} param: 要提交到网页的参数(get请求时会拼接到 url 上)
    :param {string} method: 提交方式,目前只支持 GET 和 POST 两种
    :param {int} timeout: 请求超时时间(单位:秒,设为 None 则是不设置超时时间)
    :param {dict} headers: 请求的头部信息
    :param {bool} gzip : 使用的压缩模式,值可为: gzip, deflate (值为 False 时不压缩,默认:deflate压缩)
    :return {string}: 返回获取的页面内容字符串
    """
    global CONFIG
    method = method.strip().upper()
    timeout = kwargs.get('timeout', CONFIG.get('timeout', None))
    headers = kwargs.get('headers', CONFIG.get('headers', {}))
    encoding = kwargs.get('encoding', 'gzip')

    # 提交请求
    request = urllib2.Request(url=url, data=param, headers=headers)
    if encoding:
        if not isinstance(encoding, basestring):
            encoding = 'gzip'
        request.add_header('Accept-Encoding', encoding)
    if method not in ('GET', 'POST'):
        request.get_method = lambda:method
    try:
        response = urllib2.urlopen(request, timeout=timeout)
        encoding = response.headers.get('Content-Encoding')
        status_code = response.getcode() # 响应状态码,不是 200 时直接就报异常了
        res = response.read()
        response.close()
    except urllib2.HTTPError as e:
        encoding = e.headers.get('Content-Encoding')
        status_code = e.code
        res = e.read()

    # 处理返回结果
    if encoding in ('gzip', 'deflate'):
        before_len = len(res)
        if encoding == 'gzip':
            res = str_util.gzip_decode(res)
        elif encoding == 'deflate':
            res = str_util.zlib_decode(res)
        after_length = len(res)
        logger.info(u"%s %s 压缩请求: 解压前结果长度:%s, 解压后结果长度:%s, url:%s, param:%s", method, encoding, before_len, after_length, url, param,
            extra={ 'method':method, 'url':url, 'param':param, 'result':res, 'encoding':encoding, 'before_length':before_len, 'after_length':after_length}
        )
    return status_code, res


def _handler(url, param=None, method='GET', **kwargs):
    """请求处理函数
    1.判断请求是否成功,是否返回符合验证的值
    2.请求失败及返回值不对则重发请求
    3.返回结果是否需要 json 反序列化
    """
    global CONFIG
    method = method.strip().upper()
    text = None
    _zip = kwargs.get('gzip', CONFIG.get('gzip', False))
    return_json = kwargs.get('return_json', CONFIG.get('return_json', False))
    headers = kwargs.get('headers', CONFIG.get('headers', {}))
    repeat_time = int(kwargs.get('repeat_time', CONFIG.get('repeat_time', 1)))
    judge = kwargs.get('judge', CONFIG.get('judge', (lambda result: result!=None)))

    # 允许出错时重复提交多次,只要设置了 repeat_time 的次数
    status_code = 0
    res = None
    while repeat_time > 0:
        if _zip or headers or method not in ('GET', 'POST'):
            status_code, text = multiple_send(url, param=param, method=method, encoding=_zip, **kwargs)
        else:
            status_code, text = send(url, param=param, method=method, **kwargs)
        if status_code == 200: break

        # 请求异常,认为返回不正确
        repeat_time -= 1
        e = sys.exc_info()[1]
        logger.error(u"%s 请求错误:%s, 响应状态码:%s, 返回:%s", method, e, status_code, exc_info=True)

    try:
        # 转换 json 结果
        if return_json:
            res = str_util.to_str(text)
            res = str_util.to_json(res, raise_error=False)
        else:
            res = text
        # 返回值正确
        if not judge or judge(res):
            return status_code, text, res
        # 返回值不正确
        else:
            logger.error(u"%s 返回不正确的值 url:%s, param:%s, 返回:%s", method, url, param, res,
                extra={'method':method, 'url':url, 'param':param, 'result':res}
            )
    except Exception, e:
        logger.error(u"%s 接口返回内容错误: %s", method, e, exc_info=True)

    return status_code, text, res


def _deal(url, param=None, method='GET', **kwargs):
    """处理请求的主函数
    1.处理请求参数,转成url参数形式字符串,或者json字符串
    2.判断是否发起线程来请求
    3.记录日志
    """
    start_time = time.time()
    global CONFIG
    res = None
    threads = kwargs.pop('threads', CONFIG.get('threads', False))
    warning_time = kwargs.get('warning_time', CONFIG.get('warning_time', 5))
    send_json = kwargs.get('send_json', CONFIG.get('send_json', False))
    headers = kwargs.get('headers', CONFIG.get('headers', {}))

    use_time = None
    try:
        # 提交异步请求(不处理返回结果)
        if threads:
            kwargs['threads'] = False # 避免递归发起线程
            th = threading.Thread(target=_deal, kwargs=dict(url=url, param=param, method=method,**kwargs))
            th.start() # 启动这个线程
            return th # 返回这个线程,以便 join 多个异步请求

        url = str_util.to_str(url)
        method = method.strip().upper()
        # get 方式的参数处理
        if method == 'GET':
            if param:
                # 参数拼接
                url += "&" if "?" in url else "?"
                url += url_encode(param)
            param = None
        # post、put、delete、patch、options 方式的参数处理
        else:
            if send_json:
                if not param:
                    param = ''
                elif isinstance(param, basestring):
                    pass
                else:
                    param = str_util.json2str(param)
                headers.update({'Content-Type':'application/json'})
                kwargs['headers'] = headers
            else:
                param = url_encode(param)

        # 提交请求
        status_code, text, res = _handler(url=url, param=param, method=method, **kwargs)

        # 是否输出为便于人阅读的模式
        log_param = (u', param:%s' % param) if param else ''
        log_param = (u'%s, headers:%s' % (log_param, headers)) if headers else log_param
        # 记录花费时间
        use_time = time.time() - start_time
        if use_time > float(warning_time):
            logger.warn(u"%s url 耗时太长, 用时:%.4f秒 -->%s%s 返回-->%s", method, use_time, url, log_param, text,
                extra={'method':method, 'url':url, 'param':param, 'result':text, 'use_time':use_time}
            )
        else:
            logger.info(u"%s 用时:%.4f秒, url-->%s%s 返回-->%s", method, use_time, url, log_param, text,
                extra={'method':method, 'url':url, 'param':param, 'result':text, 'use_time':use_time}
            )
        return res
    except Exception, e:
        if not use_time:
            use_time = time.time() - start_time
        logger.error(u"%s 请求错误:%s", method, e, exc_info=True)
    return res


def get(url, param=None, **kwargs):
    u"""
    get方式获取网页内容
    :param {string} url: 要获取内容的网页地址(GET请求时可直接将请求参数写在此url上)
    :param {dict|string} param: 要提交到网页的参数(get请求时会拼接到 url 上)
    :param {int} timeout: 请求超时时间(单位:秒,设为 None 则是不设置超时时间)
    :param {int} warning_time: 运行时间过长警告(超过这时间的将会警告,单位:秒)
    :param {bool} return_json: 返回结果是否需要 json 化
    :param {bool} threads: 是否发起多线程去请求,将会不再接收返回值(可节省等待请求返回的时间)
    :param {bool} gzip : 使用的压缩模式,值可为: gzip, deflate (值为 False 时不压缩,默认:不压缩)
    :param {int|long|float} repeat_time: 提交请求的最大次数,默认只提交1次。(1表示只提交一次,失败也不再重复提交； 2表示允许重复提交2次,即第一次失败时再来一次,3表示允许重复提交3次...)
    :param {lambda} judge: 判断返回值是否正确的函数(默认只要正常返回就认为正确, 当 repeat_time 参数大于 1 时不正确的返回值会自动再提交一次, 直至 repeat_time < 1 或者返回正确时为止)
    :param {dict} headers: 请求的头部信息
    :return {string}: 返回获取的页面内容字符串
    @example
        s = get('http://www.example.com?a=1&b=uu')
        s = get('http://www.example.com?a=1', {'name' : 'user1', 'password' : '123456'})
    """
    kwargs.pop('method', None)
    return _deal(url, param=param, method='GET', **kwargs)


def post(url, param=None, **kwargs):
    u"""
    post方式获取网页内容
    :param {string} url: 要获取内容的网页地址(GET请求时可直接将请求参数写在此url上)
    :param {dict|string} param: 要提交到网页的参数
    :param {int} timeout: 请求超时时间(单位:秒,设为 None 则是不设置超时时间)
    :param {int} warning_time: 运行时间过长警告(超过这时间的将会警告,单位:秒)
    :param {bool} send_json: 提交参数是否需要 json 化
    :param {bool} return_json: 返回结果是否需要 json 化
    :param {bool} threads: 是否发起多线程去请求,将会不再接收返回值(可节省等待请求返回的时间)
    :param {bool} gzip : 使用的压缩模式,值可为: gzip, deflate (值为 False 时不压缩,默认:不压缩)
    :param {int|long|float} repeat_time: 提交请求的最大次数,默认只提交1次。(1表示只提交一次,失败也不再重复提交； 2表示允许重复提交2次,即第一次失败时再来一次,3表示允许重复提交3次...)
    :param {lambda} judge: 判断返回值是否正确的函数(默认只要正常返回就认为正确, 当 repeat_time 参数大于 1 时不正确的返回值会自动再提交一次, 直至 repeat_time < 1 或者返回正确时为止)
    :param {dict} headers: 请求的头部信息
    :return {string}: 返回获取的页面内容字符串
    @example
        s = post('http://www.example.com?a=1&b=uu')
        s = post('http://www.example.com?a=1', {'name' : 'user1', 'password' : '123456'})
    """
    kwargs.pop('method', None)
    return _deal(url, param=param, method='POST', **kwargs)


def put(url, param=None, **kwargs):
    u"""
    put方式获取网页内容
    :param {string} url: 要获取内容的网页地址(GET请求时可直接将请求参数写在此url上)
    :param {dict|string} param: 要提交到网页的参数
    :param {int} timeout: 请求超时时间(单位:秒,设为 None 则是不设置超时时间)
    :param {int} warning_time: 运行时间过长警告(超过这时间的将会警告,单位:秒)
    :param {bool} send_json: 提交参数是否需要 json 化
    :param {bool} return_json: 返回结果是否需要 json 化
    :param {bool} threads: 是否发起多线程去请求,将会不再接收返回值(可节省等待请求返回的时间)
    :param {bool} gzip : 使用的压缩模式,值可为: gzip, deflate (值为 False 时不压缩,默认:不压缩)
    :param {int|long|float} repeat_time: 提交请求的最大次数,默认只提交1次。(1表示只提交一次,失败也不再重复提交； 2表示允许重复提交2次,即第一次失败时再来一次,3表示允许重复提交3次...)
    :param {lambda} judge: 判断返回值是否正确的函数(默认只要正常返回就认为正确, 当 repeat_time 参数大于 1 时不正确的返回值会自动再提交一次, 直至 repeat_time < 1 或者返回正确时为止)
    :param {dict} headers: 请求的头部信息
    :return {string}: 返回获取的页面内容字符串
    @example
        s = put('http://www.example.com?a=1&b=uu')
        s = put('http://www.example.com?a=1', {'name' : 'user1', 'password' : '123456'})
    """
    kwargs.pop('method', None)
    return _deal(url, param=param, method='PUT', **kwargs)


def delete(url, param=None, **kwargs):
    u"""
    delete方式获取网页内容
    :param {string} url: 要获取内容的网页地址(GET请求时可直接将请求参数写在此url上)
    :param {dict|string} param: 要提交到网页的参数
    :param {int} timeout: 请求超时时间(单位:秒,设为 None 则是不设置超时时间)
    :param {int} warning_time: 运行时间过长警告(超过这时间的将会警告,单位:秒)
    :param {bool} send_json: 提交参数是否需要 json 化
    :param {bool} return_json: 返回结果是否需要 json 化
    :param {bool} threads: 是否发起多线程去请求,将会不再接收返回值(可节省等待请求返回的时间)
    :param {bool} gzip : 使用的压缩模式,值可为: gzip, deflate (值为 False 时不压缩,默认:不压缩)
    :param {int|long|float} repeat_time: 提交请求的最大次数,默认只提交1次。(1表示只提交一次,失败也不再重复提交； 2表示允许重复提交2次,即第一次失败时再来一次,3表示允许重复提交3次...)
    :param {lambda} judge: 判断返回值是否正确的函数(默认只要正常返回就认为正确, 当 repeat_time 参数大于 1 时不正确的返回值会自动再提交一次, 直至 repeat_time < 1 或者返回正确时为止)
    :param {dict} headers: 请求的头部信息
    :return {string}: 返回获取的页面内容字符串
    @example
        s = delete('http://www.example.com?a=1&b=uu')
        s = delete('http://www.example.com?a=1', {'name' : 'user1', 'password' : '123456'})
    """
    kwargs.pop('method', None)
    return _deal(url, param=param, method='DELETE', **kwargs)


def patch(url, param=None, **kwargs):
    u"""
    patch方式获取网页内容
    :param {string} url: 要获取内容的网页地址(GET请求时可直接将请求参数写在此url上)
    :param {dict|string} param: 要提交到网页的参数
    :param {int} timeout: 请求超时时间(单位:秒,设为 None 则是不设置超时时间)
    :param {int} warning_time: 运行时间过长警告(超过这时间的将会警告,单位:秒)
    :param {bool} send_json: 提交参数是否需要 json 化
    :param {bool} return_json: 返回结果是否需要 json 化
    :param {bool} threads: 是否发起多线程去请求,将会不再接收返回值(可节省等待请求返回的时间)
    :param {bool} gzip : 使用的压缩模式,值可为: gzip, deflate (值为 False 时不压缩,默认:不压缩)
    :param {int|long|float} repeat_time: 提交请求的最大次数,默认只提交1次。(1表示只提交一次,失败也不再重复提交； 2表示允许重复提交2次,即第一次失败时再来一次,3表示允许重复提交3次...)
    :param {lambda} judge: 判断返回值是否正确的函数(默认只要正常返回就认为正确, 当 repeat_time 参数大于 1 时不正确的返回值会自动再提交一次, 直至 repeat_time < 1 或者返回正确时为止)
    :param {dict} headers: 请求的头部信息
    :return {string}: 返回获取的页面内容字符串
    @example
        s = patch('http://www.example.com?a=1&b=uu')
        s = patch('http://www.example.com?a=1', {'name' : 'user1', 'password' : '123456'})
    """
    kwargs.pop('method', None)
    return _deal(url, param=param, method='PATCH', **kwargs)


def options(url, param=None, **kwargs):
    u"""
    options方式获取网页内容
    :param {string} url: 要获取内容的网页地址(GET请求时可直接将请求参数写在此url上)
    :param {dict|string} param: 要提交到网页的参数
    :param {int} timeout: 请求超时时间(单位:秒,设为 None 则是不设置超时时间)
    :param {int} warning_time: 运行时间过长警告(超过这时间的将会警告,单位:秒)
    :param {bool} send_json: 提交参数是否需要 json 化
    :param {bool} return_json: 返回结果是否需要 json 化
    :param {bool} threads: 是否发起多线程去请求,将会不再接收返回值(可节省等待请求返回的时间)
    :param {bool} gzip : 使用的压缩模式,值可为: gzip, deflate (值为 False 时不压缩,默认:不压缩)
    :param {int|long|float} repeat_time: 提交请求的最大次数,默认只提交1次。(1表示只提交一次,失败也不再重复提交； 2表示允许重复提交2次,即第一次失败时再来一次,3表示允许重复提交3次...)
    :param {lambda} judge: 判断返回值是否正确的函数(默认只要正常返回就认为正确, 当 repeat_time 参数大于 1 时不正确的返回值会自动再提交一次, 直至 repeat_time < 1 或者返回正确时为止)
    :param {dict} headers: 请求的头部信息
    :return {string}: 返回获取的页面内容字符串
    @example
        s = options('http://www.example.com?a=1&b=uu')
        s = options('http://www.example.com?a=1', {'name' : 'user1', 'password' : '123456'})
    """
    kwargs.pop('method', None)
    return _deal(url, param=param, method='OPTIONS', **kwargs)


def getRequestParams(url):
    """
    获取url里面的参数,以字典的形式返回
    :param {string} url: 请求地址
    :return {dict}: 以字典的形式返回请求里面的参数
    """
    result = {}
    if not isinstance(url, basestring):
        if isinstance(url, dict):
            return url
        else:
            return result
    url = str_util.to_str(url)

    #li = re.findall(r'\w+=[^&]*', url) # 为了提高效率，避免使用正则
    i = url.find('?')
    if i != -1:
        url = url[i+1:]
    li = url.split('&')

    if not li:
        return result

    for ns in li:
        if not ns:continue
        (key,value) = ns.split('=', 1) if ns.find('=') != -1 else (ns, '')
        value = value.replace('+', ' ') # 空格会变成加号
        result[key] = urllib.unquote(value) # 值需要转码

    return result


def url_encode(param, encode='utf-8', send_json=False):
    u"""
    将字典转成 url 参数
    :param {dict|string} param: 要提交到网页的参数(get方式会拼接到 url 上)
    :param {string} encode: 编码类型,默认是 utf-8 编码
    :param {bool} send_json: 提交参数是否需要 json 化
    :return {string}: 返回可以提交的字符串参数
    @example
        s = url_encode({'name' : '测试用户', 'password' : 123456})  # 返回:password=123456&name=%E6%B5%8B%E8%AF%95%E7%94%A8%E6%88%B7
    """
    if not param:
        return ''
    # 必须转码成str,用 unicode 转url编码中文会报错
    param = str_util.deep_str(param, encode=encode, str_unicode=str_util.to_str)
    if isinstance(param, dict):
        for k,v in param.iteritems():
            if v == None:
                param[k] = ''
            elif not isinstance(v, basestring):
                param[k] = str_util.json2str(v)
        param = urllib.urlencode(param)
    # 字符串类型,不再处理
    elif isinstance(param, basestring):
        pass
    # 其它类型,转成字符串
    else:
        param = str_util.json2str(param)
    return param

