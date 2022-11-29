# pyGoogleDriveFiles

Python module 'googledrive-files' is
a simple wrapper for the files Resource of Google Drive API.

Features:
* List files and folders.
* Create, read, write, and delete files.


## Requirement

* Python 3.5 or above


## Installation

```sh
pip install googledrive-files
```


## Basic Usage

```python
>>> from googledrive import Service
>>> with Service(credentials).files() as gdrive:
...   file_content = gdrive.read(['dirA', 'subdir1'], 'filename')
...   gdrive.write(['dirB', 'subdir2'], 'filename.txt',
...                file_content, 'text/plain')
```


## Documentation

Documentation is
[available online](https://googledrive-files.readthedocs.io/).
