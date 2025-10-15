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
        if not self.national_number:
            return ""
        return f"+{self.country_code}{self.national_number}"


class SanitizerPhoneNumber:
    country: str = COUNTRY
    country_code: int = COUNTRY_CODE
    phone_number: str = ""

    def __init__(self, phone_number: str, default_country: str | None = None):
        assert isinstance(phone_number, str), "phone_number must be a string"

        self._set_phone_number(phone_number)
        self._set_country(default_country)

    def sanitize(self):
        if not self.phone_number:
            return DcPhonenumber(country=self.country, country_code=self.country_code)

        try:
            instance = parse(self.phone_number, self.country)
            number_sanitize = format_number(instance, PhoneNumberFormat.NATIONAL)
            national_number = self._clean(number_sanitize)
            return DcPhonenumber(
                country=self.country,
                national_number=national_number,
                country_code=instance.country_code,
            )
        except Exception:
            return DcPhonenumber(
                country=self.country,
                national_number=self._clean(self.phone_number),
                country_code=self.country_code,
            )

    def _set_phone_number(self, phone_number: str):
        """
        Set self.phone_number to E.164 format if possible.
        """
        phone_number = self._clean(phone_number)
        if phone_number.startswith("00"):
            phone_number = "+" + phone_number[2:]
        elif phone_number.startswith("011"):
            phone_number = "+" + phone_number[3:]
        self.phone_number = f"+{phone_number}" if phone_number.isdigit() else phone_number

    def _set_country(self, default_country: str | None = None):
        """
        Set self.country
        Set self.country_code
        """
        if default_country:
            default_country = str(default_country).upper()
            country_code = country_code_for_region(default_country)
            if country_code:
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
        return str(value).replace(" ", "").replace("+", "").strip()

    @staticmethod
    def country_to_country_code(country: str):
        country = str(country).upper()
        country_code = country_code_for_region(country)
        return country_code if country_code else COUNTRY_CODE

    @staticmethod
    def country_code_to_country(country_code: int):
        country = region_code_for_country_code(country_code)
        return country if country else COUNTRY
