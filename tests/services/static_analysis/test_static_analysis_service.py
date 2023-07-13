from pathlib import Path
from unittest.mock import MagicMock

import click
import pytest
import requests
import responses
from responses import matchers

from codecov_cli.services.staticanalysis import run_analysis_entrypoint
from codecov_cli.services.staticanalysis.types import FileAnalysisRequest


class TestStaticAnalysisService:
    @pytest.mark.asyncio
    async def test_static_analysis_service(self, mocker):
        mock_file_finder = mocker.patch(
            "codecov_cli.services.staticanalysis.select_file_finder"
        )
        mock_send_upload_put = mocker.patch(
            "codecov_cli.services.staticanalysis.send_single_upload_put"
        )

        # Doing it this way to support Python 3.7
        async def side_effect(*args, **kwargs):
            return MagicMock()

        mock_send_upload_put.side_effect = side_effect

        files_found = map(
            lambda filename: FileAnalysisRequest(str(filename), Path(filename)),
            [
                "samples/inputs/sample_001.py",
                "samples/inputs/sample_002.py",
            ],
        )
        mock_file_finder.return_value.find_files = MagicMock(return_value=files_found)
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                "https://api.codecov.io/staticanalysis/analyses",
                json={
                    "external_id": "externalid",
                    "filepaths": [
                        {
                            "state": "created",
                            "filepath": "samples/inputs/sample_001.py",
                            "raw_upload_location": "http://storage-url",
                        },
                        {
                            "state": "valid",
                            "filepath": "samples/inputs/sample_002.py",
                            "raw_upload_location": "http://storage-url",
                        },
                    ],
                },
                status=200,
                match=[
                    matchers.header_matcher({"Authorization": "Repotoken STATIC_TOKEN"})
                ],
            )
            rsps.add(
                responses.POST,
                "https://api.codecov.io/staticanalysis/analyses/externalid/finish",
                status=204,
                match=[
                    matchers.header_matcher({"Authorization": "Repotoken STATIC_TOKEN"})
                ],
            )

            await run_analysis_entrypoint(
                config={},
                folder=".",
                numberprocesses=1,
                pattern="*.py",
                token="STATIC_TOKEN",
                commit="COMMIT",
                should_force=False,
                folders_to_exclude=[],
                enterprise_url=None,
            )
        mock_file_finder.assert_called_with({})
        mock_file_finder.return_value.find_files.assert_called()
        assert mock_send_upload_put.call_count == 1
        args, _ = mock_send_upload_put.call_args
        assert args[2] == {
            "state": "created",
            "filepath": "samples/inputs/sample_001.py",
            "raw_upload_location": "http://storage-url",
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "finish_endpoint_response,expected",
        [
            (500, "Codecov is having problems"),
            (400, "some problem with the submitted information"),
        ],
    )
    async def test_static_analysis_service_finish_fails_status_code(
        self, mocker, finish_endpoint_response, expected
    ):
        mock_file_finder = mocker.patch(
            "codecov_cli.services.staticanalysis.select_file_finder"
        )
        mock_send_upload_put = mocker.patch(
            "codecov_cli.services.staticanalysis.send_single_upload_put"
        )

        # Doing it this way to support Python 3.7
        async def side_effect(*args, **kwargs):
            return MagicMock()

        mock_send_upload_put.side_effect = side_effect

        files_found = map(
            lambda filename: FileAnalysisRequest(str(filename), Path(filename)),
            [
                "samples/inputs/sample_001.py",
                "samples/inputs/sample_002.py",
            ],
        )
        mock_file_finder.return_value.find_files = MagicMock(return_value=files_found)
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                "https://api.codecov.io/staticanalysis/analyses",
                json={
                    "external_id": "externalid",
                    "filepaths": [
                        {
                            "state": "created",
                            "filepath": "samples/inputs/sample_001.py",
                            "raw_upload_location": "http://storage-url",
                        },
                        {
                            "state": "valid",
                            "filepath": "samples/inputs/sample_002.py",
                            "raw_upload_location": "http://storage-url",
                        },
                    ],
                },
                status=200,
                match=[
                    matchers.header_matcher({"Authorization": "Repotoken STATIC_TOKEN"})
                ],
            )
            rsps.add(
                responses.POST,
                "https://api.codecov.io/staticanalysis/analyses/externalid/finish",
                status=finish_endpoint_response,
                match=[
                    matchers.header_matcher({"Authorization": "Repotoken STATIC_TOKEN"})
                ],
            )
            with pytest.raises(click.ClickException, match=expected):
                await run_analysis_entrypoint(
                    config={},
                    folder=".",
                    numberprocesses=1,
                    pattern="*.py",
                    token="STATIC_TOKEN",
                    commit="COMMIT",
                    should_force=False,
                    folders_to_exclude=[],
                    enterprise_url=None,
                )
        mock_file_finder.assert_called_with({})
        mock_file_finder.return_value.find_files.assert_called()
        assert mock_send_upload_put.call_count == 1
        args, _ = mock_send_upload_put.call_args
        assert args[2] == {
            "state": "created",
            "filepath": "samples/inputs/sample_001.py",
            "raw_upload_location": "http://storage-url",
        }

    @pytest.mark.asyncio
    async def test_static_analysis_service_finish_fails_request_exception(self, mocker):
        mock_file_finder = mocker.patch(
            "codecov_cli.services.staticanalysis.select_file_finder"
        )
        mock_send_upload_put = mocker.patch(
            "codecov_cli.services.staticanalysis.send_single_upload_put"
        )

        # Doing it this way to support Python 3.7
        async def side_effect(*args, **kwargs):
            return MagicMock()

        mock_send_upload_put.side_effect = side_effect

        files_found = map(
            lambda filename: FileAnalysisRequest(str(filename), Path(filename)),
            [
                "samples/inputs/sample_001.py",
                "samples/inputs/sample_002.py",
            ],
        )
        mock_file_finder.return_value.find_files = MagicMock(return_value=files_found)
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                "https://api.codecov.io/staticanalysis/analyses",
                json={
                    "external_id": "externalid",
                    "filepaths": [
                        {
                            "state": "created",
                            "filepath": "samples/inputs/sample_001.py",
                            "raw_upload_location": "http://storage-url",
                        },
                        {
                            "state": "valid",
                            "filepath": "samples/inputs/sample_002.py",
                            "raw_upload_location": "http://storage-url",
                        },
                    ],
                },
                status=200,
                match=[
                    matchers.header_matcher({"Authorization": "Repotoken STATIC_TOKEN"})
                ],
            )
            rsps.add(
                responses.POST,
                "https://api.codecov.io/staticanalysis/analyses/externalid/finish",
                body=requests.RequestException(),
            )
            with pytest.raises(click.ClickException, match="Unable to reach Codecov"):
                await run_analysis_entrypoint(
                    config={},
                    folder=".",
                    numberprocesses=1,
                    pattern="*.py",
                    token="STATIC_TOKEN",
                    commit="COMMIT",
                    should_force=False,
                    folders_to_exclude=[],
                    enterprise_url=None,
                )
        mock_file_finder.assert_called_with({})
        mock_file_finder.return_value.find_files.assert_called()
        assert mock_send_upload_put.call_count == 1
        args, _ = mock_send_upload_put.call_args
        assert args[2] == {
            "state": "created",
            "filepath": "samples/inputs/sample_001.py",
            "raw_upload_location": "http://storage-url",
        }

    @pytest.mark.asyncio
    async def test_static_analysis_service_should_force_option(self, mocker):
        mock_file_finder = mocker.patch(
            "codecov_cli.services.staticanalysis.select_file_finder"
        )
        mock_send_upload_put = mocker.patch(
            "codecov_cli.services.staticanalysis.send_single_upload_put"
        )

        # Doing it this way to support Python 3.7
        async def side_effect(*args, **kwargs):
            return MagicMock()

        mock_send_upload_put.side_effect = side_effect

        files_found = map(
            lambda filename: FileAnalysisRequest(str(filename), Path(filename)),
            [
                "samples/inputs/sample_001.py",
                "samples/inputs/sample_002.py",
            ],
        )
        mock_file_finder.return_value.find_files = MagicMock(return_value=files_found)
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                "https://api.codecov.io/staticanalysis/analyses",
                json={
                    "external_id": "externalid",
                    "filepaths": [
                        {
                            "state": "created",
                            "filepath": "samples/inputs/sample_001.py",
                            "raw_upload_location": "http://storage-url",
                        },
                        {
                            "state": "valid",
                            "filepath": "samples/inputs/sample_002.py",
                            "raw_upload_location": "http://storage-url",
                        },
                    ],
                },
                status=200,
                match=[
                    matchers.header_matcher({"Authorization": "Repotoken STATIC_TOKEN"})
                ],
            )
            rsps.add(
                responses.POST,
                "https://api.codecov.io/staticanalysis/analyses/externalid/finish",
                status=204,
                match=[
                    matchers.header_matcher({"Authorization": "Repotoken STATIC_TOKEN"})
                ],
            )
            await run_analysis_entrypoint(
                config={},
                folder=".",
                numberprocesses=1,
                pattern="*.py",
                token="STATIC_TOKEN",
                commit="COMMIT",
                should_force=True,
                folders_to_exclude=[],
                enterprise_url=None,
            )
        mock_file_finder.assert_called_with({})
        mock_file_finder.return_value.find_files.assert_called()
        assert mock_send_upload_put.call_count == 2

    @pytest.mark.asyncio
    async def test_static_analysis_service_no_upload(self, mocker):
        mock_file_finder = mocker.patch(
            "codecov_cli.services.staticanalysis.select_file_finder"
        )
        mock_send_upload_put = mocker.patch(
            "codecov_cli.services.staticanalysis.send_single_upload_put"
        )

        # Doing it this way to support Python 3.7
        async def side_effect(*args, **kwargs):
            return MagicMock()

        mock_send_upload_put.side_effect = side_effect

        files_found = map(
            lambda filename: FileAnalysisRequest(str(filename), Path(filename)),
            [
                "samples/inputs/sample_001.py",
                "samples/inputs/sample_002.py",
            ],
        )
        mock_file_finder.return_value.find_files = MagicMock(return_value=files_found)
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                "https://api.codecov.io/staticanalysis/analyses",
                json={
                    "external_id": "externalid",
                    "filepaths": [
                        {
                            "state": "valid",
                            "filepath": "samples/inputs/sample_001.py",
                            "raw_upload_location": "http://storage-url",
                        },
                        {
                            "state": "valid",
                            "filepath": "samples/inputs/sample_002.py",
                            "raw_upload_location": "http://storage-url",
                        },
                    ],
                },
                status=200,
                match=[
                    matchers.header_matcher({"Authorization": "Repotoken STATIC_TOKEN"})
                ],
            )
            rsps.add(
                responses.POST,
                "https://api.codecov.io/staticanalysis/analyses/externalid/finish",
                status=204,
                match=[
                    matchers.header_matcher({"Authorization": "Repotoken STATIC_TOKEN"})
                ],
            )

            await run_analysis_entrypoint(
                config={},
                folder=".",
                numberprocesses=1,
                pattern="*.py",
                token="STATIC_TOKEN",
                commit="COMMIT",
                should_force=False,
                folders_to_exclude=[],
                enterprise_url=None,
            )
        mock_file_finder.assert_called_with({})
        mock_file_finder.return_value.find_files.assert_called()
        assert mock_send_upload_put.call_count == 0
