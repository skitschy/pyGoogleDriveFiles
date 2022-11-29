from typing import List, Dict, Any, Union, Iterator
from io import StringIO
from time import sleep
from functools import reduce

from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError


class Files:
    """Simple wrapper class for the files Resource of Google Drive API."""

    def __init__(self, service,
                 max_retry: int = 3, retry_interval: float = 1):
        """Init Files.

        Args:
            service: Resource for Google Drive API.
            max_retry: The maximum number of retries for API calls.
            retry_interval: The retry interval in seconds.
        """
        self.max_retry = max_retry
        self.retry_interval = retry_interval
        self.drivefiles = self.__retry(lambda: service.files())

    def __enter__(self):
        """Enter."""
        return self

    def __exit__(self, *_):
        """Exit."""
        self.close()

    def close(self) -> None:
        """Close API connection."""
        self.drivefiles.close()

    def list(self, path: Union[str, List[str]] = None,
             query: str = None, fields: str = None) -> List[Dict[str, Any]]:
        """List or searches the files in a path.

        Args:
            path: The path ID string, the list of path names, or None.
            query: A query string for filtering the file results.
            fields: The comma-separated list of the field paths to be included.
        Returns:
            A list of files.
        """
        if isinstance(path, str):
            parent_id = path
        elif path:
            parent_id = self.get_path_id(path)
        else:
            parent_id = None
        return list(self.each_files(parent_id, query, fields))

    def read(self, path: Union[str, List[str]], name: str) -> str:
        """Read the content of a file.

        Args:
            path: The path ID string, or the list of path names.
            name: The file name.
        Returns:
            The file content as a string.
        """
        if isinstance(path, str):
            parent_id = path
        else:
            parent_id = self.get_path_id(path)
        fileid = self.get_id(parent_id, name)
        return self.read_file_id(fileid) if fileid else None

    def write(self, path: Union[str, List[str]], name: str,
              content: str, mimetype: str) -> str:
        """Write the content of a file.

        The file is overwrote if it exists, or created otherwise.

        Args:
            path: The path ID string, or the array of path names.
            name: The file name.
            content: The file content as a string.
            mimetype: The mime-type of the file.
        Returns:
            The file ID string.
        """
        if isinstance(path, str):
            parent_id = path
        else:
            parent_id = self.get_path_id(path)
        fileid = self.get_id(parent_id, name)
        if fileid:
            self.update_file_id(fileid, content, mimetype)
            return fileid
        else:
            return self.create_file(parent_id, name, content, mimetype)

    def each_files(self, parent_id: str = None, query: str = None,
                   fields: str = None) -> Iterator[Dict[str, Any]]:
        """Iterate the files in a path.

        Args:
            parent_id: The path ID string, or None.
            query: A query string for filtering the file results.
            fields: The comma-separated list of the field paths to be included.
        Yields:
            Files.
        """
        if parent_id:
            if query:
                q = f"'{parent_id}' in parents and {query}"
            else:
                q = f"'{parent_id}' in parents"
        else:
            if query:
                q = query
            else:
                q = ''
        if fields and 'nextPageToken' not in fields:
            fields = 'nextPageToken,' + fields
        page_token = None
        while True:
            request = self.drivefiles.list(
                q=q, spaces='drive', fields=fields, pageToken=page_token)
            response = self.__execute(request)
            for file in response.get('files', []):
                yield file
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

    def get_path_id(self, path: List[str], root_id: str = 'root') -> str:
        """Get the file ID of the path.

        Args:
            path: The array of path names.
            root_id: The ID string of the root folder.
        Returns:
            The ID string of the path.
        """
        return reduce(lambda parent, name: self.get_id(parent, name),
                      path, root_id)

    def get_id(self, parent_id: str, name: str) -> str:
        """Get the file ID.

        Args:
            parent_id: The path ID string.
            name: The file name.
        Returns:
            The ID string of the file, or None unless the file exists.
        """
        if parent_id and name:
            request = self.drivefiles.list(
                q=f"'{parent_id}' in parents and name='{name}'",
                spaces='drive', fields="files(id)")
            files = self.__execute(request).get('files', [])
            return next(iter(files), {}).get('id', None)
        else:
            return None

    def create_file(self, parent_id: str, name: str,
                    content: str, mimetype: str) -> str:
        """Create a file.

        Args:
            parent_id: The path ID string.
            name: The file name.
            content: The file content as a string.
            mimetype: The mime-type of the file.
        Returns:
            The ID string of the created file, or None if it fails.
        """
        metadata = {'name': name, 'parents': [parent_id]}
        media = MediaIoBaseUpload(StringIO(content), mimetype=mimetype)
        request = self.drivefiles.create(body=metadata, media_body=media)
        return self.__execute(request).get('id', None)

    def read_file_id(self, file_id: str) -> str:
        """Read the file content.

        Args:
            file_id: The file ID string.
        Returns:
            The file content as a string.
        """
        return self.__execute(self.drivefiles.get_media(fileId=file_id))

    def update_file_id(self, file_id: str,
                       content: str, mimetype: str) -> None:
        """Update the file content.

        Args:
            file_id: The file ID string.
            content: The file content as a string.
            mimetype: The mime-type of the file.
        """
        media = MediaIoBaseUpload(StringIO(content), mimetype=mimetype)
        request = self.drivefiles.update(fileId=file_id, media_body=media)
        self.__execute(request)

    def delete_file_id(self, file_id: str) -> None:
        """Delete a file.

        Args:
            file_id: The file ID string.
        """
        self.__execute(self.drivefiles.delete(fileId=file_id))

    def __execute(self, request):
        return self.__retry(lambda: request.execute())

    def __retry(self, function):
        ctry = 0
        while True:
            try:
                return function()
            except (TimeoutError, HttpError):
                if ctry == self.max_retry:
                    raise
                else:
                    ctry += 1
                    sleep(self.retry_interval)
