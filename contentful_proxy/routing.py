# The MIT License (MIT)
# 
# Copyright (c) 2018 stanwood GmbH
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import webapp2
from webapp2_extras import routes

from contentful_proxy.handlers import assets
from contentful_proxy.handlers import files
from contentful_proxy.handlers import items
from contentful_proxy.handlers import managements
from contentful_proxy.handlers.cron import files_job


contentful_routes = [
    routes.PathPrefixRoute(
        '/contentful',
        [
            webapp2.Route(r'/download/<asset_id:.*>', assets.DownloadHandler),
            webapp2.Route(r'/file_cache/<source_host:[a-z.]+>/<file_path:.+>', files.CacheHandler),
            webapp2.Route(r'/<item_type:\w+>/<item_id:\w+>', items.DetailProxyHandler),
            webapp2.Route(r'/<item_type:\w+>', items.DetailProxyHandler),
            webapp2.Route(r'/', items.DetailProxyHandler),
        ],
    )
]


contentful_management_routes = [
    routes.PathPrefixRoute(
        '/contentful',
        [
            webapp2.Route(r'/manage/<endpoint:.*>', managements.ProxyHandler),
        ]
    )
]


cron_routes = [
    webapp2.Route(r'/_ah/cron/clean-up-files', files_job.CleanupCachedFilesHandler),
]
