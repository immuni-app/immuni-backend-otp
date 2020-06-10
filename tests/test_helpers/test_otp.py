#   Copyright (C) 2020 Presidenza del Consiglio dei Ministri.
#   Please refer to the AUTHORS file for more information.
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU Affero General Public License for more details.
#   You should have received a copy of the GNU Affero General Public License
#   along with this program. If not, see <https://www.gnu.org/licenses/>.

import json
from datetime import date
from hashlib import sha256

from aioredis.commands import StringCommandsMixin
from pytest import raises

from immuni_common.core.exceptions import OtpCollisionException
from immuni_common.models.dataclasses import OtpData
from immuni_otp.core import config
from immuni_otp.core.managers import managers
from immuni_otp.helpers.otp import store

_OTP = "an_otp_code"
_OTP_SHA = sha256(_OTP.encode("utf-8")).hexdigest()
_OTP_DATA = OtpData(symptoms_started_on=date(year=2020, month=12, day=10))
_OTP_DATA_SERIALIZED = json.dumps({"symptoms_started_on": "2020-12-10"})


async def test_store_success() -> None:
    key = f"~otp:{_OTP_SHA}"
    assert await managers.otp_redis.get(key=key) is None
    await store(otp=_OTP, otp_data=_OTP_DATA)
    actual = await managers.otp_redis.get(key=key)
    expected = _OTP_DATA_SERIALIZED
    assert actual == expected
    ttl = await managers.otp_redis.ttl(key=key)
    assert 0 < ttl <= config.OTP_EXPIRATION_SECONDS


async def test_store_failure_on_existent_key() -> None:
    key = f"~otp:{_OTP_SHA}"
    did_set = await managers.otp_redis.set(
        key=key, value=_OTP_DATA_SERIALIZED, exist=StringCommandsMixin.SET_IF_NOT_EXIST
    )
    assert did_set is True
    with raises(OtpCollisionException):
        await store(otp=_OTP, otp_data=_OTP_DATA)
