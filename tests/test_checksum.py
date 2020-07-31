# -*- coding: utf-8 -*-
import os
import shutil
import struct
import tempfile

import pytest
from stdlib_utils import checksum
from stdlib_utils import compute_crc32_and_write_to_file_head
from stdlib_utils import compute_crc32_bytes_of_large_file
from stdlib_utils import compute_crc32_hex_of_large_file
from stdlib_utils import Crc32ChecksumValidationFailureError
from stdlib_utils import Crc32InFileHeadDoesNotMatchExpectedValueError
from stdlib_utils import get_current_file_abs_directory
from stdlib_utils import validate_file_head_crc32


FILE_FOR_HASHING = os.path.join(
    get_current_file_abs_directory(), "file_for_crc32_hashing.bin"
)

FILE_WITH_CHECKSUM_AT_HEAD = os.path.join(
    get_current_file_abs_directory(), "file_with_crc32_checksum_at_head.bin"
)
FILE_WITH_INCORRECT_CHECKSUM_AT_HEAD = os.path.join(
    get_current_file_abs_directory(), "file_with_incorrect_crc32_checksum_at_head.bin"
)


def test_compute_crc32_bytes_of_large_file__returns_correct_hash():

    expected = b"\xaa\xd1\xc7\xb5"  # from https://emn178.github.io/online-tools/crc32_checksum.html
    actual: bytes
    with open(FILE_FOR_HASHING, "rb") as in_file:
        actual = compute_crc32_bytes_of_large_file(in_file)
    assert actual == expected


def test_compute_crc32_bytes_of_large_file__can_skip_initial_bytes():
    expected = b"\xcf\x05\xc7s"
    actual: bytes
    with open(FILE_FOR_HASHING, "rb") as in_file:
        actual = compute_crc32_bytes_of_large_file(in_file, skip_first_n_bytes=4)
    assert actual == expected


def test_compute_crc32_hex_of_large_file__returns_correct_hash():
    expected = "aad1c7b5"
    actual: str
    with open(FILE_FOR_HASHING, "rb") as in_file:
        actual = compute_crc32_hex_of_large_file(in_file)
    assert actual == expected


def test_compute_crc32_hex_of_large_file__can_skip_initial_bytes():
    expected = "cf05c773"
    actual: str
    with open(FILE_FOR_HASHING, "rb") as in_file:
        actual = compute_crc32_hex_of_large_file(in_file, skip_first_n_bytes=4)
    assert actual == expected


def test_compute_crc32_hex_of_large_file__zero_pads_left_side(mocker):
    mocker.patch.object(
        checksum,
        "compute_crc32_bytes_of_large_file",
        autospec=True,
        return_value=struct.pack(">I", 22),
    )
    actual = compute_crc32_hex_of_large_file(None)

    assert actual == "00000016"


def test_compute_crc32_and_write_to_file_head():
    expected_checksum_bytes = b"\xcf\x05\xc7s"
    with tempfile.TemporaryDirectory() as tmp_dir:
        new_file = os.path.join(tmp_dir, "new_file.h5")
        shutil.copyfile(FILE_FOR_HASHING, new_file)
        with open(new_file, "rb+") as the_file:
            compute_crc32_and_write_to_file_head(the_file)
        with open(new_file, "rb") as in_file:
            actual = in_file.read(4)
            assert actual == expected_checksum_bytes


def test_validate_file_head_crc32__does_not_raise_error_when_correct():
    with open(FILE_WITH_CHECKSUM_AT_HEAD, "rb") as in_file:
        assert validate_file_head_crc32(in_file) is None  # would raise error if failed


def test_validate_file_head_crc32__does_not_raise_error_when_correct_and_expected_checksum_is_correct():
    with open(FILE_WITH_CHECKSUM_AT_HEAD, "rb") as in_file:
        assert (
            validate_file_head_crc32(in_file, expected_checksum="cf05c773") is None
        )  # would raise error if failed


def test_validate_file_head_crc32__raises_error_if_expected_checksum_does_not_match_file_header():
    with open(FILE_WITH_CHECKSUM_AT_HEAD, "rb") as in_file:
        with pytest.raises(
            Crc32InFileHeadDoesNotMatchExpectedValueError,
            match="was aad1c7b5, but the checksum found at the file head is cf05c773",
        ):
            validate_file_head_crc32(in_file, expected_checksum="aad1c7b5")


def test_validate_file_head_crc32__raises_error_if_calculated_checksum_does_not_match_value_in_file_head():
    with open(FILE_WITH_INCORRECT_CHECKSUM_AT_HEAD, "rb") as in_file:
        with pytest.raises(
            Crc32ChecksumValidationFailureError,
            match="was 6e5855e0, but the checksum found at the file head is cf05c773",
        ):
            validate_file_head_crc32(in_file)
