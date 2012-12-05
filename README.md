# Getting Started with Compute Engine and the Google Python Client Library

Google Compute Engine features a RESTful API that allows developers to run virtual machines in the cloud. This sample python command-line application demonstrates how to access the Compute Engine API using the Google Python API Client Library. For more information about the library, read the [Getting Started: Google Python Client Library documentation][1].

This demo:

- Starts an instance with a start up script and metadata. 
- Waits for the startup script, it does the following:
    - Installs Image Magick on the machine.
    - Downloads the image at the URL provided in the metadata.
    - Adds the text provided in the metadata to the image.
    - Copies the edited image to Cloud Storage.
- Shuts down the instance.

## Products
- [Google Compute Engine][2]
- [Google Cloud Storage][5]

## Language
- [Python][3]

## Dependencies
- [Google APIs Client Library for Python][4]

[1]: https://developers.google.com/compute/docs/api/python_guide
[2]: https://developers.google.com/compute
[3]: https://python.org
[4]: http://code.google.com/p/google-api-python-client/
[5]: https://developers.google.com/storage
