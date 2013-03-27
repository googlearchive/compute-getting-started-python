# Copyright 2012 Google Inc. All Rights Reserved.
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

import logging
try:
  import simplejson as json
except:
  import json
import time
import traceback

from apiclient.discovery import build
from apiclient.errors import HttpError
from httplib2 import HttpLib2Error
from oauth2client.client import AccessTokenRefreshError

SETTINGS_FILE = 'settings.json'


class Gce(object):
  """Demonstrates some of the image and instance API functionality.

  Attributes:
    settings: A dictionary of application settings from the settings.json file.
    service: An apiclient.discovery.Resource object for Compute Engine.
    project_id: The string Compute Engine project ID.
    project_url: The string URL of the Compute Engine project.
  """

  def __init__(self, auth_http, project_id=None):
    """Initialize the Gce object.

    Args:
      auth_http: an authorized instance of httplib2.Http.
      project_id: the API console project name.
    """

    self.settings = json.loads(open(SETTINGS_FILE, 'r').read())

    self.service = build(
        'compute', self.settings['compute']['api_version'], http=auth_http)

    self.gce_url = 'https://www.googleapis.com/compute/%s/projects/' % (
        self.settings['compute']['api_version'])

    self.project_id = None
    if not project_id:
      self.project_id = self.settings['project']
    else:
      self.project_id = project_id
    self.project_url = self.gce_url + self.project_id

  def start_instance(self,
                     instance_name,
                     zone=None,
                     machine_type=None,
                     image=None,
                     network=None,
                     disk=None,
                     service_email=None,
                     scopes=None,
                     metadata=None,
                     startup_script=None,
                     startup_script_url=None,
                     blocking=True):
    """Start an instance with the given name and settings.

    Args:
      instance_name: String name for instance.
      zone: The string zone name.
      machine_type: The string machine type.
      image: The string name of a custom image.
      network: The string network.
      disk: The string disk.
      service_email: The string service email.
      scopes: List of string scopes.
      metadata: List of metadata dictionaries.
      startup_script: The filename of a startup script.
      startup_script_url: Url of a startup script.
      blocking: Whether the function will wait for the operation to complete.

    Returns:
      Dictionary response representing the operation.

    Raises:
      ApiOperationError: Operation contains an error message.
    """

    if not instance_name:
      logging.error('instance_name required.')
      return

    # Set required instance fields with defaults if not provided.
    instance = {}
    instance['name'] = instance_name
    if not machine_type:
      machine_type = self.settings['compute']['machine_type']
    instance['machineType'] = '%s/global/machineTypes/%s' % (
        self.project_url, machine_type)
    if not image:
      instance['image'] = '%sgoogle/global/images/%s' % (
          self.gce_url, self.settings['compute']['image'])
    else:
      instance['image'] = '%s/global/images/%s' % (
          self.project_url, image)
    if not network:
      network = self.settings['compute']['network']
    instance['networkInterfaces'] = [{
        'accessConfigs': [{'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}],
        'network': '%s/global/networks/%s' % (self.project_url, network)}]

    # Set optional fields with provided values.
    if disk:
      instance['disks'] = [{'type': disk}]
    if service_email and scopes:
      instance['serviceAccounts'] = [{'email': service_email, 'scopes': scopes}]

    # Set the instance metadata if provided.
    instance['metadata'] = {}
    instance['metadata']['items'] = []
    if metadata:
      instance['metadata']['items'].extend(metadata)

    # Set the instance startup script if provided.
    if startup_script:
      startup_script_resource = {
          'key': 'startup-script', 'value': open(startup_script, 'r').read()}
      instance['metadata']['items'].append(startup_script_resource)

    # Set the instance startup script URL if provided.
    if startup_script_url:
      startup_script_url_resource = {
          'key': 'startup-script-url', 'value': startup_script_url}
      instance['metadata']['items'].append(startup_script_url_resource)

    # Send the request.
    if not zone:
      zone = self.settings['compute']['zone']
    request = self.service.instances().insert(
        project=self.project_id, zone=zone, body=instance)
    response = self._execute_request(request)
    if response and blocking:
      response = self._blocking_call(response)

    if response and 'error' in response:
      raise ApiOperationError(response['error']['errors'])

    return response

  def list_instances(self, zone=None, list_filter=None):
    """Lists project instances.

    Args:
      zone: The string zone name.
      list_filter: String filter for list query.

    Returns:
      List of instances matching given filter.
    """

    if not zone:
      zone = self.settings['compute']['zone']

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
                    zone=None,
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
      logging.error('instance_name required.')
      return

    if not zone:
      zone = self.settings['compute']['zone']

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
        logging.info(
            'Waiting until operation is DONE. Current status: %s', status)
        if status != 'DONE':
          time.sleep(3)

    return response

  def _execute_request(self, request):
    """Helper method to execute API requests.

    Args:
      request: the API request to execute.

    Returns:
      Dictionary response representing the operation if successful.

    Raises:
      ApiError: Error occurred during API call.
    """

    try:
      response = request.execute()
    except AccessTokenRefreshError, e:
      logging.error('Access token is invalid.')
      raise ApiError(e)
    except HttpError, e:
      logging.error('Http response was not 2xx.')
      raise ApiError(e)
    except HttpLib2Error, e:
      logging.error('Transport error.')
      raise ApiError(e)
    except Exception, e:
      logging.error('Unexpected error occured.')
      traceback.print_stacktrace()
      raise ApiError(e)

    return response


class Error(Exception):
  """Base class for exceptions in this module."""
  pass


class ApiError(Error):
  """Error occurred during API call."""
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
