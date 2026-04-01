import csv
from io import BytesIO, StringIO


def generate_profit_share_csv_report(rows: list[dict]) -> BytesIO:
    output_text = StringIO()
    fieldnames = ["event_time", "phone", "country", "value", "currency", "event_name"]
    writer = csv.DictWriter(output_text, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

    output = BytesIO(output_text.getvalue().encode("utf-8-sig"))
    output.seek(0)
    return output
