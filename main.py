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

"""Google Compute Engine demo using the Google Python Client Library.

Demo steps:

- Create an instance with a start up script and metadata.
- Print out the URL where the modified image will be written.
- The start up script executes these steps on the instance:
    - Installs Image Magick on the machine.
    - Downloads the image from the URL provided in the metadata.
    - Adds the text provided in the metadata to the image.
    - Copies the edited image to Cloud Storage.
- After recieving input from the user, shut down the instance.

To run this demo:
- Edit the client id and secret in the client_secrets.json file.
- Enter your Compute Engine API console project name below.
- Enter the URL of an image in the code below.
- Create a bucket on Google Cloud Storage accessible by your console project:
http://cloud.google.com/products/cloud-storage.html
- Enter the name of the bucket below.
"""

__author__ = 'kbrisbin@google.com (Kathryn Hurley)'

import logging
try:
  import simplejson as json
except:
  import json

import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

import gce


def main():
  """Perform OAuth 2 authorization, then start, list, and stop instance(s)."""

  logging.basicConfig(level=logging.INFO)

  # Load GCE settings.
  settings = json.loads(open(gce.SETTINGS_FILE, 'r').read())

  # Perform OAuth 2.0 authorization flow.
  flow = flow_from_clientsecrets(
      settings['client_secrets'], scope=settings['compute_scope'])
  storage = Storage(settings['oauth_storage'])
  credentials = storage.get()

  # Authorize an instance of httplib2.Http.
  if credentials is None or credentials.invalid:
    credentials = run(flow, storage)
  http = httplib2.Http()
  auth_http = credentials.authorize(http)

  gce_helper = gce.Gce(auth_http, settings['project'])

  # Start an image with a local start-up script.
  logging.info('Starting up an instance')
  instance_name = 'startup-script-demo'
  zone_name = settings['compute']['zone']
  try:
    gce_helper.start_instance(
        instance_name,
	zone=zone_name,
        service_email=settings['compute']['service_email'],
        scopes=settings['compute']['scopes'],
        startup_script='startup.sh',
        metadata=[
            {'key': 'url', 'value': settings['image_url']},
            {'key': 'text', 'value': settings['image_text']},
            {'key': 'cs-bucket', 'value': settings['storage']['bucket']}])
  except gce.ApiError, e:
    logging.error('Error starting instance.')
    logging.error(e)
    return
  except gce.ApiOperationError as e:
    logging.error('Error starting instance')
    logging.error(e)
    return

  # List all running instances.
  logging.info('Here are your running instances:')
  instances = gce_helper.list_instances()
  for instance in instances:
    logging.info(instance['name'])

  logging.info(
      'Visit http://storage.googleapis.com/%s/output.png',
      settings['storage']['bucket'])
  logging.info('It might take a minute for the output.png file to show up.')
  raw_input('Hit Enter when done to shutdown instance')

  # Stop the instance.
  logging.info('Shutting down the instance')
  try:
    gce_helper.stop_instance(instance_name, zone=zone_name)
  except gce.ApiError, e:
    logging.error('Error stopping instance.')
    logging.error(e)
    return
  except gce.ApiOperationError, e:
    logging.error('Error stopping instance')
    logging.error(e)
    return

  logging.info('Remember to delete the output.png file in ' + settings[
      'storage']['bucket'])

if __name__ == '__main__':
  main()
