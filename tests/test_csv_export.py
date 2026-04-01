import csv
from io import StringIO

from utils.csv_export import generate_profit_share_csv_report


class TestGenerateProfitShareCsvReport:
    def test_generates_expected_columns_and_rows(self):
        rows = [
            {
                "event_time": "2026-04-10",
                "phone": "996555123456",
                "country": "KG",
                "value": "15000.00",
                "currency": "KGS",
                "event_name": "Subscribe",
            }
        ]

        result = generate_profit_share_csv_report(rows)
        text = result.getvalue().decode("utf-8-sig")
        reader = csv.DictReader(StringIO(text))
        parsed = list(reader)

        assert reader.fieldnames == ["event_time", "phone", "country", "value", "currency", "event_name"]
        assert len(parsed) == 1
        assert parsed[0]["value"] == "15000.00"
        assert parsed[0]["event_name"] == "Subscribe"
