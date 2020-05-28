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

from datetime import date
from http import HTTPStatus

from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic_openapi import doc

from immuni_common.core.exceptions import OtpCollisionException, SchemaValidationException
from immuni_common.helpers.cache import cache
from immuni_common.helpers.sanic import json_response, validate
from immuni_common.helpers.swagger import doc_exception
from immuni_common.models.dataclasses import OtpData
from immuni_common.models.enums import Location
from immuni_common.models.marshmallow.fields import IsoDate, OtpCode
from immuni_common.models.swagger import HeaderImmuniContentTypeJson
from immuni_otp.helpers.otp import store
from immuni_otp.models.swagger import OtpBody

bp = Blueprint("otp", url_prefix="/otp")


@bp.route("", methods=["POST"], version=1)
@doc.summary("Authorise OTP (caller: HIS).")
@doc.description(
    "The provided OTP authorises the upload of the Mobile Client’s TEKs. This API will not be "
    "publicly exposed, to prevent unauthorised users from reaching it. "
    "Authentication for having the OTP Service and the HIS trust each other will be configured at "
    "the infrastructure level. "
    "The payload also contains the start date of the symptoms, so that the Exposure Ingestion "
    "Service can compute the Transmission Risk for each uploaded TEK."
)
@doc.consumes(OtpBody, location="body")
@doc.consumes(HeaderImmuniContentTypeJson(), location="header", required=True)
@doc.response(
    HTTPStatus.NO_CONTENT.value, None, description="OTP successfully authorised.",
)
@doc_exception(SchemaValidationException)
@doc_exception(OtpCollisionException)
@validate(
    location=Location.JSON, otp=OtpCode(), symptoms_started_on=IsoDate(),
)
@cache(no_store=True)
async def authorize_otp(request: Request, otp: str, symptoms_started_on: date) -> HTTPResponse:
    """
    Authorize the upload of the Mobile Client’s TEKs.

    :param request: the HTTP request object.
    :param otp: the OTP code to authorize.
    :param symptoms_started_on: the date of the first symptoms.
    :return: 204 on OTP successfully authorized, 400 on BadRequest, 409 on OTP already authorized.
    """
    await store(otp=otp, otp_data=OtpData(symptoms_started_on=symptoms_started_on))
    return json_response(body=None, status=HTTPStatus.NO_CONTENT)
