#!/usr/bin/env python3
"""
Blurmoji - Entry Point
Demonstrates the restructured codebase with src/ and tests/ directories.
"""

import logging
import sys

from src.config.config import Config
from src.core.emoji_kitchen_service import EmojiKitchenService
from src.storage.file_based_game_state_store import FileBasedGameStateStore
from src.game.daily_challenge_service import DailyChallengeService

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    logger = logging.getLogger(__name__)
    
    print("🎮 Blurmoji - Emoji Guessing Game")
    print("=" * 40)

    # Initialize services
    config = Config.from_environment()
    emoji_service = EmojiKitchenService(config)
    store = FileBasedGameStateStore(config)
    challenge_service = DailyChallengeService(config, emoji_service, store)

    # Quick demo
    print(f"📊 Loaded {len(emoji_service.supported_list)} supported emojis")
    print(f"💾 Game state stored in: {config.game_state_dir}")

    # Test emoji combination
    result = emoji_service.get_mixed_emoji_url("👻", "☕")
    if "error" not in result:
        print("✅ Emoji Kitchen working: Ghost + Coffee combination found")
    else:
        print("❌ Emoji Kitchen error:", result["error"])

    print("\n🚀 Run 'python tests/test_daily_challenge.py' for full game demo")


if __name__ == "__main__":
    main()
