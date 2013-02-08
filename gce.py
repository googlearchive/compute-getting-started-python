#!/usr/bin/env python
#
# Copyright 2012 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Compute Engine helper class.

Use this class to:
- Start an instance
- List instances
- Delete an instance
"""

__author__ = 'kbrisbin@google.com (Kathryn Hurley)'

import traceback

from apiclient.discovery import build
from apiclient.errors import HttpError
from httplib2 import HttpLib2Error
from oauth2client.client import AccessTokenRefreshError

import settings

GCE_URL = 'https://www.googleapis.com/compute/%s/projects/' % (
    settings.API_VERSION)
GCE_SCOPE = 'https://www.googleapis.com/auth/compute'


class Gce(object):
  """Demonstrates some of the image and instance API functionality."""

  def __init__(self, auth_http, project_id):
    """Initialize the Gce object.

    Args:
      auth_http: an authorized instance of Http
      project_id: the API console project name
    """
    self.service = build('compute', settings.API_VERSION, http=auth_http)
    self.project_id = project_id
    self.project_url = GCE_URL + self.project_id

  def start_instance(self,
                     instance_name,
                     zone=settings.DEFAULT_ZONE,
                     machine_type=settings.DEFAULT_MACHINE_TYPE,
                     disk=settings.DEFAULT_DISK,
                     image=settings.DEFAULT_IMAGE,
                     service_email=settings.DEFAULT_SERVICE_EMAIL,
                     network=settings.DEFAULT_NETWORK,
                     scopes=None,
                     metadata=None,
                     startup_script=None,
                     startup_script_url=None,
                     blocking=True):
    """Start instance with the given name and settings.

    Args:
      instance_name: String name for instance.
      zone: The string zone name.
      machine_type: The string machine type.
      disk: The string disk.
      image: The string image name.
      service_email: The string service email.
      network: The string network.
      scopes: List of string scopes.
      metadata: List of metadata objects.
      startup_script: The filename of a startup script.
      startup_script_url: Url of a startup script.
      blocking: Whether the function will wait for the operation to complete.

    Returns:
      Dictionary response representing the operation.

    Raises:
      ApiOperationError: Operation contains an error message.
    """
    if not instance_name:
      print 'instance_name required.'
      return

    image_url = None
    if image == settings.DEFAULT_IMAGE:
      image_url = '%sgoogle/global/images/%s' % (GCE_URL, image)
    else:
      image_url = '%s/global/images/%s' % (self.project_url, image)
    if not scopes: scopes = settings.DEFAULT_SCOPES

    instance = {
        'name': instance_name,
        'machineType': '%s/global/machineTypes/%s' % (
            self.project_url, machine_type),
        'image': image_url,
        'disks': [{
            'type': disk
        }],
        'networkInterfaces': [{
            'accessConfigs': [{
                'type': 'ONE_TO_ONE_NAT',
                'name': 'External NAT'
            }],
            'network': '%s/global/networks/%s' % (self.project_url, network)
        }],
        'serviceAccounts': [{
            'email': service_email,
            'scopes': scopes
        }]
    }

    instance['metadata'] = {}
    instance['metadata']['items'] = []

    if metadata:
      instance['metadata']['items'].extend(metadata)

    if startup_script:
      startup_script_resource = {
          'key': 'startup-script',
          'value': open(startup_script, 'r').read()
      }
      instance['metadata']['items'].append(startup_script_resource)

    if startup_script_url:
      startup_script_url_resource = {
          'key': 'startup-script-url',
          'value': startup_script_url
      }
      instance['metadata']['items'].append(startup_script_url_resource)

    request = self.service.instances().insert(
        project=self.project_id, zone=zone, body=instance)
    response = self._execute_request(request)
    if response and blocking:
      response = self._blocking_call(response)

    if response and 'error' in response:
      raise ApiOperationError(response['error']['errors'])

    return response

  def list_instances(self, zone=settings.DEFAULT_ZONE, list_filter=None):
    """Lists project instances.

    Args:
      zone: The string zone name.
      list_filter: String filter for list query.

    Returns:
      List of instances matching given filter.
    """
    request = None
    if list_filter:
      request = self.service.instances().list(
          project=self.project_id, zone=zone, filter=list_filter)
    else:
      request = self.service.instances().list(
          project=self.project_id, zone=zone)
    response = self._execute_request(request)
    if response and 'items' in response:
      return response['items']
    return []

  def stop_instance(self,
                    instance_name,
                    zone=settings.DEFAULT_ZONE,
                    blocking=True):
    """Stops instances.

    Args:
      instance_name: String name for the instance.
      zone: The string zone name.
      blocking: Whether the function will wait for the operation to complete.

    Returns:
      Dictionary response representing the operation.

    Raises:
      ApiOperationError: Operation contains an error message.
    """
    if not instance_name:
      print 'instance_name required.'
      return

    request = self.service.instances().delete(
        project=self.project_id, zone=zone, instance=instance_name)
    response = self._execute_request(request)
    if response and blocking:
      response = self._blocking_call(response)

    if response and 'error' in response:
      raise ApiOperationError(response['error']['errors'])

    return response

  def _blocking_call(self, response):
    """Blocks until the operation status is done for the given operation.

    Args:
      response: the response from the API call.
    Returns:
      Dictionary response representing the operation.
    """
    status = response['status']
    while status != 'DONE' and response:
      operation_id = response['name']
      if 'zone' in response:
        zone = response['zone'].rsplit('/', 1)[-1]
        request = self.service.zoneOperations().get(
            project=self.project_id, zone=zone, operation=operation_id)
      else:
        request = self.service.globalOperations().get(
            project=self.project_id, operation=operation_id)
      response = self._execute_request(request)
      if response:
        status = response['status']
    return response

  def _execute_request(self, request):
    """Helper method to execute API requests.

    Args:
      request: the API request to execute.

    Returns:
      Dictionary response representing the operation if successful.
    """
    try:
      response = request.execute()
    except AccessTokenRefreshError:
      print 'Access token is invalid.'
      traceback.print_exc()
      return
    except HttpError:
      print 'Http response was not 2xx.'
      traceback.print_exc()
      return
    except HttpLib2Error:
      print 'Transport error.'
      traceback.print_exc()
      return
    except:
      print 'Unexpected error occured.'
      traceback.print_exc()
      return
    return response


class Error(Exception):
  """Base class for exceptions in this module."""
  pass


class ApiOperationError(Error):
  """Raised when an API operation contains an error."""

  def __init__(self, error_list):
    """Initialize the Error.

    Args:
      error_list: the list of errors from the operation.
    """
    super(ApiOperationError, self).__init__()
    self.error_list = error_list

  def __str__(self):
    """String representation of the error."""
    return repr(self.error_list)
