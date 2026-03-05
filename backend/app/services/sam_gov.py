"""
SAM.gov API client for fetching government contract opportunities.

Ported from the govbizops project and adapted for the Pretorin CRM backend.
"""

import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import requests

logger = logging.getLogger(__name__)


class SAMGovClient:
    """Client for the SAM.gov Contract Opportunities API."""

    BASE_URL = "https://api.sam.gov/opportunities/v2/search"

    MAX_NAICS_CODES = 50
    MAX_DAYS_RANGE = 90
    RATE_LIMIT_DELAY = 2  # seconds between API calls

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"X-Api-Key": api_key, "Accept": "application/json"})

    def search_opportunities(
        self,
        posted_from: datetime,
        posted_to: datetime,
        naics_codes: list[str] | None = None,
        limit: int = 100,
        offset: int = 0,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Search for contract opportunities with pagination."""
        if naics_codes and len(naics_codes) > self.MAX_NAICS_CODES:
            raise ValueError(
                f"Maximum {self.MAX_NAICS_CODES} NAICS codes allowed. Got {len(naics_codes)}."
            )

        days_diff = (posted_to - posted_from).days
        if days_diff > self.MAX_DAYS_RANGE:
            raise ValueError(
                f"Maximum {self.MAX_DAYS_RANGE} days range allowed. Got {days_diff} days."
            )

        params: dict[str, Any] = {
            "postedFrom": posted_from.strftime("%m/%d/%Y"),
            "postedTo": posted_to.strftime("%m/%d/%Y"),
            "limit": min(limit, 1000),
            "offset": offset,
        }

        if naics_codes:
            params["ncode"] = ",".join(naics_codes)

        params.update(kwargs)

        logger.info("SAM.gov API request: %s", params)
        response = self.session.get(self.BASE_URL, params=params)

        if response.status_code != 200:
            logger.error("SAM.gov API error %d: %s", response.status_code, response.text)

        response.raise_for_status()
        result: dict[str, Any] = response.json()

        logger.info(
            "SAM.gov API response: totalRecords=%d, returned=%d",
            result.get("totalRecords", 0),
            len(result.get("opportunitiesData", [])),
        )

        time.sleep(self.RATE_LIMIT_DELAY)
        return result

    def get_all_opportunities(
        self,
        posted_from: datetime,
        posted_to: datetime,
        naics_codes: list[str] | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Fetch all opportunities matching criteria, handling pagination."""
        all_opportunities: list[dict[str, Any]] = []
        offset = 0
        limit = 500

        while True:
            try:
                response = self.search_opportunities(
                    posted_from=posted_from,
                    posted_to=posted_to,
                    naics_codes=naics_codes,
                    limit=limit,
                    offset=offset,
                    **kwargs,
                )

                opportunities = response.get("opportunitiesData", [])
                if not opportunities:
                    break

                all_opportunities.extend(opportunities)

                total_records = response.get("totalRecords", 0)
                if offset + limit >= total_records:
                    break

                offset += limit
                time.sleep(self.RATE_LIMIT_DELAY)

            except Exception as e:
                logger.error("Error fetching opportunities at offset %d: %s", offset, e)
                break

        logger.info("Total opportunities collected: %d", len(all_opportunities))
        return all_opportunities


def collect_opportunities(
    api_key: str,
    naics_codes: list[str],
    days_back: int = 1,
    solicitations_only: bool = True,
) -> list[dict[str, Any]]:
    """
    Collect opportunities from SAM.gov API.

    Returns deduplicated list of opportunity dicts in SAM.gov API format.
    """
    if days_back > SAMGovClient.MAX_DAYS_RANGE:
        raise ValueError(
            f"Maximum {SAMGovClient.MAX_DAYS_RANGE} days range allowed. Got {days_back}."
        )

    client = SAMGovClient(api_key)
    posted_to = datetime.now(timezone.utc)
    posted_from = posted_to - timedelta(days=days_back)

    logger.info(
        "Collecting opportunities: NAICS=%s, range=%s to %s",
        naics_codes,
        posted_from.date(),
        posted_to.date(),
    )

    # Collect per NAICS code and deduplicate by noticeId
    unique: dict[str, dict[str, Any]] = {}
    for code in naics_codes:
        opportunities = client.get_all_opportunities(
            posted_from=posted_from,
            posted_to=posted_to,
            naics_codes=[code],
        )
        for opp in opportunities:
            notice_id = opp.get("noticeId")
            if notice_id:
                unique[notice_id] = opp

    results = list(unique.values())

    if solicitations_only:
        results = [opp for opp in results if "Solicitation" in opp.get("type", "")]

    logger.info(
        "Collection complete: %d total unique, %d after filtering", len(unique), len(results)
    )
    return results
