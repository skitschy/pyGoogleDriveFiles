"""Unittest for googledrive.Files."""

import unittest
from unittest.mock import MagicMock, patch

from googledrive import Service
from googleapiclient.http import MediaUpload


class TestFiles(unittest.TestCase):
    """Test case for googledrive.Files."""

    def test_init(self):
        """Test __init__."""
        self._get_files()

    def test_get_id(self):
        """Test get_id."""
        FILE_ID = 'file-id'
        files, files_mock = self._get_files()
        list_execute_mock = self._assign_execute_mock(
            files_mock.list, dict(files=[dict(id=FILE_ID)])
        )
        file_id = files.get_id(None, 'filename')
        files_mock.list.assert_not_called()
        file_id = files.get_id('parent', 'filename')
        self.assertEqual(file_id, FILE_ID)
        files_mock.list.assert_called_once()
        self._assert_called_with_kwargs(
            files_mock.list,
            q="'parent' in parents and name='filename'"
        )
        list_execute_mock.assert_called_once_with()

    def test_create_file(self):
        """Test create_file."""
        FILE_ID = 'file-id'
        PARENT_ID = 'parent_id'
        FILENAME = 'name'
        CONTENT = 'content'
        MIMETYPE = 'mimetype'
        files, files_mock = self._get_files()
        create_execute_mock = self._assign_execute_mock(
            files_mock.create, dict(id=FILE_ID)
        )
        file_id = files.create_file(PARENT_ID, FILENAME, CONTENT, MIMETYPE)
        self.assertEqual(file_id, FILE_ID)
        files_mock.create.assert_called_once()
        self._assert_called_with_kwargs(
            files_mock.create,
            body={'name': FILENAME, 'parents': [PARENT_ID]},
            media_body=lambda arg: (
                self.assertIsInstance(arg, MediaUpload),
                self.assertEqual(arg.mimetype(), MIMETYPE),
                self.assertEqual(arg.getbytes(0, len(CONTENT)+1), CONTENT)
            )
        )
        create_execute_mock.assert_called_once_with()

    def test_read_file_id(self):
        """Test read_file_id."""
        FILE_ID = 'file-id'
        CONTENT = 'content'
        files, files_mock = self._get_files()
        get_media_execute_mock = self._assign_execute_mock(
            files_mock.get_media, CONTENT
        )
        content = files.read_file_id(FILE_ID)
        self.assertEqual(content, CONTENT)
        files_mock.get_media.assert_called_once()
        self._assert_called_with_kwargs(
            files_mock.get_media,
            fileId=FILE_ID
        )
        get_media_execute_mock.assert_called_once_with()

    def test_update_file_id(self):
        """Test update_file_id."""
        FILE_ID = 'file-id'
        CONTENT = 'content'
        MIMETYPE = 'mimetype'
        files, files_mock = self._get_files()
        update_execute_mock = self._assign_execute_mock(
            files_mock.update, None
        )
        files.update_file_id(FILE_ID, CONTENT, MIMETYPE)
        files_mock.update.assert_called_once()
        self._assert_called_with_kwargs(
            files_mock.update,
            fileId=FILE_ID,
            media_body=lambda arg: (
                self.assertIsInstance(arg, MediaUpload),
                self.assertEqual(arg.mimetype(), MIMETYPE),
                self.assertEqual(arg.getbytes(0, len(CONTENT)+1), CONTENT)
            )
        )
        update_execute_mock.assert_called_once_with()

    def test_delete_file_id(self):
        """Test delete_file_id."""
        FILE_ID = 'file-id'
        files, files_mock = self._get_files()
        delete_execute_mock = self._assign_execute_mock(
            files_mock.delete, None
        )
        files.delete_file_id(FILE_ID)
        files_mock.delete.assert_called_once()
        self._assert_called_with_kwargs(
            files_mock.delete,
            fileId=FILE_ID
        )
        delete_execute_mock.assert_called_once_with()

    def test_each_files(self):
        """Test each_files."""
        FILE_IDS = ['file-id1', 'file-id2', 'file-id3']
        NEXT_PAGE_TOKEN = 'next_page_token'
        files, files_mock = self._get_files()
        list_execute_mock = self._assign_execute_mock(
            files_mock.list, None
        )
        list_execute_mock.side_effect = [
            dict(files=[dict(id=FILE_IDS[0])], nextPageToken=NEXT_PAGE_TOKEN),
            dict(files=[dict(id=FILE_IDS[1]), dict(id=FILE_IDS[2])]),
        ]
        for idx, file in enumerate(files.each_files()):
            self.assertDictEqual(file, dict(id=FILE_IDS[idx]))
        self.assertEqual(files_mock.list.call_count, 2)
        call_args_list = files_mock.list.call_args_list
        self._assert_kwargs(
            call_args_list[0].kwargs,
            q='', spaces='drive', fields=None, pageToken=None
        )
        self._assert_kwargs(
            call_args_list[1].kwargs,
            q='', spaces='drive', fields=None, pageToken=NEXT_PAGE_TOKEN
        )
        self.assertEqual(list_execute_mock.call_count, 2)

        list_execute_mock = self._assign_execute_mock(
            files_mock.list, dict(files=[dict(id=FILE_IDS[0])])
        )
        files_mock.list.reset_mock()
        next(files.each_files('parent'))
        files_mock.list.assert_called_once()
        self._assert_called_with_kwargs(
            files_mock.list,
            q="'parent' in parents", spaces='drive',
            fields=None, pageToken=None
        )
        files_mock.list.reset_mock()
        next(files.each_files('parent', 'query', 'fields'))
        files_mock.list.assert_called_once()
        self._assert_called_with_kwargs(
            files_mock.list,
            q="'parent' in parents and query", spaces='drive',
            fields='nextPageToken,fields', pageToken=None
        )

    def test_get_path_id(self):
        """Test get_path_id."""
        TOPID = 'topid'
        PATH = ('path1', 'path2', 'path3')
        PATH_IDS = ['pathid1', 'pathid2', 'pathid3']
        files, files_mock = self._get_files()
        list_execute_mock = self._assign_execute_mock(
            files_mock.list, None
        )
        list_execute_mock.side_effect = [
            dict(files=[dict(id=fileid)]) for fileid in PATH_IDS
        ]
        path_id = files.get_path_id(PATH, TOPID)
        self.assertEqual(path_id, PATH_IDS[2])
        call_args_list = files_mock.list.call_args_list
        for idx, parent in enumerate([TOPID, PATH_IDS[0], PATH_IDS[1]]):
            self._assert_kwargs(
                call_args_list[idx].kwargs,
                q=f"'{parent}' in parents and name='{PATH[idx]}'"
            )
        self.assertEqual(list_execute_mock.call_count, 3)

        PATH_IDS = ['pathid', None]
        list_execute_mock = self._assign_execute_mock(
            files_mock.list, None
        )
        list_execute_mock.side_effect = [
            dict(files=[dict(id=fileid)]) for fileid in PATH_IDS
        ]
        files_mock.list.reset_mock()
        path_id = files.get_path_id(PATH)
        self.assertIsNone(path_id)
        call_args_list = files_mock.list.call_args_list
        for idx, parent in enumerate(['root', PATH_IDS[0]]):
            self._assert_kwargs(
                call_args_list[idx].kwargs,
                q=f"'{parent}' in parents and name='{PATH[idx]}'"
            )
        self.assertEqual(list_execute_mock.call_count, 2)

    def test_list(self):
        """Test list."""
        PATH = ('path1', 'path2')
        PATH_IDS = ['pathid1', 'pathid2']
        FILE_IDS = ['file-id1', 'file-id2']
        files, files_mock = self._get_files()
        list_execute_mock = self._assign_execute_mock(
            files_mock.list,
            dict(files=[dict(id=FILE_IDS[0]), dict(id=FILE_IDS[1])])
        )
        file_list = files.list(PATH_IDS[1], 'query', 'fields')
        self.assertEqual(
            file_list,
            list(map(lambda id: {'id': id}, FILE_IDS))
        )
        files_mock.list.assert_called_once()
        self._assert_called_with_kwargs(
            files_mock.list,
            q=f"'{PATH_IDS[1]}' in parents and query", spaces='drive',
            fields='nextPageToken,fields', pageToken=None
        )

        list_execute_mock = self._assign_execute_mock(
            files_mock.list, None
        )
        list_execute_mock.side_effect = [
            dict(files=[dict(id=PATH_IDS[0])]),
            dict(files=[dict(id=PATH_IDS[1])]),
            dict(files=[dict(id=FILE_IDS[0]), dict(id=FILE_IDS[1])])
        ]
        files_mock.list.reset_mock()
        file_list = files.list(PATH, 'query', 'fields')
        self.assertEqual(
            file_list,
            list(map(lambda id: {'id': id}, FILE_IDS))
        )
        call_args_list = files_mock.list.call_args_list
        for idx, parent in enumerate(['root', PATH_IDS[0]]):
            self._assert_kwargs(
                call_args_list[idx].kwargs,
                q=f"'{parent}' in parents and name='{PATH[idx]}'"
            )
        self._assert_kwargs(
            call_args_list[2].kwargs,
            q=f"'{PATH_IDS[1]}' in parents and query", spaces='drive',
            fields='nextPageToken,fields', pageToken=None
        )
        self.assertEqual(list_execute_mock.call_count, 3)

        list_execute_mock = self._assign_execute_mock(
            files_mock.list,
            dict(files=[dict(id=FILE_IDS[0]), dict(id=FILE_IDS[1])])
        )
        files_mock.list.reset_mock()
        file_list = files.list()
        self.assertEqual(
            file_list,
            list(map(lambda id: {'id': id}, FILE_IDS))
        )
        files_mock.list.assert_called_once()
        self._assert_called_with_kwargs(
            files_mock.list,
            q='', spaces='drive', fields=None, pageToken=None
        )

    def test_read(self):
        """Test read."""
        PATH = ('path1', 'path2')
        PATH_IDS = ['pathid1', 'pathid2']
        FILE_ID = 'file-id'
        CONTENT = 'content'
        files, files_mock = self._get_files()
        list_execute_mock = self._assign_execute_mock(
            files_mock.list, dict(files=[dict(id=FILE_ID)])
        )
        get_media_execute_mock = self._assign_execute_mock(
            files_mock.get_media, CONTENT
        )
        content = files.read(PATH_IDS[1], 'filename')
        self.assertEqual(content, CONTENT)
        files_mock.list.assert_called_once()
        self._assert_called_with_kwargs(
            files_mock.list,
            q=f"'{PATH_IDS[1]}' in parents and name='filename'"
        )
        list_execute_mock.assert_called_once_with()
        files_mock.get_media.assert_called_once()
        self._assert_called_with_kwargs(
            files_mock.get_media,
            fileId=FILE_ID
        )
        get_media_execute_mock.assert_called_once_with()

        list_execute_mock.side_effect = [
            dict(files=[dict(id=PATH_IDS[0])]),
            dict(files=[dict(id=PATH_IDS[1])]),
            dict(files=[dict(id=FILE_ID)])
        ]
        files_mock.list.reset_mock()
        get_media_execute_mock = self._assign_execute_mock(
            files_mock.get_media, CONTENT
        )
        files_mock.get_media.reset_mock()
        content = files.read(PATH, 'filename')
        self.assertEqual(content, CONTENT)
        call_args_list = files_mock.list.call_args_list
        for idx, parent in enumerate(['root', PATH_IDS[0]]):
            self._assert_kwargs(
                call_args_list[idx].kwargs,
                q=f"'{parent}' in parents and name='{PATH[idx]}'"
            )
        self._assert_kwargs(
            call_args_list[2].kwargs,
            q=f"'{PATH_IDS[1]}' in parents and name='filename'"
        )
        self.assertEqual(list_execute_mock.call_count, 3)
        files_mock.get_media.assert_called_once()
        self._assert_called_with_kwargs(
            files_mock.get_media,
            fileId=FILE_ID
        )
        get_media_execute_mock.assert_called_once_with()

    def test_write(self):
        """Test write."""
        PATH = ('path1', 'path2')
        PATH_IDS = ['pathid1', 'pathid2']
        FILE_ID = 'file-id'
        CONTENT = 'content'
        MIMETYPE = 'mimetype'
        files, files_mock = self._get_files()
        list_execute_mock = self._assign_execute_mock(
            files_mock.list, dict(files=[dict(id=FILE_ID)])
        )
        update_execute_mock = self._assign_execute_mock(
            files_mock.update, None
        )
        files.write(PATH_IDS[1], 'filename', CONTENT, MIMETYPE)
        files_mock.list.assert_called_once()
        self._assert_called_with_kwargs(
            files_mock.list,
            q=f"'{PATH_IDS[1]}' in parents and name='filename'"
        )
        list_execute_mock.assert_called_once_with()
        files_mock.update.assert_called_once()
        self._assert_called_with_kwargs(
            files_mock.update,
            fileId=FILE_ID,
            media_body=lambda arg: (
                self.assertIsInstance(arg, MediaUpload),
                self.assertEqual(arg.mimetype(), MIMETYPE),
                self.assertEqual(arg.getbytes(0, len(CONTENT)+1), CONTENT)
            )
        )
        update_execute_mock.assert_called_once_with()

        list_execute_mock.side_effect = [
            dict(files=[dict(id=PATH_IDS[0])]),
            dict(files=[dict(id=PATH_IDS[1])]),
            dict(files=[dict(id=FILE_ID)])
        ]
        files_mock.list.reset_mock()
        update_execute_mock = self._assign_execute_mock(
            files_mock.update, None
        )
        files_mock.update.reset_mock()
        files.write(PATH, 'filename', CONTENT, MIMETYPE)
        call_args_list = files_mock.list.call_args_list
        for idx, parent in enumerate(['root', PATH_IDS[0]]):
            self._assert_kwargs(
                call_args_list[idx].kwargs,
                q=f"'{parent}' in parents and name='{PATH[idx]}'"
            )
        self._assert_kwargs(
            call_args_list[2].kwargs,
            q=f"'{PATH_IDS[1]}' in parents and name='filename'"
        )
        self.assertEqual(list_execute_mock.call_count, 3)
        files_mock.update.assert_called_once()
        self._assert_called_with_kwargs(
            files_mock.update,
            fileId=FILE_ID,
            media_body=lambda arg: (
                self.assertIsInstance(arg, MediaUpload),
                self.assertEqual(arg.mimetype(), MIMETYPE),
                self.assertEqual(arg.getbytes(0, len(CONTENT)+1), CONTENT)
            )
        )
        update_execute_mock.assert_called_once_with()

    # Utility methods
    def _get_files(self):
        service, service_mock = self._get_service()
        files_mock = MagicMock()
        service_mock.files.return_value = files_mock
        files = service.files()
        service_mock.files.assert_called()
        return files, files_mock

    @patch('googledrive._service.build')
    def _get_service(self, mock: MagicMock):
        service_mock = MagicMock()
        mock.return_value = service_mock
        service = Service('credential')
        mock.assert_called()
        return service, service_mock

    def _assign_execute_mock(self, target, execute_return) -> MagicMock:
        mock = MagicMock(**{'execute.return_value': execute_return})
        target.return_value = mock
        return mock.execute

    def _assert_called_with_kwargs(self, method, **kwargs):
        self._assert_kwargs(method.call_args.kwargs, **kwargs)

    def _assert_kwargs(self, called_kwargs, **kwargs):
        for k, v in kwargs.items():
            self.assertIn(k, called_kwargs)
            if callable(v):
                v(called_kwargs[k])
            else:
                self.assertEqual(called_kwargs[k], v)


if __name__ == '__main__':
    unittest.main()
