#!/usr/bin/env python3
"""
agent.py — RunesCard Social Media AI Agent
==========================================

The main orchestrator. Generates content with the LLM and publishes
to enabled platforms, or previews in dry-run mode.

Usage:
    python agent.py                          # one full run on all platforms
    python agent.py --dry-run                # preview without posting
    python agent.py --platform twitter       # target single platform
    python agent.py --post-type educational  # force a content category
    python agent.py --hint "new feature: multi-token support"
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# ── env ─────────────────────────────────────────────────────────────────────
_ENV_FILE = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_ENV_FILE)

# ── logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("agent")
console = Console()

# ── local imports ────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from generators.content_generator import ContentGenerator, POST_TYPES  # noqa: E402


# ── helpers ──────────────────────────────────────────────────────────────────

def _enabled_platforms() -> list[str]:
    raw = os.getenv("ENABLED_PLATFORMS", "twitter,farcaster")
    return [p.strip().lower() for p in raw.split(",") if p.strip()]


def _is_dry_run() -> bool:
    return os.getenv("DRY_RUN", "true").lower() in ("true", "1", "yes")


def _get_publisher(platform: str):
    """Return the publisher instance for *platform*, or None on error."""
    try:
        if platform == "twitter":
            from publishers.twitter import TwitterPublisher
            return TwitterPublisher()
        elif platform == "farcaster":
            from publishers.farcaster import FarcasterPublisher
            return FarcasterPublisher()
        else:
            logger.warning(f"Unknown platform: {platform}")
            return None
    except EnvironmentError as exc:
        logger.warning(f"[{platform}] Skipping — missing credentials: {exc}")
        return None


def _print_post(platform: str, post_type: str, text: str, dry_run: bool) -> None:
    mode_label = "[DRY RUN]" if dry_run else "[LIVE]"
    color = "yellow" if dry_run else "green"
    panel = Panel(
        Text(text, style="white"),
        title=f"[bold {color}]{mode_label} {platform.upper()} — {post_type.replace('_', ' ').title()}[/bold {color}]",
        border_style=color,
        padding=(1, 2),
    )
    console.print(panel)


# ── core run ─────────────────────────────────────────────────────────────────

def run_once(
    platforms: list[str],
    post_type: str | None = None,
    extra_hint: str = "",
    dry_run: bool | None = None,
) -> None:
    """
    Generate and publish (or preview) one post per platform.

    Args:
        platforms:   list of platform names to target
        post_type:   override content category (random if None)
        extra_hint:  optional freeform context for the LLM
        dry_run:     override .env DRY_RUN; uses env value when None
    """
    if dry_run is None:
        dry_run = _is_dry_run()

    generator = ContentGenerator()

    for platform in platforms:
        _type = post_type  # each platform may get a different random type
        try:
            text = generator.generate(platform, _type, extra_hint)
            selected_type = _type or "random"
            _print_post(platform, selected_type, text, dry_run)

            if not dry_run:
                publisher = _get_publisher(platform)
                if publisher:
                    result = publisher.post(text)
                    console.print(
                        f"  [green]✓ Posted to {platform}:[/green] {result}\n"
                    )
            else:
                console.print(
                    f"  [dim]Dry-run mode — not posting to {platform}.[/dim]\n"
                )
        except Exception as exc:
            logger.error(f"[{platform}] Failed: {exc}", exc_info=True)


# ── entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="RunesCard Social Media AI Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py --dry-run
  python agent.py --platform twitter --post-type educational
  python agent.py --hint "we just hit 10,000 cards sent!"
  python agent.py --post-type call_to_action --live
        """,
    )
    parser.add_argument(
        "--platform",
        choices=["twitter", "farcaster"],
        help="Target a single platform (default: all enabled in .env)",
    )
    parser.add_argument(
        "--post-type",
        choices=POST_TYPES,
        dest="post_type",
        help="Force a specific content category",
    )
    parser.add_argument(
        "--hint",
        default="",
        help="Extra context or hook to steer content generation",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=None,
        dest="dry_run",
        help="Preview content without posting (overrides .env DRY_RUN)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        dest="live",
        help="Force live posting (overrides .env DRY_RUN=true)",
    )

    args = parser.parse_args()

    # Resolve platforms
    platforms = [args.platform] if args.platform else _enabled_platforms()
    if not platforms:
        console.print("[red]No platforms enabled. Check ENABLED_PLATFORMS in .env.[/red]")
        sys.exit(1)

    # Resolve dry-run flag
    if args.live:
        dry_run = False
    elif args.dry_run:
        dry_run = True
    else:
        dry_run = _is_dry_run()

    console.rule("[bold cyan]RunesCard Social Media Agent[/bold cyan]")
    console.print(
        f"  Platforms : [cyan]{', '.join(platforms)}[/cyan]\n"
        f"  Mode      : [{'yellow' if dry_run else 'green'}]{'DRY RUN' if dry_run else 'LIVE'}[/{'yellow' if dry_run else 'green'}]\n"
        f"  Post type : [cyan]{args.post_type or 'random'}[/cyan]"
    )
    console.print()

    run_once(
        platforms=platforms,
        post_type=args.post_type,
        extra_hint=args.hint,
        dry_run=dry_run,
    )

    console.rule("[dim]Done[/dim]")


if __name__ == "__main__":
    main()
