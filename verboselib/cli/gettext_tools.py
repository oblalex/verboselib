import itertools
import sys

if sys.version_info >= (3, 9):
  List = list
else:
  from typing import List

from pathlib import Path

from .text import normalize_eols
from .text import stringify_path

from .utils import find_executable
from .utils import popen_wrapper
from .utils import print_err


GETTEXT_TOOLS_STATUS_OK = 0
GETTEXT_TOOLS_EXECUTABLES = [
  "xgettext",
  "msguniq",
  "msgmerge",
  "msgattrib",
  "msgfmt",
]


def validate_gettext_tools_exist() -> None:
  for executable_name in GETTEXT_TOOLS_EXECUTABLES:
    if find_executable(executable_name) is None:
      raise OSError(
        f"cannot find executable '{executable_name}': make sure you have GNU "
        f"gettext tools 0.15 or newer installed"
      )


def get_gettext_tool_output(args: List[str]) -> str:
  content, errors, status = popen_wrapper(args)

  if errors:
    if status != GETTEXT_TOOLS_STATUS_OK:
      tool_name = args[0]
      raise RuntimeError(
        f"failed to run gettext tool '{tool_name}' (status={status}): "
        f"{errors}"
      )
    else:
      print_err(errors)

  if content:
    content = normalize_eols(content)

  return content


def _make_xgettext_args(
  source_file_path: Path,
  domain: str,
  keywords: List[str],
  no_wrap: bool,
  no_location: bool,
  extra_args: List[str],
) -> List[str]:

  args = [
    "xgettext",
    "-d", domain,
    "--from-code=UTF-8",
    "--add-comments=Translators",
    "--output=-",
  ]

  args.extend([f"--keyword={x}" for x in keywords])

  if no_wrap:
    args.append("--no-wrap")

  if no_location:
    args.append("--no-location")

  if extra_args:
    args.extend(extra_args)

  args.append(stringify_path(source_file_path))

  return args


def extract_translations(
  source_file_path: Path,
  domain: str,
  keywords: List[str],
  no_wrap: bool,
  no_location: bool,
  xgettext_extra_args: List[str],
) -> str:

  args = _make_xgettext_args(
    source_file_path=source_file_path,
    domain=domain,
    keywords=keywords,
    no_wrap=no_wrap,
    no_location=no_location,
    extra_args=xgettext_extra_args,
  )
  return get_gettext_tool_output(args)


def strip_translations_header(translations: str) -> str:
  """
  Strip header from translations generated by ``xgettext``.

  Header consists of multiple lines separated from the body by an empty line.

  """
  return "\n".join(itertools.dropwhile(len, translations.splitlines()))


def _make_msguniq_args(
  pot_file_path: Path,
  no_wrap: bool,
  no_location: bool,
  extra_args: List[str],
) -> List[str]:

  args = [
    "msguniq",
    "--to-code=utf-8",
  ]

  if no_wrap:
    args.append("--no-wrap")

  if no_location:
    args.append("--no-location")

  if extra_args:
    args.extend(extra_args)

  args.append(stringify_path(pot_file_path))

  return args


def extract_unique_messages(
  pot_file_path: Path,
  no_wrap: bool,
  no_location: bool,
  msguniq_extra_args: List[str],
) -> str:

  args = _make_msguniq_args(
    pot_file_path=pot_file_path,
    no_wrap=no_wrap,
    no_location=no_location,
    extra_args=msguniq_extra_args,
  )
  return get_gettext_tool_output(args)


def _make_msgmerge_args(
  po_file_path: Path,
  pot_file_path: Path,
  no_wrap: bool,
  no_location: bool,
  extra_args: List[str],
) -> List[str]:

  args = [
    "msgmerge",
    "-q",
    "--previous",
  ]

  if no_wrap:
    args.append("--no-wrap")

  if no_location:
    args.append("--no-location")

  if extra_args:
    args.extend(extra_args)

  args.append(stringify_path(po_file_path))
  args.append(stringify_path(pot_file_path))

  return args


def merge_new_and_existing_translations(
  po_file_path: Path,
  pot_file_path: Path,
  no_wrap: bool,
  no_location: bool,
  msgmerge_extra_args: List[str],
) -> str:

  args = _make_msgmerge_args(
    po_file_path=po_file_path,
    pot_file_path=pot_file_path,
    no_wrap=no_wrap,
    no_location=no_location,
    extra_args=msgmerge_extra_args,
  )
  return get_gettext_tool_output(args)


def _make_msgattrib_args(
  po_file_path: Path,
  no_wrap: bool,
  no_location: bool,
  extra_args: List[str],
) -> List[str]:

  args = [
    "msgattrib",
    "--no-obsolete",
  ]

  if no_wrap:
    args.append("--no-wrap")

  if no_location:
    args.append("--no-location")

  if extra_args:
    args.extend(extra_args)

  po_file_path_str = stringify_path(po_file_path)

  args.extend([
    "-o",
    po_file_path_str,
    po_file_path_str,
  ])

  return args


def remove_obsolete_translations(
  po_file_path: Path,
  no_wrap: bool,
  no_location: bool,
  msgattrib_extra_args: List[str],
) -> str:

  args = _make_msgattrib_args(
    po_file_path=po_file_path,
    no_wrap=no_wrap,
    no_location=no_location,
    extra_args=msgattrib_extra_args,
  )
  _ = get_gettext_tool_output(args)


def _make_msgfmt_args(
  mo_file_path: Path,
  po_file_path: Path,
  fuzzy: bool,
  extra_args: List[str],
) -> List[str]:

  args = [
    "msgfmt",
    "--check-format",
  ]

  if fuzzy:
    args.append("-f")

  if extra_args:
    args.extend(extra_args)

  args.extend([
    "-o",
    stringify_path(mo_file_path),
    stringify_path(po_file_path),
  ])

  return args


def compile_translations(
  mo_file_path: Path,
  po_file_path: Path,
  fuzzy: bool,
  msgfmt_extra_args: List[str],
) -> None:

  args = _make_msgfmt_args(
    mo_file_path=mo_file_path,
    po_file_path=po_file_path,
    fuzzy=fuzzy,
    extra_args=msgfmt_extra_args,
  )
  _ = get_gettext_tool_output(args)
