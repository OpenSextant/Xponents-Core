# -*- coding: utf-8 -*-
from calendar import timegm
from datetime import datetime

import arrow
from opensextant import logger_config
from opensextant.FlexPat import PatternMatch, RegexPatternManager, PatternExtractor

TZINFO = arrow.utcnow().tzinfo

NOW = arrow.now()
YEAR = NOW.year
MILLENNIUM = 2000
CURR_YY = YEAR - MILLENNIUM
FUTURE_YY_THRESHOLD = CURR_YY + 2
MAXIMUM_YEAR = 2040

INVALID_DATE = -1
INVALID_DAY = -2
NO_YEAR = -3
NO_MONTH = -4
NO_DAY = -5

log = logger_config("INFO", pkg=__name__)
_default_locale = None

def format_date(d):
    if isinstance(d, arrow.Arrow):
        return d.format("YYYY-MM-DD")
    else:
        return arrow.get(d).format("YYYY-MM-DD")


def normalize_day(slots):
    """

    :param slots:
    :return:
    """
    if not slots:
        return INVALID_DAY

    day = slots.get("DM2") or slots.get("DOM") or slots.get("DD")
    if day:
        try:
            day = int(day)
            if 0 < day <= 31:
                return day
            else:
                return INVALID_DAY
        except:
            pass
    return INVALID_DATE


def normalize_month_name(slots):
    """

    :param slots:
    :return: name of month in English
    """
    text = slots.get("MON_ABBREV") or slots.get("MON_NAME")
    if not text:
        return INVALID_DATE
    tlen = len(text)
    if tlen < 3 or 11 < tlen:
        return INVALID_DATE
    try:
        short = text[0:3]
        return arrow.get(short, "MMM").month
    except:
        return INVALID_DATE


def normalize_month_num(slots: dict):
    """
    returns month number
    :param slots:
    :return: month num, 1-12
    """
    if not slots:
        return INVALID_DATE

    month_num = slots.get("DM1") or slots.get("MM") or slots.get("MONTH")
    if month_num:
        try:
            num = int(month_num)
            if 0 < num <= 12:
                return num
        except:
            pass
    return INVALID_DATE


def test_european_locale(slots: dict, locale=None):
    """

    :param slots:
    :return:  day, month
    """
    if not ("DM1" in slots and "DM2" in slots):
        return None, None

    # Matched as MDY
    # But we test if DMY is valid based on values.
    try:
        day = int(slots["DM1"])
        mon = int(slots["DM2"])
        # First pass -- if LOCALE == "euro", then assume pattern matches DAY/MON/YYYY
        if locale and locale == "euro":
            if mon <= 12 and  day <= 31:
                return day, mon
            else:
                return -1, -1
        else:
            # Otherwise -- this is a test and we're guessing. Only return
            # a date if date pattern appears to be unambiguous.  03/05   is Mar-5th or May-3rd, for example
            if day > 12 and mon <= 12:
                # Valid match  31/12/...  new year's eve.
                return day, mon
            if day > 12 and mon > 12:
                # Invalid date match for this pattern, e.g., 13/13/, or 30/13/...
                return -1, -1
    except:
        pass
    return None, None

def _get_year(slots:dict) -> str:
    return slots.get("YEAR") or slots.get("YY") or slots.get("YEARYY") or slots.get("YY2")

def normalize_year(slots) -> int:
    if not slots:
        return INVALID_DATE

    year_str = slots.get("YEAR")
    if year_str:
        year = int(year_str)
        if 0 < year < MAXIMUM_YEAR:
            return year

    is_year = False
    year = INVALID_DATE
    yearyy = slots.get("YEARYY")
    yy = slots.get("YY") or slots.get("YY2")
    try:
        if yy:
            year = int(yy)
        elif yearyy:
            is_year = yearyy.startswith("'")
            yearyy = yearyy.strip("'")
            year = int(yearyy)

        # measure len of either slot
        short_year = len(yy or yearyy) < 4

        #  Recent years, just past turn of century.
        if not short_year and year < MAXIMUM_YEAR:
            return year

        # Is short year
        if is_year:
            # class of '17
            # 22 Jun '17
            if 0 <= year <= FUTURE_YY_THRESHOLD:
                return MILLENNIUM + year
            elif year <= 99:
                # Year is '27      -- more likely 1927
                return 1900 + year
        elif FUTURE_YY_THRESHOLD < year <= 99:
            # If not marked as a year and its a bare two-digits, then only accept years
            # Note -- "24"  could be 1924 or 2024,... or Day of month 24.
            return 1900 + year
        else:
            # Default.   Two-digit year, add Millennium
            return MILLENNIUM + year

    except:
        return INVALID_DATE


def normalize_tz(slots):
    """

    :param slots:
    :return: arrow.tzinfo
    """

    try:
        tz = slots.get("SHORT_TZ")
        if tz:
            dt_tz = arrow.get(tz, "Z")
            return dt_tz
        tz = slots.get("LONG_TZ")
        if tz:
            dt_tz = arrow.get(tz, "ZZZ")
            return dt_tz
    except Exception as parse_err:
        return None


def normalize_time(slots):
    """
    Derive a valid time tuple.
    :param slots:
    :return: tuple of H, M, S, resolution
    """

    # Default time is mid-day, noon. In timezone provided or UTC if no timezone.
    hh_mm_ss = []
    for field in ["hh", "mm", "ss"]:
        if field in slots:
            val = slots.get(field)
            if val is not None:
                hh_mm_ss.append(int(val))
        else:
            hh_mm_ss.append(-1)

    # Time resolution is D, H, M, S ... where second is optional
    hh, mm, ss = hh_mm_ss
    # resolution = Resolution.DAY
    if not (0 <= hh < 24):
        return None
    # resolution = Resolution.HOUR
    if not (0 <= mm < 60):
        return None
    resolution = Resolution.MINUTE
    if 0 <= ss < 60:
        resolution = Resolution.SECOND
    return hh, mm, ss, resolution


class XTemporal(PatternExtractor):
    def __init__(self, cfg="datetime_patterns_py.cfg", debug=False, locale=None):
        """
        :param cfg: patterns config file.
        """
        PatternExtractor.__init__(self, RegexPatternManager(cfg, debug=debug, testing=debug))
        if locale:
            global _default_locale
            _default_locale = locale.lower()

        if debug:
            log.setLevel("DEBUG")


class Resolution:
    YEAR = "Y"
    MONTH = "M"
    WEEK = "W"
    DAY = "D"
    HOUR = "H"
    MINUTE = "m"
    SECOND = "s"


class DateTimeMatch(PatternMatch):
    """
    DateTimeMatch puts out a matched date with attributes:

        datenorm -- ISO yyyy-mm-dd date
        epoch    -- seconds from 1970-01-01
        resolution - D, M, h, m, s
        locale   -- "north-am" or "euro".

        If locale is set using XTemporal(locale='euro')
        matching Euro-style dates will be forced as such through out document.
        When locale is not set, the default is to only use euro locale for dates
        that are not ambiguous, e.g., 30/05/1977.
        Ambiguous dates (with no default locale used) are parsed as "north-am".
    """
    def __init__(self, *args, **kwargs):
        PatternMatch.__init__(self, *args, **kwargs)
        self.case = PatternMatch.LOWER_CASE
        self.locale = "north-am"  # vs. "euro" vs...

    def __str__(self):
        return f"{self.text}"

    def normalize(self):
        PatternMatch.normalize(self)
        self.is_valid = False
        self.filtered_out = True

        # Slots to capture:
        # MON_ABBREV, MON_NAME,  MONTH, MM
        # YEAR, YY, YEARYY
        # DAY_ENUM, DOM, DD
        # SHORT_TZ, LONG_TZ
        # hh, mm, ss
        slots = self.attributes()

        # normalize_year, resolution = YEAR
        # if separators present, validate now
        # normalize day or day of month
        # normalize month num or month name
        # normalize TZ and time if present.
        # set finest resolution Y, M, D, H, S
        # TODO: TIMEX encodings

        year = normalize_year(slots)
        if year is None or year == INVALID_DATE:
            return False

        # resolution = Resolution.YEAR
        day, month = None, None
        is_short_mdy = False
        if self.pattern_id in {"MDY-01", "MDY-02"}:
            is_short_mdy = True
            day, month = test_european_locale(slots, _default_locale) # Uses DM slots only
            if day and day < 0:
                return False
            if day and month:
                # Non-zero day/month returned from test
                self.locale = "euro"

        if not month:
            month = normalize_month_num(slots)
        if month <= 0:
            month = normalize_month_name(slots)

        if month < 0:
            return False

        resolution = Resolution.MONTH
        sep1 = slots.get("DSEP1")
        sep2 = slots.get("DSEP2")
        if sep1 and sep2 and sep1 != sep2:
            return False

        if sep1 == "." and is_short_mdy:
            year_str = _get_year(slots)
            if len(year_str) ==2:
                return False
            
        if not day:
            day = normalize_day(slots)
        if day == INVALID_DAY:
            return False
        elif day == INVALID_DATE:
            # Missing day
            day = 1
        else:
            resolution = Resolution.DAY

        # Simple february catch:
        if month == 2 and day > 29:
            return False

        try:
            tz_found = None
            date_found = arrow.get(datetime(year, month, day))
            tm = normalize_time(slots)
            if tm:
                hr, minute, seconds, resolution = tm
                if hr >= 0:
                    date_found = date_found.shift(hours=hr)
                    if minute >= 0:
                        date_found = date_found.shift(minutes=minute)
                        if seconds >= 0:
                            date_found = date_found.shift(seconds=seconds)
                tz_found = normalize_tz(slots)
                if tz_found:
                    date_found = date_found.to(tz_found.tzinfo)

            # Matchgroups are raw data from REGEX
            # Attributes are final encodings to share.
            self.attrs = {
                "datenorm": date_found.format("YYYY-MM-DD"),
                "epoch": timegm(date_found.timetuple()),
                "resolution": resolution,
                "locale": self.locale
            }
            if tm:
                self.attrs["timestamp"] = date_found.format("YYYY-MM-DDTHH:mm:ssZ")
            if tz_found:
                self.attrs["tzinfo"] = tz_found.format("ZZZ")

            self.is_valid = True
            self.filtered_out = False
        except Exception as parse_err:
            # For debugging purposes -- but ideally, you IGNORE
            # date/time values that are marked filtered_out = True
            self.attrs["error"] = str(parse_err)
            log.info("Parsing error: DATE: %s (YMD = %d / % d / %d )", self.text, year, month, day)
            log.debug("Exception  - ", exc_info=parse_err)
