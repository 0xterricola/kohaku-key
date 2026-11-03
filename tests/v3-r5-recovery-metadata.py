#!/usr/bin/env python3
"""V3-R5 recovery metadata validation; synthetic public fixtures only."""

import copy
import json
import re

FORMAT = "kohaku-key/v3-recovery/1"
METHOD = "keycard4-bip85-hmac-sha256/1"
BIP85_PATH = "m/83696968'/128169'/32'/0'"
DOMAIN = "kohaku-key/v3-r3/privacy-pools-v1/deriveAt"
SDK_PREFIX = "m/28784'/1'"


def exact_keys(value, expected):
    if type(value) is not dict or set(value) != set(expected):
        raise ValueError("invalid metadata field set")


def integer(value, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError("invalid integer metadata")


def validate(metadata):
    exact_keys(metadata, ("format", "derivation", "context"))

    if metadata["format"] != FORMAT:
        raise ValueError("unsupported recovery format")

    derivation = metadata["derivation"]
    exact_keys(
        derivation,
        (
            "method",
            "bip85_path",
            "bip85_length",
            "domain",
            "sdk_prefix",
            "account_index",
        ),
    )

    expected = {
        "method": METHOD,
        "bip85_path": BIP85_PATH,
        "bip85_length": 32,
        "domain": DOMAIN,
        "sdk_prefix": SDK_PREFIX,
        "account_index": 0,
    }

    for field, value in expected.items():
        if type(derivation[field]) is not type(value):
            raise ValueError("invalid derivation field type")
        if derivation[field] != value:
            raise ValueError("derivation contract mismatch")

    context = metadata["context"]
    exact_keys(
        context,
        ("chain_id", "entrypoint_address", "scan_from_block"),
    )

    integer(context["chain_id"], 1)
    integer(context["scan_from_block"])

    address = context["entrypoint_address"]
    if type(address) is not str or not re.fullmatch(
        r"0x[0-9a-fA-F]{40}", address
    ):
        raise ValueError("invalid entrypoint address")

    return True


def fixture():
    # All values below are synthetic, public test metadata.
    return {
        "format": FORMAT,
        "derivation": {
            "method": METHOD,
            "bip85_path": BIP85_PATH,
            "bip85_length": 32,
            "domain": DOMAIN,
            "sdk_prefix": SDK_PREFIX,
            "account_index": 0,
        },
        "context": {
            "chain_id": 11155111,
            "entrypoint_address": "0x" + "11" * 20,
            "scan_from_block": 0,
        },
    }


def main():
    original = fixture()
    assert validate(original)
    assert validate(json.loads(json.dumps(original)))
    print("PASS: Public metadata round-trip")

    changes = [
        lambda m: m.update(format="unsupported/2"),
        lambda m: m.update(seed="prohibited"),
        lambda m: m["derivation"].update(pin="prohibited"),
        lambda m: m["derivation"].update(domain="different"),
        lambda m: m["derivation"].update(bip85_path="m/0'"),
        lambda m: m["derivation"].update(account_index=1),
        lambda m: m["derivation"].update(bip85_length=64),
        lambda m: m["derivation"].update(sdk_prefix="m/0'"),
        lambda m: m["context"].update(chain_id=True),
        lambda m: m["context"].update(chain_id=0),
        lambda m: m["context"].update(scan_from_block=-1),
        lambda m: m["context"].update(entrypoint_address="bad"),
        lambda m: m["context"].update(nullifier="prohibited"),
        lambda m: m["context"].pop("entrypoint_address"),
    ]

    for index, change in enumerate(changes, 1):
        candidate = copy.deepcopy(original)
        change(candidate)

        try:
            validate(candidate)
        except ValueError:
            continue

        raise AssertionError(
            f"Unsafe or incompatible metadata accepted: case {index}"
        )

    print(f"PASS: {len(changes)} invalid metadata cases rejected")
    print("PASS: Derivation contract version locked")
    print("PASS: No credential material required by schema")
    print("PASS: V3-R5-A recovery metadata checkpoint")


if __name__ == "__main__":
    main()
