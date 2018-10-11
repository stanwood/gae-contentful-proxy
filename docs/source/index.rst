.. gae-contentful-proxy documentation master file, created by
   sphinx-quickstart on Wed Oct  3 16:45:37 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to gae-contentful-proxy's documentation!
================================================

Module based on top of Google Cloud Platform which creates simple proxy for `Contentful API <https://www.contentful.com/developers/docs/references/content-delivery-api>`_.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   _modules/modules.rst


Example usage
**********************


1. Requirements:

   .. code-block:: bash

      pip install -r requirements.txt

2. Example file with handlers:

   .. code-block:: python

      from contentful_proxy import routes

      app = webapp2.WSGIApplication(
         routes.contentful_routes + routes.cron_routes,
         debug=True
      )

3. Example App Engine settings file (app.yaml):

   .. code-block:: yaml

    api_version: 1

    builtins:
    - deferred: true

    env_variables:
      CONTENTFUL_SPACE: {CONTENTFUL_SPACE}
      CONTENTFUL_SPACE_ID: {CONTENTFUL_SPACE_ID}
      CONTENTFUL_MANAGEMENT_TOKEN: {CONTENTFUL_MANAGEMENT_TOKEN}

    handlers:
    - url: /_ah/queue/deferred
      login: admin
      script: google.appengine.ext.deferred.deferred.application
    - url: /ah/cron/.*
      login: admin
      script: main.app
    - url: .*
      script: main.app

    instance_class: F1

    libraries:
    - name: webapp2
      version: 2.5.2
    - name: ssl
      version: 2.7.11
    - name: webob
      version: latest

    runtime: python27
    threadsafe: true

4. Example cron:

   .. code-block:: yaml

    cron:
    - description: Delete old cached files
      url: /_ah/cron/clean-up-files
      schedule: every day 2:00
      timezone: Europe/Berlin

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
