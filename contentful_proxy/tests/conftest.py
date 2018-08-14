from dev_appserver import fix_sys_path
fix_sys_path()

import contentful_proxy.utils.pytest  # reload gae resources
import contentful_proxy.appengine_config  # import vendor modules to gae

import pytest
import webapp2
import webtest


@pytest.fixture
def testbed():
    """Helps with manipulate stubs for API testing on Google App Engine"""

    from google.appengine.datastore import datastore_stub_util
    from google.appengine.ext import testbed

    tb = testbed.Testbed()
    tb.consistency = datastore_stub_util.PseudoRandomHRConsistencyPolicy(
        probability=1,
    )
    tb.activate()
    tb.init_app_identity_stub()
    tb.init_datastore_v3_stub(consistency_policy=tb.consistency)
    tb.init_memcache_stub()
    tb.init_urlfetch_stub()
    tb.init_app_identity_stub()
    tb.init_search_stub()

    tb.init_taskqueue_stub(root_path='.')
    tb.MEMCACHE_SERVICE_NAME = testbed.MEMCACHE_SERVICE_NAME
    tb.TASKQUEUE_SERVICE_NAME = testbed.TASKQUEUE_SERVICE_NAME

    yield tb

    tb.deactivate()


@pytest.fixture
def app(testbed):
    import os
    from contentful_proxy import routing
    os.environ['CONTENTFUL_SPACE'] = '123'
    os.environ['CONTENTFUL_TOKEN'] = '123'

    app = webapp2.WSGIApplication(
        routing.contentful_routes + routing.contentful_management_routes + routing.cron_routes,
        debug=True
    )
    return webtest.TestApp(app)
