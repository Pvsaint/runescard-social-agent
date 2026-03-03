#!/usr/bin/env python3
"""
scheduler.py — Automated posting daemon for RunesCard Social Media Agent
========================================================================

Runs the agent on a configurable schedule (POST_FREQUENCY posts per day),
distributing posts evenly across the day.

Usage:
    python scheduler.py            # start the daemon (uses .env config)
    python scheduler.py --once     # run immediately once, then exit

Environment variables (in .env):
    POST_FREQUENCY   — number of posts per day (default: 3)
    DRY_RUN          — "true" to preview without posting (default: true)
    ENABLED_PLATFORMS — comma-separated list
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from rich.console import Console

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("scheduler")
console = Console()

sys.path.insert(0, str(Path(__file__).parent))
from agent import run_once, _enabled_platforms, _is_dry_run  # noqa: E402


def _interval_minutes() -> int:
    frequency = int(os.getenv("POST_FREQUENCY", "3"))
    if frequency <= 0:
        frequency = 1
    # Spread posts evenly across 16 waking hours (960 minutes)
    return max(1, 960 // frequency)


def _scheduled_job() -> None:
    logger.info("Scheduler triggered — running agent...")
    run_once(platforms=_enabled_platforms(), dry_run=_is_dry_run())


def main() -> None:
    parser = argparse.ArgumentParser(description="RunesCard Social Media Scheduler")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run the agent once immediately, then exit",
    )
    args = parser.parse_args()

    if args.once:
        console.print("[cyan]Running agent once...[/cyan]")
        _scheduled_job()
        return

    interval = _interval_minutes()
    frequency = int(os.getenv("POST_FREQUENCY", "3"))
    dry_run = _is_dry_run()

    console.rule("[bold cyan]RunesCard Social Media Scheduler[/bold cyan]")
    console.print(
        f"  Frequency : [cyan]{frequency} posts/day[/cyan] (every {interval} min)\n"
        f"  Platforms : [cyan]{', '.join(_enabled_platforms())}[/cyan]\n"
        f"  Mode      : [{'yellow' if dry_run else 'green'}]{'DRY RUN' if dry_run else 'LIVE'}[/{'yellow' if dry_run else 'green'}]"
    )
    console.print("\n[dim]Press Ctrl+C to stop.[/dim]\n")

    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(
        _scheduled_job,
        trigger=IntervalTrigger(minutes=interval),
        id="runescard_post",
        name="RunesCard Social Post",
        replace_existing=True,
    )

    # Also fire immediately on start
    scheduler.add_job(
        _scheduled_job,
        id="runescard_post_immediate",
        name="RunesCard Immediate Post",
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        console.print("\n[dim]Scheduler stopped.[/dim]")


if __name__ == "__main__":
    main()
