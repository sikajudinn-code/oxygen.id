#!/usr/bin/env python3
"""Archive one Clarity traffic snapshot for the previous Jakarta date."""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
STATS_PATH = ROOT / "traffic-stats.json"
API_URL = "https://www.clarity.ms/export-data/api/v1/project-live-insights"
TIME_ZONE = ZoneInfo("Asia/Jakarta")


def count_total(rows, field):
    values = []
    for row in rows:
        value = row.get(field)
        if value is None or value == "":
            continue
        values.append(int(str(value).replace(",", "")))
    return sum(values) if values else None


def main():
    token = os.environ.get("CLARITY_API_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Missing GitHub Actions secret CLARITY_API_TOKEN.")

    url = f"{API_URL}?{urlencode({'numOfDays': '1'})}"
    request = Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise RuntimeError(f"Clarity API returned HTTP {error.code}.") from None
    except URLError as error:
        raise RuntimeError(f"Unable to reach Clarity API: {error.reason}") from None

    if not isinstance(payload, list):
        raise RuntimeError("Unexpected Clarity API response format.")
    traffic = next((item for item in payload if item.get("metricName") == "Traffic"), None)
    if not traffic:
        raise RuntimeError("Clarity response did not include the Traffic metric.")
    rows = traffic.get("information") or []
    if not rows:
        raise RuntimeError("Clarity returned no Traffic information rows; no snapshot was written.")

    sessions = count_total(rows, "totalSessionCount")
    unique_visitors = count_total(rows, "distantUserCount")
    if sessions is None:
        raise RuntimeError("Clarity response did not include totalSessionCount.")

    collected_at = datetime.now(timezone.utc).astimezone(TIME_ZONE)
    # The scheduled run is at about 00:05 WIB. Clarity supplies a rolling 24-hour
    # window, so its snapshot is labeled with the preceding Jakarta calendar date.
    snapshot_date = (collected_at.date() - timedelta(days=1)).isoformat()

    if STATS_PATH.exists():
        try:
            stats = json.loads(STATS_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise RuntimeError("traffic-stats.json is not valid JSON.") from error
    else:
        stats = {"provider": "Microsoft Clarity", "timezone": "Asia/Jakarta", "days": {}}

    stats.setdefault("provider", "Microsoft Clarity")
    stats["timezone"] = "Asia/Jakarta"
    stats.setdefault("days", {})
    stats["days"][snapshot_date] = {
        "sessions": sessions,
        "uniqueVisitors": unique_visitors,
        "collectedAt": collected_at.isoformat(timespec="seconds"),
        "window": "last_24_hours",
    }
    stats["updatedAt"] = collected_at.isoformat(timespec="seconds")

    STATS_PATH.write_text(
        json.dumps(stats, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"Saved Clarity snapshot for {snapshot_date}: "
        f"sessions={sessions}, unique_visitors={unique_visitors if unique_visitors is not None else 'unavailable'}"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
