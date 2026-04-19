import logging

from nicegui import ui

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
            with ui.card().classes('w-full h-full bg-[#1e1e1e] border border-[#333] items-center justify-center'):
                ui.spinner(size='lg')
            return

        with ui.card().classes('w-full h-full bg-[#1e1e1e] border border-[#333] p-3 items-center justify-center'):
            ui.image(rendered_image).classes('w-full h-auto max-h-full object-contain rounded-lg')
            if state.is_completed:
                ui.label('SOLVED').classes('text-center font-bold text-xl mt-2 text-green-500')

        logger.info('Rendered challenge image: attempts=%s completed=%s', state.attempts, state.is_completed)
