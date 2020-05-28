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

from hashlib import sha256

from aioredis.commands import StringCommandsMixin

from immuni_common.core.exceptions import OtpCollisionException
from immuni_common.helpers.otp import key_for_otp_sha
from immuni_common.models.dataclasses import OtpData
from immuni_common.models.marshmallow.schemas import OtpDataSchema
from immuni_otp.core import config
from immuni_otp.core.managers import managers


def _key_for_otp(otp: str) -> str:
    """
    Return database key associated with the given OTP.

    :param otp: the OTP whose key is to be computed.
    :return: the database key associated with the given OTP.
    """
    otp_sha = sha256(otp.encode("utf-8")).hexdigest()
    return key_for_otp_sha(otp_sha)


async def store(otp: str, otp_data: OtpData) -> None:
    """
    Store the OtpData associated with the OTP, managing the key and value dump to the database.

    :param otp: the OTP associated with the database entry.
    :param otp_data: the OtpData to store.
    :raises: OtpCollision if the OTP is already in the database.
    """
    did_set = await managers.otp_redis.set(
        key=_key_for_otp(otp),
        value=OtpDataSchema().dumps(otp_data),
        expire=config.OTP_KEY_EXPIRATION_SECONDS,
        exist=StringCommandsMixin.SET_IF_NOT_EXIST,
    )
    if not did_set:
        raise OtpCollisionException()
