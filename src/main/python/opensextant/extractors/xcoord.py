# coding: utf-8

import arrow
from opensextant import Coordinate
from opensextant.FlexPat import PatternExtractor, RegexPatternManager, PatternMatch
from pygeodesy.mgrs import Mgrs
from pygeodesy.utm import Utm


# History - 2024 may - MCU ported from XCoord Java
#
#
# TODO: error "precision" scales
#       text formatting of normalized coordinate
#       complete testing

class XCoord(PatternExtractor):
    """
    NOTE: a port of XCoord java (org.opensextant.extractors.xcoord, in Xponents-Core)
    """

    def __init__(self, cfg="geocoord_patterns_py.cfg", debug=False):
        """
        :param cfg: patterns config file.
        """
        PatternExtractor.__init__(self, RegexPatternManager(cfg, debug=debug, testing=debug))


class ResolutionUncertainty:
    UNKNOWN = 100000
    REGIONAL = 50000
    LOCAL = 5000
    SITE = 1000
    SPOT = 100
    GPS = 10


class Specificity:
    DEG = 1
    SUBDEG = 2
    MINUTE = 3
    SUBMINUTE = 4
    SECOND = 5
    SUBSECOND = 6


HEMISPHERES = {
    "-": -1,
    "W": -1,
    "S": -1,
    "+": 1,
    "E": 1,
    "N": 1,
    None: 1
}


def hemisphere_factor(sym: str) -> int:
    if sym:
        return HEMISPHERES.get(sym.upper())
    return HEMISPHERES.get(None)


class Hemisphere:
    def __init__(self, axis, slots=None):
        self.axis = axis
        self.symbol = None
        self.polarity = 0
        self.slots = slots
        self.normalize()

    def is_alpha(self) -> bool:
        return self.symbol and self.symbol.isalpha()

    def standard_format(self) -> str:
        """
        Caution -- test for  presence of symbol first, as decimal value without hemisphere may not be geo coord at all.
        """
        if self.polarity >= 0:
            return "+"
        if self.polarity < 0:
            return "-"

    def normalize(self):
        if not self.slots:
            return
        if self.axis == "lon":
            for slot in ["hemiLon", "hemiLonSign", "hemiLonPre"]:
                if slot in self.slots:
                    self.symbol = self.slots.get(slot)
                    if not self.symbol:
                        self.polarity = 1
                        return

        if self.axis == "lat":
            for slot in ["hemiLat", "hemiLatSign", "hemiLatPre"]:
                if slot in self.slots:
                    self.symbol = self.slots.get(slot)
                    if not self.symbol:
                        self.polarity = 1
                        return

        if self.symbol:
            self.symbol = self.symbol.upper().strip()
            self.polarity = hemisphere_factor(self.symbol)


class DMSOrdinate:
    SYMBOLS = {"°", "º", "'", "\"", ":", "lat", "lon", "geo", "coord", "deg"}

    def __init__(self, axis: str, text: str, slots=None):
        self.axis = axis
        self.text = text
        self.slots = slots
        self.degrees = None
        self.min = None
        self.seconds = None
        self.hemi = None
        self.symbols = set()
        self.normalized_slots = dict()
        self.resolution = ResolutionUncertainty.UNKNOWN
        self.specificity = Specificity.DEG
        self.normalize()

    def is_valid(self):
        if not self.degrees:
            return False
        # Must have degrees, in range for the axis
        if self.axis == "lat":
            if not -90 < self.degrees < 90:
                return False
        if self.axis == "lon":
            if not -180 < self.degrees < 180:
                return False
        # Min and Secs must be in range if specified
        if self.min and not 0 < self.min < 60:
            return False
        if self.seconds and not 0 < self.seconds < 60:
            return False

        return True

    def has_minutes(self):
        return self.min and (self.specificity == Specificity.MINUTE or self.specificity == Specificity.SUBMINUTE)

    def has_submin(self):
        return self.specificity == Specificity.SUBMINUTE

    def has_seconds(self):
        return self.seconds and (self.specificity == Specificity.SECOND or self.specificity == Specificity.SUBSECOND)

    def has_subsec(self):
        return self.specificity == Specificity.SUBSECOND

    def has_symbols(self):
        return len(self.symbols) > 1

    def normalize(self):
        """
        Parse all slots for the pattern, normalizing found items as both
        string and numeric representation.  That is, the string portion of the value should be preserved
        to avoid inserting additional precision not present in the value.  e.g., "30.44"  is 2-sig-figs, and not
        "30.4400001" or whatever artifacts come with floating point computation.

        separators and symbols present are useful in post-match processing/filtering to weed out false positives.
        """
        if not self.slots:
            return
        txtnorm = self.text.lower()
        for sym in DMSOrdinate.SYMBOLS:
            if sym in txtnorm:
                self.symbols.add(sym)

        self.hemi = Hemisphere(self.axis, slots=self.slots)
        if self.axis == "lat":
            self.digest_lat()
        elif self.axis == "lon":
            self.digest_lon()

    def decimal(self):
        pol = 1
        if self.hemi:
            pol = self.hemi.polarity
            if not pol:
                raise Exception("logic error - hemisphere was not resolved")

        if self.seconds and self.min and self.degrees:
            if self.seconds < 60:
                return pol * (self.degrees + self.min / 60 + self.seconds / 3600)
        if self.min and self.degrees:
            if self.min < 60:
                return pol * (self.degrees + self.min / 60)
        if self.degrees:
            return pol * self.degrees
        return None

    def digest_lat(self):
        self._digest_slots("Lat")

    def digest_lon(self):
        self._digest_slots("Lon")

    def _digest_slots(self, axis):
        """
        Fields or slots are named xxxLatxx or xxxLonxx
        """
        # DEGREES
        deg = self.get_int(f"deg{axis}", "deg")
        deg2 = self.get_int(f"dmsDeg{axis}", "deg")
        deg3 = self.get_decimal(f"decDeg{axis}", "deg")
        self.degrees = deg or deg2 or deg3
        if self.degrees:
            self.specificity = Specificity.DEG
            if deg3:
                self.specificity = Specificity.SUBDEG
        else:
            return

        #  MINUTES
        minutes = self.get_int(f"min{axis}", "min")
        minutes2 = self.get_int(f"dmsMin{axis}", "min")
        minutes3 = self.get_decimal(f"decMin{axis}", "min")
        mindash = self.get_decimal(f"decMin{axis}3", "min")

        self.min = minutes or minutes2 or minutes3 or mindash
        if self.min:
            self.specificity = Specificity.MINUTE

            min_fract = self.get_fractional(f"fractMin{axis}", "fmin")
            min_fract2 = self.get_fractional(f"fractMin{axis}3", "fmin")
            # variation 2, is a 3-digit or longer fraction

            if min_fract or min_fract2:
                self.specificity = Specificity.SUBMINUTE
                self.min += min_fract or min_fract2

        else:
            return

        # SECONDS
        sec = self.get_int(f"sec{axis}", "sec")
        sec2 = self.get_int(f"dmsSec{axis}", "sec")
        self.seconds = sec or sec2
        if self.seconds:
            self.specificity = Specificity.SECOND

            fsec = self.get_fractional(f"fractSec{axis}", "fsec")
            fsec2 = self.get_fractional(f"fractSec{axis}Opt", "fsec")
            if fsec or fsec2:
                self.specificity = Specificity.SUBSECOND
                self.seconds += fsec or fsec2
        return

    def get_int(self, f, fnorm):
        if f in self.slots:
            val = self.slots[f]
            self.normalized_slots[fnorm] = self.slots[f]
            return int(val)

    def get_decimal(self, f, fnorm):
        """
        find slot and convert pattern "-dddd..." to 0.dddd...
        Also, if fraction is simply "dddd..." then insert "." at front.
        """
        if f in self.slots:
            val = self.slots[f]
            if "-" in val:
                val = val.replace("-", ".")
            self.normalized_slots[fnorm] = val
            return float(val)

    def get_fractional(self, f, fnorm):
        """
        find slot and convert pattern "-dddd..." to 0.dddd...
        Also if fraction is simply "dddd..." then insert "." at front.
        """
        if f in self.slots:
            val = self.slots[f]
            if not val:
                return None
            if val.startswith("-"):
                val = val.replace("-", ".")
            elif not val.startswith("."):
                val = f".{val}"
            self.normalized_slots[fnorm] = val
            return float(val)


class GeocoordMatch(PatternMatch):
    def __init__(self, *args, **kwargs):
        PatternMatch.__init__(self, *args, **kwargs)
        self.case = PatternMatch.UPPER_CASE
        self.geodetic = None
        self.coordinate = None
        self.parsing_err = None
        self.lat_ordinate = None
        self.lon_ordinate = None
        self.filter = None

    def __str__(self):
        return f"{self.text}"

    def normalize(self):
        PatternMatch.normalize(self)
        self.is_valid = False
        self.filtered_out = True

    def _make_coordinate(self):
        if self.lat_ordinate and self.lon_ordinate:
            self.is_valid = self.lon_ordinate.is_valid() and self.lon_ordinate.is_valid()
            if self.is_valid:
                # continue to weed out noise.
                self.coordinate = Coordinate(None,
                                             lat=self.lat_ordinate.decimal(),
                                             lon=self.lon_ordinate.decimal())
                self.is_valid = self.coordinate.validate()
        elif self.geodetic:
            self.is_valid = True
            self.filtered_out = False
            LL = self.geodetic.toLatLon()
            self.coordinate = Coordinate(None, lat=LL.lat, lon=LL.lon)
            # These are parsed by UTM and MGRS libraries, so coordinate is assumed valid.


class GeocoordFilter:
    def filter_out(self, m: GeocoordMatch) -> tuple:
        return False, "reason"


class MGRSFilter(GeocoordFilter):
    def __init__(self):
        GeocoordFilter.__init__(self)
        self.date_formats = ["DDMMMYYYY", "DMMMYYHHmm", "DDMMMYYHHmm", "DMMMYY", "HHZZZYYYY"]
        self.sequences = ["1234", "123456", "12345678", "1234567890"]
        self.today = arrow.utcnow()
        self.YEAR = self.today.date().year
        self.YY = self.YEAR - 2000

    def filter_out(self, mgrs: GeocoordMatch) -> tuple:
        """
        :return: True if filtered out, false positive.
        """
        # MGRS rules:     upper case alphanumeric, greater than 6 chars,
        #    subjective:
        #    - is not a digit sequence;
        #    - is not a recent date;
        #    - is not a rate ('NNN per LB');
        #    - is not time with 'sec'

        # Lexical filters:
        if not (mgrs.text.isupper() and len(mgrs.text.replace(" ", "")) > 6):
            return True, "lexical"
        parts = set(mgrs.text.split())
        if "SEC" in parts or "PER" in parts:
            return True, "rate"
        for seq in self.sequences:
            if seq in mgrs.textnorm:
                return True, "digit-seq"

        # Date Filter
        date_test = mgrs.textnorm[0:10]
        for fmt in self.date_formats:
            try:
                dt = arrow.get(date_test, fmt)
                recent_year = abs(dt.date().year - self.YEAR) < 25
                if recent_year:
                    return True, "date"
            except Exception as parse_err:
                pass

        # Not filtered out
        return False, None


class DMSFilter(GeocoordFilter):
    def __init__(self):
        GeocoordFilter.__init__(self)
        self.date_formats = ["YY-DD-MM HH:mm:ss", "MM-DD-YY HH:mm:ss"]

    def filter_out(self, dms: GeocoordMatch) -> tuple:
        """
        Easy filter -- if puncutation matches, this is an easy pattern to ignore.
        :return: True if filtered out, false positive.
        """
        if dms.text[0].isalpha():
            return False, None
        for fmt in self.date_formats:
            try:
                dt = arrow.get(dms.text, fmt)
                return True, "date"
            except Exception as err:
                pass
        return False, None


mgrs_filter = MGRSFilter()
dms_filter = DMSFilter()


class MGRSMatch(GeocoordMatch):
    def __init__(self, *args, **kwargs):
        GeocoordMatch.__init__(self, *args, **kwargs)
        self.filter = mgrs_filter

    def validate(self):
        self.filtered_out, self.parsing_err = self.filter.filter_out(self)

    def normalize(self):
        GeocoordMatch.normalize(self)
        slots = self.attributes()
        self.textnorm = self.textnorm.replace(" ", "")

        z = slots.get("MGRSZone")
        q = slots.get("MGRSQuad")
        east_north = slots.get("Easting_Northing")

        e, n = None, None
        if " " in east_north:
            e, n = east_north.split(" ", 1)
            le = len(e)
            ln = len(n)
            if le != ln:
                resolution = min(le, ln)
                e = e[:resolution]
                n = n[:resolution]
        elif len(east_north) % 2 == 0:
            resolution = int(len(east_north) / 2)
            e, n = east_north[0:resolution], east_north[resolution:]

        if e and n:
            try:
                e = int(e)
                n = int(n)
                self.geodetic = Mgrs(zone=z, EN=q, easting=e, northing=n)
                self._make_coordinate()
                self.validate()
            except Exception as err:
                self.parsing_err = str(err)


class UTMMatch(GeocoordMatch):
    def __init__(self, *args, **kwargs):
        GeocoordMatch.__init__(self, *args, **kwargs)

    def normalize(self):
        GeocoordMatch.normalize(self)
        slots = self.attributes()

        z = slots.get("UTMZone")
        z1 = slots.get("UTMZoneZZ")  # 0-5\d
        z2 = slots.get("UTMZoneZ")  # \d

        ZZ = int(z or z1 or z2)
        band = slots.get("UTMBand")
        if not band:
            return

        hemi = band[0]
        e = slots.get("UTMEasting")
        n = slots.get("UTMNorthing")
        if e and n:
            try:
                self.geodetic = Utm(zone=ZZ, hemisphere=hemi, band=band, easting=int(e), northing=int(n))
                self._make_coordinate()
            except Exception as err:
                self.parsing_err = str(err)


class DegMinMatch(GeocoordMatch):
    def __init__(self, *args, **kwargs):
        GeocoordMatch.__init__(self, *args, **kwargs)

    def validate(self):

        slots = self.attributes()
        if self.is_valid:
            # Punct - separators must match for DM  patterns.
            lat_sep = slots.get("dmLatSep")
            lon_sep = slots.get("dmLonSep")
            if (lat_sep and not lon_sep) or (not lat_sep and lon_sep):
                self.is_valid = False
            elif lat_sep != lon_sep:
                self.is_valid = False

        # TODO: evaluate other dashes: GeocoordNormalization eval dashes, eval punct
        self.filtered_out = not self.is_valid

    def normalize(self):
        GeocoordMatch.normalize(self)

        # DEG MIN (DM) patterns, with fractional min
        #
        # dmsDegLat > [-\s]? < dmsMinLat > < hemiLat > < fractMinLat > < latlonSep > < dmsDegLon > [-\s]? < dmsMinLon > < hemiLon > < fractMinLon
        #
        # degLat > < dmLatSep >\s? < minLat > < fractMinLat >? < msLatSep >?\s? < hemiLat > < latlonSep3 > < degLon > < dmLonSep >\s? < minLon > < fractMinLon
        #
        # < hemiLatPre >\s? < degLat > < dmLatSep >\s? < minLat > < fractMinLat >? < msLatSep >? < latlonSep3 >
        #     < hemiLonPre >\s? < degLon > < dmLonSep >\s? < minLon > < fractMinLon >? < msLonSep >?

        # TODO: conditions that invalidate this pattern?
        self.lat_ordinate = DMSOrdinate("lat", self.text, slots=self.attributes())
        self.lon_ordinate = DMSOrdinate("lon", self.text, slots=self.attributes())
        self._make_coordinate()
        self.validate()


class DegMinSecMatch(GeocoordMatch):
    def __init__(self, *args, **kwargs):
        GeocoordMatch.__init__(self, *args, **kwargs)
        self.filter = dms_filter

    def normalize(self):
        GeocoordMatch.normalize(self)
        self.lat_ordinate = DMSOrdinate("lat", self.text, slots=self.attributes())
        self.lon_ordinate = DMSOrdinate("lon", self.text, slots=self.attributes())
        self._make_coordinate()
        self.validate()

    def validate(self):
        self.filtered_out, self.parsing_err = self.filter.filter_out(self)


class DecimalDegMatch(GeocoordMatch):
    def __init__(self, *args, **kwargs):
        GeocoordMatch.__init__(self, *args, **kwargs)

    def validate(self):
        """
        Validate a parsed coordinate.
             55.60, 80.11  -- not valid
             N55.60, W80.11  -- valid
             +55.60, -80.11  -- valid

        Validate also if the coordinate is a valid range for Lat/Lon.
        """
        if not self.is_valid:
            return
        lath = self.lat_ordinate.hemi
        lonh = self.lon_ordinate.hemi
        valid_hemi =  lath and lonh and lath.is_alpha() and lonh.is_alpha()
        valid_sym = self.lat_ordinate.has_symbols() or self.lon_ordinate.has_symbols()
        self.is_valid = valid_hemi or valid_sym

        self.filtered_out = not self.is_valid

    def normalize(self):
        GeocoordMatch.normalize(self)
        self.lat_ordinate = DMSOrdinate("lat", self.text, slots=self.attributes())
        self.lon_ordinate = DMSOrdinate("lon", self.text, slots=self.attributes())
        self._make_coordinate()
        self.validate()