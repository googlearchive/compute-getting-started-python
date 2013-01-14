# Getting Started with Compute Engine and the Google Python Client Library

Google Compute Engine features a RESTful API that allows developers to run virtual machines in the cloud. This sample python command-line application demonstrates how to access the Compute Engine API using the Google Python API Client Library. For more information about the library, read the [Getting Started: Google Python Client Library documentation][1].

To run the demo:

- Update the client_secrets.json file with your client id and secret found in the [Google APIs Console][2].
- Update the global variables at the top of the helloworld.py file with your project information.
- Run the sample using the command:

python helloworld.py

Demo steps:

- Create an instance with a start up script and metadata. 
- Print out the URL where the modified image will be written.
- The start up script executes these steps on the instance:
    - Installs Image Magick on the machine.
    - Downloads the image from the URL provided in the metadata.
    - Adds the text provided in the metadata to the image.
    - Copies the edited image to Cloud Storage.
- After recieving input from the user, shut down the instance.

## Products
- [Google Compute Engine][3]
- [Google Cloud Storage][4]

## Language
- [Python][5]

## Dependencies
- [Google APIs Client Library for Python][6]

[1]: https://developers.google.com/compute/docs/api/python_guide
[2]: https://code.google.com/apis/console
[3]: https://developers.google.com/compute
[4]: https://developers.google.com/storage
[5]: https://python.org
[6]: http://code.google.com/p/google-api-python-client/
