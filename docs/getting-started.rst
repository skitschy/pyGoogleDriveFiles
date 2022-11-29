Getting Started
================

Firstly, create drive API client and
get a wrapper :py:class:`googledrive.Files` for the file Resource.

    >>> import google.auth
    >>> from googledrive import Service
    >>> creds, _ = google.auth.default()
    >>> gdrive = Service(creds).files()

Use :py:func:`googledrive.Files.list` without any parameters
to get the list of all files and folders in your `My Drive`.

    >>> all_file_list = gdrive.list()
    >>> for file in all_file_list:
    ...     print(file.get('name'))

You can also list files in ``subfolderA`` in ``folder1`` in your `My Drive`.

    >>> filelist = gdrive.list(('folder1', 'subfolderA'))

Use :py:func:`googledrive.Files.read` with the path and the name of the file.

    >>> file_content_str = gdrive.read(('folder1', 'subfolderA'), 'filename')

You can use the ID of the parent folder instead of the path.

    >>> file_content_str = gdrive.read('folder_id_str', 'filename')

Use :py:func:`googledrive.Files.write` to create or update a file.

    >>> gdrive.write(('folder1', 'subfolderA'), 'filename', 'content_str', 'text/plain')
    >>> gdrive.write('folder_id_str', 'filename', 'content_str', 'text/plain')

Use :py:func:`googledrive.Files.delete_file_id` with the file ID to be deleted.

    >>> gdrive.delete_file_id('file_id')
