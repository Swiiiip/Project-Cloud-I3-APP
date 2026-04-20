import logging
from datetime import date

from nicegui import ui

from src.frontend.ui_constants import UIClasses, UIContent, format_daily_challenge_label
from src.frontend.view_model import BlurmojiViewModel

logger = logging.getLogger(__name__)


class ChallengeImageSection:
    def __init__(self, view_model: BlurmojiViewModel):
        self._view_model = view_model

    @ui.refreshable
    def render(self):
        state = self._view_model.state
        rendered_image = self._view_model.rendered_image
        if not state or rendered_image is None:
            logger.info('ChallengeImageSection waiting for initial data: has_state=%s has_image=%s', state is not None, rendered_image is not None)
            with ui.card().classes(UIClasses.PANEL_CARD_CENTERED):
                ui.spinner(size='lg')
            return

        with ui.card().classes(f'{UIClasses.PANEL_CARD_PADDED} items-center justify-center'):
            ui.label(format_daily_challenge_label(date.today().strftime('%d-%m-%Y'))).classes(UIClasses.DAILY_CHALLENGE_TEXT)
            ui.image(rendered_image).classes(UIClasses.CHALLENGE_IMAGE)
            if state.is_completed:
                ui.label(UIContent.SOLVED_LABEL).classes(UIClasses.SOLVED_LABEL)

        logger.info('Rendered challenge image: attempts=%s completed=%s', state.attempts, state.is_completed)
