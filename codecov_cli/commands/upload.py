import logging
import os
import pathlib
import typing
import uuid

import click

from codecov_cli.fallbacks import CodecovOption, FallbackFieldEnum
from codecov_cli.helpers.options import global_options
from codecov_cli.services.upload import do_upload_logic

logger = logging.getLogger("codecovcli")


def _turn_env_vars_into_dict(ctx, params, value):
    return dict((v, os.getenv(v, None)) for v in value)


_global_upload_options = [
    click.option(
        "--report-code",
        help="The code of the report. If unsure, leave default",
        default="default",
    ),
    click.option(
        "--network-root-folder",
        help="Root folder from which to consider paths on the network section",
        type=click.Path(path_type=pathlib.Path),
        default=pathlib.Path.cwd,
        show_default="Current working directory",
    ),
    click.option(
        "-s",
        "--dir",
        "--coverage-files-search-root-folder",
        "coverage_files_search_root_folder",
        help="Folder where to search for coverage files",
        type=click.Path(path_type=pathlib.Path),
        default=pathlib.Path.cwd,
        show_default="Current Working Directory",
    ),
    click.option(
        "--exclude",
        "--coverage-files-search-exclude-folder",
        "coverage_files_search_exclude_folders",
        help="Folders to exclude from search",
        type=click.Path(path_type=pathlib.Path),
        multiple=True,
        default=[],
    ),
    click.option(
        "-f",
        "--file",
        "--coverage-files-search-direct-file",
        "coverage_files_search_explicitly_listed_files",
        help="Explicit files to upload. These will be added to the coverage files found for upload. If you wish to only upload the specified files, please consider using --disable-search to disable uploading other files.",
        type=click.Path(path_type=pathlib.Path),
        multiple=True,
        default=[],
    ),
    click.option(
        "--disable-search",
        help="Disable search for coverage files. This is helpful when specifying what files you want to uload with the --file option.",
        is_flag=True,
        default=False,
    ),
    click.option(
        "--disable-file-fixes",
        help="Disable file fixes to ignore common lines from coverage (e.g. blank lines or empty brackets)",
        is_flag=True,
        default=False,
    ),
    click.option(
        "-b",
        "--build",
        "--build-code",
        "build_code",
        cls=CodecovOption,
        help="Specify the build number manually",
        fallback_field=FallbackFieldEnum.build_code,
    ),
    click.option(
        "--build-url",
        "build_url",
        cls=CodecovOption,
        help="The URL of the build where this is running",
        fallback_field=FallbackFieldEnum.build_url,
    ),
    click.option(
        "--job-code",
        cls=CodecovOption,
        fallback_field=FallbackFieldEnum.job_code,
    ),
    click.option(
        "-n",
        "--name",
        help="Custom defined name of the upload. Visible in Codecov UI",
    ),
    click.option(
        "-B",
        "--branch",
        help="Branch to which this commit belongs to",
        cls=CodecovOption,
        fallback_field=FallbackFieldEnum.branch,
    ),
    click.option(
        "-P",
        "--pr",
        "--pull-request-number",
        "pull_request_number",
        help="Specify the pull request number mannually. Used to override pre-existing CI environment variables",
        cls=CodecovOption,
        fallback_field=FallbackFieldEnum.pull_request_number,
    ),
    click.option(
        "-e",
        "--env",
        "--env-var",
        "env_vars",
        multiple=True,
        callback=_turn_env_vars_into_dict,
        help="Specify environment variables to be included with this build.",
    ),
    click.option(
        "-F",
        "--flag",
        "flags",
        multiple=True,
        default=[],
        help="Flag the upload to group coverage metrics. Multiple flags allowed.",
    ),
    click.option(
        "--plugin",
        "plugin_names",
        multiple=True,
        default=["xcode", "gcov", "pycoverage"],
    ),
    click.option(
        "-d",
        "--dry-run",
        "dry_run",
        is_flag=True,
        help="Don't upload files to Codecov",
    ),
    click.option(
        "--legacy",
        "--use-legacy-uploader",
        "use_legacy_uploader",
        is_flag=True,
        help="Use the legacy upload endpoint",
    ),
    click.option(
        "--handle-no-reports-found",
        "handle_no_reports_found",
        is_flag=True,
        help="Raise no excpetions when no coverage reports found.",
    ),
]


def global_upload_options(func):
    for option in reversed(_global_upload_options):
        func = option(func)
    return func


@click.command()
@global_upload_options
@global_options
@click.pass_context
def do_upload(
    ctx: click.Context,
    commit_sha: str,
    report_code: str,
    build_code: typing.Optional[str],
    build_url: typing.Optional[str],
    job_code: typing.Optional[str],
    env_vars: typing.Dict[str, str],
    flags: typing.List[str],
    name: typing.Optional[str],
    network_root_folder: pathlib.Path,
    coverage_files_search_root_folder: pathlib.Path,
    coverage_files_search_exclude_folders: typing.List[pathlib.Path],
    coverage_files_search_explicitly_listed_files: typing.List[pathlib.Path],
    disable_search: bool,
    disable_file_fixes: bool,
    token: typing.Optional[uuid.UUID],
    plugin_names: typing.List[str],
    branch: typing.Optional[str],
    slug: typing.Optional[str],
    pull_request_number: typing.Optional[str],
    use_legacy_uploader: bool,
    fail_on_error: bool,
    dry_run: bool,
    git_service: typing.Optional[str],
    handle_no_reports_found: bool,
):
    versioning_system = ctx.obj["versioning_system"]
    codecov_yaml = ctx.obj["codecov_yaml"] or {}
    cli_config = codecov_yaml.get("cli", {})
    ci_adapter = ctx.obj.get("ci_adapter")
    enterprise_url = ctx.obj.get("enterprise_url")
    logger.debug(
        "Starting upload processing",
        extra=dict(
            extra_log_attributes=dict(
                commit_sha=commit_sha,
                report_code=report_code,
                build_code=build_code,
                build_url=build_url,
                job_code=job_code,
                env_vars=env_vars,
                flags=flags,
                name=name,
                network_root_folder=network_root_folder,
                coverage_files_search_root_folder=coverage_files_search_root_folder,
                coverage_files_search_exclude_folders=coverage_files_search_exclude_folders,
                coverage_files_search_explicitly_listed_files=coverage_files_search_explicitly_listed_files,
                plugin_names=plugin_names,
                token=token,
                branch=branch,
                slug=slug,
                pull_request_number=pull_request_number,
                git_service=git_service,
                enterprise_url=enterprise_url,
                disable_search=disable_search,
                disable_file_fixes=disable_file_fixes,
                handle_no_reports_found=handle_no_reports_found,
            )
        ),
    )
    do_upload_logic(
        cli_config,
        versioning_system,
        ci_adapter,
        commit_sha=commit_sha,
        report_code=report_code,
        build_code=build_code,
        build_url=build_url,
        job_code=job_code,
        env_vars=env_vars,
        flags=flags,
        name=name,
        network_root_folder=network_root_folder,
        coverage_files_search_root_folder=coverage_files_search_root_folder,
        coverage_files_search_exclude_folders=list(
            coverage_files_search_exclude_folders
        ),
        coverage_files_search_explicitly_listed_files=list(
            coverage_files_search_explicitly_listed_files
        ),
        plugin_names=plugin_names,
        token=token,
        branch=branch,
        slug=slug,
        pull_request_number=pull_request_number,
        use_legacy_uploader=use_legacy_uploader,
        fail_on_error=fail_on_error,
        dry_run=dry_run,
        git_service=git_service,
        enterprise_url=enterprise_url,
        disable_search=disable_search,
        handle_no_reports_found=handle_no_reports_found,
        disable_file_fixes=disable_file_fixes,
    )
