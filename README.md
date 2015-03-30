# Getting Started with Compute Engine and the Google Python Client Library

[Google Compute Engine](https://cloud.google.com/compute/) features a [RESTful API](https://cloud.google.com/compute/docs/api/getting-started)
that allows developers to run virtual machines in the cloud. This sample python command-line application demonstrates how to access the Compute Engine API using the
[Google Python API Client Library](https://developers.google.com/api-client-library/python/).


## Pre-requisites

1. Create a project on the [Google Developers Console](https://console.developers.google.com) and [enable billing](https://console.developers.google.com/project/_/settings).
2. Install the [Google Cloud SDK](https://cloud.google.com/sdk/)

```bash
curl https://sdk.cloud.google.com | bash
gcloud auth login
gcloud config set project your-project-id
```
3. Install dependencies using [pip](https://pypi.python.org/pypi/pip)

```bash
pip install -r requirements.txt
```

## Running the sample

```bash
python main.py
```

The sample will:
 1. Create an instance with a start up script and metadata.
 2. Print out the URL where the modified image will be written.
 3. Waits for input from the user and then delete the instance.

The start up script executes these steps on the instance:
 1. Installs Image Magick on the machine.
 2. Downloads the image from the URL provided in the metadata.
 3. Adds the text provided in the metadata to the image.
 4. Copies the edited image to Cloud Storage.


## Products
- [Google Compute Engine](https://developers.google.com/compute)
- [Google Cloud Storage](https://developers.google.com/storage)


## Contributing changes

* See [CONTRIBUTING.md](CONTRIBUTING.md)


## Licensing

* See [LICENSE](LICENSE)
