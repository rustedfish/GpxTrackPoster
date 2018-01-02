# Copyright 2016-2017 Florian Pigorsch & Contributors. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import svgwrite
from . import value_range
from . import year_range


class Poster:
    def __init__(self):
        self.athlete = None
        self.title = "My Poster"
        self.tracks_by_date = {}
        self.tracks = []
        self.length_range = value_range.ValueRange()
        self.length_range_by_date = value_range.ValueRange()
        self.units = "metric"
        self.colors = {"background": "#222222", "text": "#FFFFFF", "special": "#FFFF00", "track": "#4DD2FF"}
        self.width = 200
        self.height = 300
        self.years = None
        self.tracks_drawer = None

    def set_tracks(self, tracks):
        self.tracks = tracks
        self.tracks_by_date = {}
        self.length_range = value_range.ValueRange()
        self.length_range_by_date = value_range.ValueRange()
        self.__compute_years(tracks)
        for track in tracks:
            if not self.years.contains(track.start_time):
                continue
            text_date = track.start_time.strftime("%Y-%m-%d")
            if text_date in self.tracks_by_date:
                self.tracks_by_date[text_date].append(track)
            else:
                self.tracks_by_date[text_date] = [track]
            self.length_range.extend(track.length)
        for tracks in self.tracks_by_date.values():
            length = sum([t.length for t in tracks])
            self.length_range_by_date.extend(length)

    def draw(self, drawer, output):
        self.tracks_drawer = drawer
        d = svgwrite.Drawing(output, ('{}mm'.format(self.width), '{}mm'.format(self.height)))
        d.viewbox(0, 0, self.width, self.height)
        d.add(d.rect((0, 0), (self.width, self.height), fill=self.colors['background']))
        self.__draw_header(d)
        self.__draw_footer(d)
        self.__draw_tracks(d, self.width - 20, self.height - 30 - 30, 10, 30)
        d.save()

    def m2u(self, m):
        if self.units == "metric":
            return 0.001 * m
        else:
            return 0.001 * m / 1.609344

    def u(self):
        if self.units == "metric":
            return "km"
        else:
            return "mi"

    def __draw_tracks(self, d, w, h, offset_x, offset_y):
        self.tracks_drawer.draw(d, w, h, offset_x, offset_y)

    def __draw_header(self, d):
        text_color = self.colors["text"]
        title_style = "font-size:12px; font-family:Arial; font-weight:bold;"
        d.add(d.text(self.title, insert=(10, 20), fill=text_color, style=title_style))

    def __draw_footer(self, d):
        text_color = self.colors["text"]
        header_style = "font-size:4px; font-family:Arial"
        value_style = "font-size:9px; font-family:Arial"
        small_value_style = "font-size:3px; font-family:Arial"

        (total_length, average_length, min_length, max_length, weeks) = self.__compute_track_statistics()

        d.add(d.text("ATHLETE", insert=(10, self.height-20), fill=text_color, style=header_style))
        d.add(d.text(self.athlete, insert=(10, self.height-10), fill=text_color, style=value_style))
        d.add(d.text("STATISTICS", insert=(120, self.height-20), fill=text_color, style=header_style))
        d.add(d.text("Number: {}".format(len(self.tracks)), insert=(120, self.height - 15), fill=text_color,
                     style=small_value_style))
        d.add(d.text("Weekly: {:.1f}".format(len(self.tracks) / weeks), insert=(120, self.height - 10), fill=text_color,
                     style=small_value_style))
        d.add(d.text("Total: {:.1f} {}".format(self.m2u(total_length), self.u()), insert=(139, self.height-15),
                     fill=text_color, style=small_value_style))
        d.add(d.text("Avg: {:.1f} {}".format(self.m2u(average_length), self.u()), insert=(139, self.height-10),
                     fill=text_color, style=small_value_style))
        d.add(d.text("Min: {:.1f} {}".format(self.m2u(min_length), self.u()), insert=(167, self.height-15),
                     fill=text_color, style=small_value_style))
        d.add(d.text("Max: {:.1f} {}".format(self.m2u(max_length), self.u()), insert=(167, self.height-10),
                     fill=text_color, style=small_value_style))

    def __compute_track_statistics(self):
        length_range = value_range.ValueRange()
        total_length = 0
        weeks = {}
        for t in self.tracks:
            total_length += t.length
            length_range.extend(t.length)
            # time.isocalendar()[1] -> week number
            weeks[(t.start_time.year, t.start_time.isocalendar()[1])] = 1
        return total_length, total_length / len(self.tracks), length_range.lower(), length_range.upper(), len(weeks)

    def __compute_years(self, tracks):
        if self.years is not None:
            return
        self.years = year_range.YearRange()
        for t in tracks:
            self.years.add(t.start_time)