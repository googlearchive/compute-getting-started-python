# Copyright 2013 Google Inc. All Rights Reserved.
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

IMAGE_URL = 'http://storage.googleapis.com/gce-demo-input/photo.jpg'
IMAGE_TEXT = 'Ready for dessert?'
INSTANCE_NAME = 'startup-script-demo'
DISK_NAME = INSTANCE_NAME + '-disk'
INSERT_ERROR = 'Error inserting %(name)s.'
DELETE_ERROR = """
Error deleting %(name)s. %(name)s might still exist; You can use
the console (http://cloud.google.com/console) to delete %(name)s.
"""


def delete_resource(delete_method, *args):
  """Delete a Compute Engine resource using the supplied method and args.

  Args:
    delete_method: The gce.Gce method for deleting the resource.
  """

  resource_name = args[0]
  logging.info('Deleting %s' % resource_name)

  try:
    delete_method(*args)
  except (gce.ApiError, gce.ApiOperationError, ValueError) as e:
    logging.error(DELETE_ERROR, {'name': resource_name})
    logging.error(e)


def main():
  """Perform OAuth 2 authorization, then start, list, and stop instance(s)."""

  logging.basicConfig(level=logging.INFO)

  # Load the settings for this sample app.
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

  # Retrieve user input.
  image_url = raw_input(
      'Enter the URL of an image [Defaults to %s]: ' % IMAGE_URL)
  if not image_url:
    image_url = IMAGE_URL
  image_text = raw_input(
      'Enter text to add to the image [Defaults to "%s"]: ' % IMAGE_TEXT)
  if not image_text:
    image_text = IMAGE_TEXT
  bucket = raw_input('Enter a Cloud Storage bucket [Required]: ')
  if not bucket:
    logging.error('Cloud Storage bucket required.')
    return

  # Initialize gce.Gce.
  gce_helper = gce.Gce(auth_http, project_id=settings['project'])

  # Create a Persistent Disk (PD), which is used as a boot disk.
  try:
    gce_helper.create_disk(DISK_NAME)
  except (gce.ApiError, gce.ApiOperationError, ValueError, Exception) as e:
    logging.error(INSERT_ERROR, {'name': DISK_NAME})
    logging.error(e)
    return

  # Start an instance with a local start-up script and boot disk.
  logging.info('Starting GCE instance')
  try:
    gce_helper.start_instance(
        INSTANCE_NAME,
        DISK_NAME,
        service_email=settings['compute']['service_email'],
        scopes=settings['compute']['scopes'],
        startup_script='startup.sh',
        metadata=[
            {'key': 'url', 'value': image_url},
            {'key': 'text', 'value': image_text},
            {'key': 'cs-bucket', 'value': bucket}])
  except (gce.ApiError, gce.ApiOperationError, ValueError, Exception) as e:
    # Delete the disk in case the instance fails to start.
    delete_resource(gce_helper.delete_disk, DISK_NAME)
    logging.error(INSERT_ERROR, {'name': INSTANCE_NAME})
    logging.error(e)
    return
  except gce.DiskDoesNotExistError as e:
    logging.error(INSERT_ERROR, {'name': INSTANCE_NAME})
    logging.error(e)
    return

  # List all running instances.
  logging.info('These are your running instances:')
  instances = gce_helper.list_instances()
  for instance in instances:
    logging.info(instance['name'])

  logging.info(
      'Visit http://storage.googleapis.com/%s/output.png.' % bucket)
  logging.info('It might take a minute for the output.png file to show up.')
  raw_input('Hit Enter when done to shutdown instance.')

  # Stop the instance.
  delete_resource(gce_helper.stop_instance, INSTANCE_NAME)

  # Delete the disk.
  delete_resource(gce_helper.delete_disk, DISK_NAME)

  logging.info('Remember to delete the output.png file in ' + bucket)

if __name__ == '__main__':
  main()
