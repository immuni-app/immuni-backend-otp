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

from typing import Optional

from aioredis import Redis, create_redis_pool

from immuni_common.core.exceptions import ImmuniException
from immuni_common.core.managers import BaseManagers
from immuni_otp.core import config


class Managers(BaseManagers):
    """
    Collection of managers, lazily initialized.
    """

    _otp_redis: Optional[Redis] = None

    @property
    def otp_redis(self) -> Redis:
        """
        Return the Redis manager to store OtpData.

        :return: the Redis manager to store OtpData.
        :raise: ImmuniException if the manager is not initialized.
        """
        if self._otp_redis is None:
            raise ImmuniException("Cannot use the Redis manager before initialising it.")
        return self._otp_redis

    async def initialize(self) -> None:
        """
        Initialize managers on demand.
        """
        await super().initialize()
        self._otp_redis = await create_redis_pool(
            address=config.OTP_CACHE_REDIS_URL,
            encoding="utf-8",
            maxsize=config.OTP_CACHE_REDIS_MAX_CONNECTIONS,
        )

    async def teardown(self) -> None:
        """
        Perform teardown actions (e.g., close open connections).
        """
        await super().teardown()
        if self._otp_redis is not None:
            self._otp_redis.close()
            await self._otp_redis.wait_closed()


managers = Managers()
