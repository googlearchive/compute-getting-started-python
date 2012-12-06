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

import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run

import gce

CLIENT_SECRETS = 'client_secrets.json'
OAUTH2_STORAGE = 'oauth2.dat'
GCE_SCOPE = 'https://www.googleapis.com/auth/compute'

PROJECT_ID = '<your_project_id>'
IMAGE_URL = '<image_url>'
CS_BUCKET = '<your_cloud_storage_bucket>'


def main():
  """Perform OAuth 2 authorization, then start, list, and stop instance(s)."""

  # Perform OAuth 2.0 authorization.
  flow = flow_from_clientsecrets(CLIENT_SECRETS, scope=GCE_SCOPE)
  storage = Storage(OAUTH2_STORAGE)
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run(flow, storage)
  http = httplib2.Http()
  auth_http = credentials.authorize(http)

  gce_helper = gce.Gce(auth_http, PROJECT_ID)

  # Start an image with a local start-up script.
  instance_name = 'startup-script-demo'
  try:
    gce_helper.start_instance(
        instance_name, startup_script='startup.sh', metadata=[{
            'key': 'url',
            'value': IMAGE_URL
        }, {
            'key': 'text',
            'value': 'AWESOME'
        }, {
            'key': 'cs-bucket',
            'value': CS_BUCKET
        }])
  except gce.ApiOperationError as e:
    print 'Error starting instance'
    print e
    return

  instances = gce_helper.list_instances()
  for instance in instances:
    print instance['name']

  print 'Visit http://commondatastorage.googleapis.com/%s/output.png' % (
      CS_BUCKET)
  print 'It might take a minute for the output.png file to show up.'
  raw_input('Hit Enter when done to shutdown instance')

  # Stop the instance.
  try:
    gce_helper.stop_instance(instance_name)
  except gce.ApiOperationError as e:
    print 'Error stopping instance'
    print e
    return


if __name__ == '__main__':
  main()
