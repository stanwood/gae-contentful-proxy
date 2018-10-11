[![docs badge](https://readthedocs.org/projects/gae-contentful-proxy/badge/?version=latest&style=flat)](https://gae-contentful-proxy.readthedocs.io/en/latest/)

# Contentful proxy module

Module based on top of Google Cloud Platform which creates simple proxy for 
[Contentful API](https://www.contentful.com/developers/docs/references/content-delivery-api/).

## Dependencies

- Google App Engine Standard Environment (runtime: python2.7)
- Google Cloud Storage
- Webapp2

## Example code and usage

1. Requirements:
    ```
    pip install -r requirements.txt
    ```

2. Example file with handlers:
    ```
    from contentful_proxy import routes
    
    app = webapp2.WSGIApplication(
        routes.contentful_routes + routes.cron_routes,
        debug=True
    )
    ```

3. Example App Engine settings file (app.yaml):
    ```
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
    ```

4. Example cron:
    ```
    cron:
    - description: Delete old cached files
      url: /_ah/cron/clean-up-files
      schedule: every day 2:00
      timezone: Europe/Berlin
    ```

## Documentation

Auto generate documentation

```bash

cd docs/

sphinx-apidoc -o ./source/_modules/ ../contentful_proxy/

make html
```
