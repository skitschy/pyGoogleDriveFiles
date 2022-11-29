from ._files import Files

from googleapiclient.discovery import build


class Service:
    """Simple wrapper class for Google Drive API."""

    SCOPE = 'https://www.googleapis.com/auth/drive'
    """OAuth scope string for Google Drive API."""

    def __init__(self, credentials, *args):
        """Init Service.

        Args:
            credentials (oauth2client.Credentials or
                google.auth.credentials.Credentials):
                The credentials to be used for authentication.
            *args: Optional arguments to ``googleapiclient.discovery.build``.
        """
        self._drive = build('drive', 'v3', credentials=credentials, *args)

    def files(self, max_retry: int = 3, retry_interval: float = 1):
        """Return a :py:class:`Files` object, \
            a simple wrapper for files resource of Google Drive API.

        Args:
            max_retry: The maximum number of retries for API calls.
            retry_interval: The retry interval in seconds.
        """
        return Files(self._drive, max_retry, retry_interval)
