from datetime import date

from utils.meta_time import build_unique_meta_event_time


class TestMetaTime:
    def test_build_unique_meta_event_time_has_plus6_offset_and_iso_format(self):
        dt = build_unique_meta_event_time(date(2026, 4, 2))
        assert dt.strftime("%z") == "+0600"
        assert dt.isoformat().endswith("+06:00")

    def test_build_unique_meta_event_time_is_unique_by_seconds(self):
        dt1 = build_unique_meta_event_time(date(2026, 4, 2))
        dt2 = build_unique_meta_event_time(date(2026, 4, 2))
        assert dt1.date() == date(2026, 4, 2)
        assert dt2.date() == date(2026, 4, 2)
        assert int(dt2.timestamp()) != int(dt1.timestamp())
