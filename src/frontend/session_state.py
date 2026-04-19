from dataclasses import dataclass

from src.frontend.game_client import GameClient
from src.frontend.view_model import BlurmojiViewModel


@dataclass
class FrontendSessionState:
    client: GameClient
    view_model: BlurmojiViewModel

