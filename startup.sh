#!/bin/bash
apt-get -y install imagemagick
IMAGE_URL=$(curl http://metadata/0.1/meta-data/attributes/url)
TEXT=$(curl http://metadata/0.1/meta-data/attributes/text)
CS_BUCKET=$(curl http://metadata/0.1/meta-data/attributes/cs-bucket)
mkdir image-output
cd image-output
wget $IMAGE_URL
convert * -pointsize 30 -fill black -annotate +10+40 $TEXT output.png
gsutil cp -a public-read output.png gs://$CS_BUCKET/output.png
