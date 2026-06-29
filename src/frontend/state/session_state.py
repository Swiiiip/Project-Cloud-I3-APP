from dataclasses import dataclass

from src.frontend.view.view_model import BlurmojiViewModel


@dataclass
class FrontendSessionState:
    view_model: BlurmojiViewModel

