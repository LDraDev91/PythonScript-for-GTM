from googleapiclient.discovery import build
from googleapiclient.http import HttpError
import simplejson as json
import settings

from oauth2client.service_account import ServiceAccountCredentials

import httplib2


def GetService(api_name, api_version, scope, key_file_location):

      print('Connecting to Google Tag Manager service...')

      credentials = ServiceAccountCredentials.from_json_keyfile_name(scopes=scope, filename=key_file_location)

      http = credentials.authorize(httplib2.Http())

      # Build the service object.
      service = build(api_name, api_version, http=http)

      return service


def GetAccountID(service):

    print('Getting your Google Tag Manager Accounts...')

    # Note: This code assumes you have an authorized tagmanager service object.

    # This request lists all accounts for the authorized user.
    try:
        accounts = service.accounts().list(fields='accounts/accountId').execute()
    except TypeError as error:
        # Handle errors in constructing a query.
        raise Exception('There was an error in constructing your query : %s' % error)

    except HttpError as error:
        # Handle API errors.
        raise Exception('There was an API error : %s' % (json.loads(error.content)['error']['message']))

    # The results of the list method are stored in the accounts object.
    # get first account
    if accounts.get('accounts'):
        return accounts.get('accounts')[0].get('accountId')
    raise Exception('Currently you have not created any account on Google Tag Manager or You have not assigned '
                    'permissions to your service account email for Goolge Tag Manager. '
                    'Either create Google Tag account here https://tagmanager.google.com/#/admin/accounts/create'
                    ' OR assign permissions to your service account here '
                    'https://support.google.com/tagmanager/answer/6107011?hl=en')


def GetContainersList(service, account_id):
    """
    This code assumes you have an authorized tagmanager service object.
    This request lists all containers for the authorized user.
    """

    try:
        containers = service.accounts().containers().list(
            accountId=account_id,
            fields='containers/name, containers/containerId, containers/publicId'
        ).execute()

    except TypeError as error:
        # Handle errors in constructing a query.
        raise Exception('There was an error in constructing your query : %s' % error)

    except HttpError as error:
        # Handle API errors.
        raise Exception('There was an error either in API call or your Account ID. Original Message: %s' %
                        (json.loads(error.content)['error']['message']))

    # The results of the list method are stored in the containers object.
    return {
            container.get('name'): (container.get('containerId'), container.get('publicId')) for container in containers.get('containers', [])
           }


def CreateOrGetContainer(service, account_id, container_name, container_site, container_type=None):
    """
    This code assumes you have an authorized tagmanager service object, account ID and container name.
    This request creates a new container or return existing container if exists
    It may return container public id to be used for GMT snippet or
    it may return container id to get tag or create tag
    """

    account_containers = GetContainersList(service, account_id)
    if container_name in account_containers.keys():

        if container_type == 'public_id':
            return account_containers[container_name][1]

        return account_containers[container_name][0]

    print('Creating new container...')

    try:
        response = service.accounts().containers().create(
            accountId=account_id,
            fields='containerId',
            body={
                'name': container_name,
                'timeZoneCountryId': settings.TIME_ZONE_COUNTRY_ID,
                'timeZoneId': settings.TIME_ZONE_ID,
                'usageContext': settings.GOOGLE_TAG_USAGE_CONTEXT,
                'domainName':  [container_site]
            }
        ).execute()

    except AttributeError as error:
        # handle attribute missing error for timezone and usage context in settings.py
        raise Exception('Improperly configured settings: %s' % error)

    except TypeError as error:
        # Handle errors in constructing a query.
        raise Exception('There was an error in constructing your query : %s' % error)

    except HttpError as error:
        # Handle API errors.
        raise Exception('There was an error either in API call or your Account ID. Original Message: %s' % (
            json.loads(error.content)['error']['message']))

    # The results of the create method are stored in the response object.
    # The following code shows how to access the created id and fingerprint.
    return response.get('containerId')


def GetTagsList(service, account_id, container_id):
    """
    Note: This code assumes you have an authorized tagmanager service object.

    # This request lists all tags for the authorized user.
    """

    print('Getting existing Tags...')

    try:
        tags = service.accounts().containers().tags().list(
            accountId=account_id,
            containerId=container_id,
            fields='tags/name, tags/tagId'
        ).execute()

    except TypeError as error:
        # Handle errors in constructing a query.
        raise Exception('There was an error in constructing your query : %s' % error)

    except HttpError as error:
        # Handle API errors.
        raise Exception('There was an API error : %s : %s' % (error.resp.status, error.resp.reason))

    # The results of the list method are stored in the tags object.
    # The following code shows how to iterate through them.
    return {
             tag.get('name'): tag.get('tagId') for tag in tags.get('tags', [])
            }


def GetTagDetails(service, account_id, container_id, tag_id):
    """
    # Note: This code assumes you have an authorized tagmanager service object.

    # This request gets an existing new container tag.
    """
    try:
        tag = service.accounts().containers().tags().get(
            accountId=account_id,
            containerId=container_id,
            tagId=tag_id,
            fields=''
        ).execute()

    except TypeError as error:
        # Handle errors in constructing a query.
        raise Exception('There was an error in constructing your query : %s' % error)

    except HttpError as error:
        # Handle API errors.
        raise Exception('There was an API error : %s : %s' % (error.resp.status, error.resp.reason))

    return tag


def CreateOrGetTag(service, account_id, container_id, tracking_id, tag_name='UA Hello World Tag'):
    """
    Create the Universal Analytics Hello World Tag or return if exist

    Args:
    service: the Tag Manager service object.
    account_id: the ID of the account holding the container.
    container_id: the ID of the container to create the tag in.
    tracking_id: the Universal Analytics tracking ID to use.

    Returns:
    The API response as a dict representing the newly created Tag resource
    or an error.
    """

    container_tags = GetTagsList(service, account_id, container_id)
    if tag_name in container_tags.keys():
        tag_id = container_tags[tag_name]
        return GetTagDetails(service, account_id, container_id, tag_id)

    hello_world_tag = {
      'name': tag_name,
      'type': 'ua',
      'parameter': [{
          'key': 'trackingId',
          'type': 'template',
          'value': str(tracking_id),
      }],
    }

    print('Creating Tag...')

    try:
        response = service.accounts().containers().tags().create(
          accountId=account_id,
          containerId=container_id,
          body=hello_world_tag,
          fields=''
        ).execute()

    except TypeError as error:
        # Handle errors in constructing a query.
        raise Exception('There was an error in constructing your query : %s' % error)

    except HttpError as error:
        # Handle API errors.
        raise Exception('There was an error either in API call or Google Tracking ID. Original Message: %s' % (
            json.loads(error.content)['error']['message']))
    return response


def CreateContainerVersion(service, account_id, container_id):
    """
    This code assumes you have an authorized tagmanager service object.
    This request creates a new container version.
    """

    print('Creating container version for publishing...')

    try:
        response = service.accounts().containers().versions().create(
            accountId=account_id,
            containerId=container_id,
            fields='containerVersion/containerVersionId',
            body={
                'quickPreview': False
            }
        ).execute()

    except TypeError as error:
        # Handle errors in constructing a query.
        raise Exception('There was an error in constructing your query : %s' % error)

    except HttpError as error:
        # Handle API errors.
        raise Exception('There was an API error or Something went wrong with your Accout. Original Message : %s' %
                        (json.loads(error.content)['error']['message']))

    # The results of the create method are stored in response object.
    # The following code shows how to access the created id and fingerprint.
    version = response.get('containerVersion', {})
    return version.get('containerVersionId')


def PublishContainerVersion(service, account_id, container_id, container_version_id):
    # Note: This code assumes you have an authorized tagmanager service object.

    # This request publishes a container version.

    print('Publishing Container...')

    try:
        service.accounts().containers().versions().publish(
            accountId=account_id,
            containerId=container_id,
            containerVersionId=container_version_id,
            fields=''
        ).execute()

    except TypeError as error:
        # Handle errors in constructing a query.
        raise Exception('There was an error in constructing your query : %s' % error)

    except HttpError as error:
        # Handle API errors.
        raise Exception('There was an API error. Original Message: %s' % (json.loads(error.content)['error']['message']))