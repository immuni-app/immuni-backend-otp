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

from sanic_openapi import doc


class OtpBody:
    """
    Documentation class for /v1/otp body.
    """

    otp = doc.String(
        "The OTP is formed by 10 uppercase alphanumeric characters, with the last character being a"
        " check digit."
        "<br><br>"
        "To prevent misunderstandings when the user communicates the OTP to the Healthcare "
        "Operator, the characters used in the OTP are limited to the following subset: "
        "`A, E, F, H, I, J, K, L, Q, R, S, U, W, X, Y, Z, 1, 2, 3, 4, 5, 6, 7, 8, 9`. "
        "This leads to 25^9 possible valid combinations (since the last character is computed "
        "deterministically, based on the previous 9 characters)."
        "In case the user decided to use the self-unlock via app, the OTP (CUN) is encoded in "
        "sha256 format.",
        required=True,
    )
    symptoms_started_on = doc.String(
        "The date the patient started having the first symptoms (ISO format, e.g., 2020-02-25).",
        required=True,
    )
    id_transaction = doc.String(
        "The id of the transaction (available only with the self-unlock) received from HIS "
        "service after the request.",
        required=False,
    )
