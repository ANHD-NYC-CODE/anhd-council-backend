from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from datasets.models import DOBPermitIssuedLegacy


class DownloadFileRetryTests(SimpleTestCase):
    @patch('datasets.utils.BaseDatasetModel.c_models.DataFile')
    @patch('datasets.utils.BaseDatasetModel.files.File')
    @patch('datasets.utils.BaseDatasetModel.tempfile.NamedTemporaryFile')
    @patch('datasets.utils.BaseDatasetModel.time.sleep')
    @patch('datasets.utils.BaseDatasetModel.requests.get')
    def test_retries_on_socrata_429(self, mock_get, mock_sleep, mock_tempfile, mock_file, mock_datafile):
        mock_tempfile.return_value = MagicMock()

        rate_limited = MagicMock()
        rate_limited.status_code = 429
        rate_limited.headers = {'Retry-After': '2'}

        ok_response = MagicMock()
        ok_response.status_code = 200
        ok_response.headers = {}
        ok_response.iter_content.return_value = [b'a,b\n', b'1,2\n']

        mock_get.side_effect = [rate_limited, ok_response]

        with patch.object(DOBPermitIssuedLegacy, 'get_dataset', return_value=MagicMock(name='DOB Permits Issued (Legacy)')):
            DOBPermitIssuedLegacy.download_file('https://example.test/data.csv', file_name='test.csv')

        self.assertEqual(mock_get.call_count, 2)
        mock_sleep.assert_called_once_with(2)
