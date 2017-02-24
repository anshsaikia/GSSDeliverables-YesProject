import requests

__author__ = 'zhamilto'

class VeTestRequests(object):
    '''
    classdocs
    '''
    def __init__ (self,test):
        self.test = test
        self.list = []

    def request(self, method, url, **kwargs):
        request_item = {"method": method, "path": url, "args": kwargs}
        self.list.append(request_item)
        return requests.request(method, url, **kwargs)

    def get(self, url, params=None, **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return self.request('get', url, params=params, **kwargs)

    def options(self, url, **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return self.request('options', url, **kwargs)

    def head(self, url, **kwargs):
        kwargs.setdefault('allow_redirects', False)
        return self.request('head', url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        return self.request('post', url, data=data, json=json, **kwargs)

    def put(self, url, data=None, **kwargs):
        return self.request('put', url, data=data, **kwargs)

    def patch(self, url, data=None, **kwargs):
        return self.request('patch', url,  data=data, **kwargs)

    def delete(self, url, **kwargs):
        return self.request('delete', url, **kwargs)
