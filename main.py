import re
from dataclasses import dataclass

from phonenumbers import parse, format_number, PhoneNumberFormat
from phonenumbers.phonenumberutil import region_code_for_country_code, country_code_for_region

COUNTRY = "ES"
COUNTRY_CODE = 34


@dataclass
class DcPhonenumber:
    country: str = COUNTRY
    national_number: str = ""
    country_code: int = COUNTRY_CODE

    @property
    def e164(self):
        return f"+{self.country_code}{self.national_number}" if self.national_number else ""


class SanitizerPhoneNumber:
    country: str = COUNTRY
    country_code: int = COUNTRY_CODE
    phone_number: str = ""

    def __init__(self, phone_number: str, default_country: str | None = None):
        assert isinstance(phone_number, str), "phone_number must be a string"

        self._set_phone_number(phone_number, default_country)
        self._set_country(default_country)

    def sanitize(self):
        if not self.phone_number:
            return DcPhonenumber(country=self.country, country_code=self.country_code)
        try:
            instance = parse(self.phone_number, self.country)
            number_sanitize = self._clean(format_number(instance, PhoneNumberFormat.NATIONAL))
            return DcPhonenumber(
                country=self.country,
                national_number=number_sanitize,
                country_code=instance.country_code,
            )
        except Exception:
            return DcPhonenumber(
                country=self.country,
                national_number=self._clean(self.phone_number),
                country_code=self.country_code,
            )

    def _set_phone_number(self, phone_number: str, default_country: str | None = None):
        phone_number = self._clean(phone_number)
        phone_number = re.sub(r"^\++", "+", phone_number)
        phone_number = re.sub(r"^(?:\+?(?:00|011))", lambda m: "+" if m.group(0).startswith("+") else "", phone_number)

        if not phone_number.startswith("+") and default_country:
            country_code = country_code_for_region(default_country)
            if country_code:
                phone_number = f"+{country_code}{phone_number}"

        self.phone_number = phone_number if phone_number.startswith("+") else f"+{phone_number}"

    def _set_country(self, default_country: str | None = None):
        if default_country:
            default_country = str(default_country).upper()
            country_code = country_code_for_region(default_country)
            if country_code and country_code > 0:
                self.country = default_country
                self.country_code = country_code

        try:
            instance = parse(self.phone_number, self.country)
            self.country = region_code_for_country_code(instance.country_code)
            self.country_code = instance.country_code
        except Exception:
            self.country = COUNTRY
            self.country_code = COUNTRY_CODE

    def _clean(self, value: str):
        return re.sub(r"[^\d+]", "", str(value)).strip()

    @staticmethod
    def country_to_country_code(country: str):
        country = str(country).upper()
        return country_code_for_region(country) or COUNTRY_CODE

    @staticmethod
    def country_code_to_country(country_code: int):
        return region_code_for_country_code(country_code) or COUNTRY
