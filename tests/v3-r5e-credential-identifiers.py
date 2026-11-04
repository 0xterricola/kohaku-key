#!/usr/bin/env python3
"""V3-R5-E public identifier contract; no secrets."""

from dataclasses import dataclass, replace
import re

ADDRESS = re.compile(r"0x[0-9a-f]{40}\Z")
DECIMAL = re.compile(r"0|[1-9][0-9]*\Z")
MAX_HARDENED = 2**31


@dataclass(frozen=True)
class CredentialId:
    chain_id: int
    entrypoint: str
    account: int
    deposit: int
    role: str
    secret_index: int

    def validate(self):
        assert type(self.chain_id) is int
        assert 0 < self.chain_id < 2**256
        assert ADDRESS.fullmatch(self.entrypoint)

        for value in (
            self.account,
            self.deposit,
            self.secret_index,
        ):
            assert type(value) is int
            assert 0 <= value < MAX_HARDENED

        assert (
            (self.role == "deposit" and
             self.secret_index == 0)
            or
            (self.role == "withdraw" and
             self.secret_index >= 1)
        )
        return self

    def canonical(self):
        self.validate()
        return ":".join(map(str, (
            "kkid", "v1", "privacy-pools-v1",
            "eip155", self.chain_id,
            self.entrypoint, self.account,
            self.deposit, self.role,
            self.secret_index,
        )))

    def sdk_coordinates(self):
        self.validate()
        return {
            "chainId": self.chain_id,
            "entrypointAddress": int(
                self.entrypoint, 16
            ),
            "accountIndex": self.account,
            "depositIndex": self.deposit,
            "secretIndex": self.secret_index,
            "role": self.role,
        }


def parse(value):
    parts = value.split(":")
    assert len(parts) == 10
    assert parts[:4] == [
        "kkid", "v1",
        "privacy-pools-v1", "eip155"
    ]

    for index in (4, 6, 7, 9):
        assert DECIMAL.fullmatch(parts[index])

    identifier = CredentialId(
        chain_id=int(parts[4]),
        entrypoint=parts[5],
        account=int(parts[6]),
        deposit=int(parts[7]),
        role=parts[8],
        secret_index=int(parts[9]),
    )

    identifier.validate()
    assert identifier.canonical() == value
    return identifier


base = CredentialId(
    chain_id=11155111,
    entrypoint=(
        "0x34a2068192b1297f2a7f85d7d8cde66f8f0921cb"
    ),
    account=0,
    deposit=17,
    role="deposit",
    secret_index=0,
)

canonical = base.canonical()

assert parse(canonical) == base
assert parse(canonical).canonical() == canonical
print("PASS: Canonical identifier round-trip")

coords = base.sdk_coordinates()

assert coords["chainId"] == 11155111
assert coords["accountIndex"] == 0
assert coords["depositIndex"] == 17
assert coords["secretIndex"] == 0
print("PASS: Existing SDK coordinate mapping")

variants = [
    base,
    replace(base, chain_id=1),
    replace(base, entrypoint="0x" + "12" * 20),
    replace(base, account=1),
    replace(base, deposit=18),
    replace(
        base,
        role="withdraw",
        secret_index=1,
    ),
    replace(
        base,
        role="withdraw",
        secret_index=2,
    ),
]

assert len({
    item.canonical() for item in variants
}) == len(variants)

print("PASS: Context and withdrawal separation")

invalid = [
    canonical.replace("kkid:v1", "kkid:v2"),
    canonical.replace(
        "privacy-pools-v1", "railgun"
    ),
    canonical.replace(":11155111:", ":011155111:"),
    canonical.replace(":17:deposit:", ":-1:deposit:"),
    canonical.replace(":deposit:0", ":withdraw:0"),
    canonical.replace(":deposit:0", ":deposit:1"),
    canonical.replace(":0:17:", ":2147483648:17:"),
    canonical.replace(
        "0x34a206", "0X34a206"
    ),
]

for value in invalid:
    try:
        parse(value)
    except (AssertionError, ValueError):
        continue
    raise AssertionError(
        "Invalid identifier accepted"
    )

print("PASS: Invalid and ambiguous identifiers rejected")
print("PASS: V3-R5-E architecture contract checkpoint")
