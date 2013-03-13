#!/bin/bash
# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
apt-get -y install imagemagick
IMAGE_URL=$(curl http://metadata/computeMetadata/v1beta1/instance/attributes/url)
TEXT=$(curl http://metadata/computeMetadata/v1beta1/instance/attributes/text)
CS_BUCKET=$(curl http://metadata/computeMetadata/v1beta1/instance/attributes/cs-bucket)
mkdir image-output
cd image-output
wget $IMAGE_URL
convert * -pointsize 30 -fill black -annotate +10+40 $TEXT output.png
gsutil cp -a public-read output.png gs://$CS_BUCKET/output.png
