"""Simple Google Drive API wrapper.

Examples:
    >>> from googledrive import Service
    >>> with Service(credentials).files() as gdrive:
    ...   file_content = gdrive.read(('folderA', 'subfolder1'), 'filename')
    ...   gdrive.write(('folderB', 'subfolder2'), 'filename.txt',
    ...                file_content, 'text/plain')
"""

from ._service import Service
from ._files import Files

__version__ = '0.1.1'
__author__ = 'skitschy'

__all__ = ['Service', 'Files']
