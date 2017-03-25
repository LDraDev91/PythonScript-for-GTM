"""
Access Google Analytics API and create or get web property tracking ID
"""
from __future__ import print_function, unicode_literals
from googleapiclient.discovery import build

import httplib2
import settings
from googleapiclient.http import HttpError
import simplejson as json
from oauth2client.service_account import ServiceAccountCredentials


def GetService(api_name, api_version, scope, key_file_location):

      print('Connecting to Google Analytics service...')

      credentials = ServiceAccountCredentials.from_json_keyfile_name(scopes=scope, filename=key_file_location)

      http = credentials.authorize(httplib2.Http())

      # Build the service object.
      service = build(api_name, api_version, http=http)

      return service


def GetOrCreateTrackingId(service, site_name, site_url):

    print('Creating Web property to get Tracking ID...')

    try:
        accounts = service.management().accounts().list(fields='items').execute()
    except HttpError as error:
        raise Exception('Currently you have not created any account on Google Analytics or You have not assigned '
                        'permissions to your service account email for Goolge Analytics. '
                        'Create Google Analytics account here '
                        'https://analytics.google.com/analytics/web/#management/Settings/a47311425w132280467p136241489/%3Fm.page%3DNewAccount/'
                        ' OR assign permissions to your service account here '
                        'https://support.google.com/analytics/answer/6132368')

    if accounts.get('items'):

        # Get the first Google Analytics account.
        account = accounts.get('items')[0].get('id')

        # Get a list of all the properties for the first account.
        properties = service.management().webproperties().list(accountId=account, fields='items').execute()

        if properties.get('items'):

          # check if property already exists then simply return tracking code from property
          for property in properties.get('items'):
              if site_name == property.get('name'):
                  return property.get('id')

          try:
              web_property = service.management().webproperties().insert(
                  accountId=account,
                  fields='id',
                  body={
                      'websiteUrl': site_url,
                      'name': site_name
                  }
              ).execute()

          except TypeError as error:
              # Handle errors in constructing a query.
              raise Exception('There was an error in constructing your query : %s' % error)

          except HttpError as error:
              # Handle API errors.
              raise Exception('There was an in API call or your Account ID. Original Message: %s :' % (json.loads(error.content)['error']['message']))

    return web_property.get('id')
