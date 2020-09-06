"""Represent a range of years, with ability to update based on a track"""
# Copyright 2016-2020 Florian Pigorsch & Contributors. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import datetime
import re
import typing


class YearRange:
    """Represent a range of years, with ability to update based on a track

    Attributes:
        from_year: First year in range (lower)
        to_year: Last year in range (higher)

    Methods:
        parse: Parse a string into lower and upper bounds
        add: Adjust bounds based on a track
        contains: If track is contained in the range
        count: Number of years in range
    """

    def __init__(self) -> None:
        """Inits YearRange with empty bounds -- to be built after init"""
        self.from_year: typing.Optional[int] = None
        self.to_year: typing.Optional[int] = None

    def parse(self, s: str) -> bool:
        """Parse a plaintext range of years into a pair of years

        Attempt to turn the input string into a pair of year values, from_year and to_year. If one
        year is passed, both from_year and to_year will be set to that year. If a range like
        '2016-2018' is passed, from_year will be set to 2016, and to_year will be set to 2018.

        Args:
            s: A string representing a range of years or a single year

        Returns:
            True if the range was successfully parsed, False if not.
        """
        if s == "all":
            self.from_year = None
            self.to_year = None
            return True
        m = re.match(r"^\d+$", s)
        if m:
            self.from_year = int(s)
            self.to_year = self.from_year
            return True
        m = re.match(r"^(\d+)-(\d+)$", s)
        if m:
            y1, y2 = int(m.group(1)), int(m.group(2))
            if y1 <= y2:
                self.from_year = y1
                self.to_year = y2
                return True
        return False

    def clear(self) -> None:
        self.from_year = None
        self.to_year = None

    def add(self, t: datetime.datetime) -> None:
        """For the given t, update from_year and to_year to include that timestamp"""
        if self.from_year is None:
            self.from_year = t.year
            self.to_year = t.year
            return

        assert self.from_year is not None
        assert self.to_year is not None
        if t.year < self.from_year:
            self.from_year = t.year
        elif t.year > self.to_year:
            self.to_year = t.year

    def contains(self, t: datetime.datetime) -> bool:
        """Return True if current year range contains t, False if not"""
        if self.from_year is None:
            return True

        assert self.from_year is not None
        assert self.to_year is not None
        return self.from_year <= t.year <= self.to_year

    def count(self) -> int:
        """Return number of years contained in the current range"""
        if self.from_year is None:
            return 0

        assert self.to_year is not None
        return 1 + self.to_year - self.from_year

    def iter(self) -> typing.Generator[int, None, None]:
        if self.from_year is None:
            return

        assert self.to_year is not None
        for year in range(self.from_year, self.to_year + 1):
            yield year
