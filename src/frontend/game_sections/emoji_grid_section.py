import logging
from collections import OrderedDict

from nicegui import ui

from src.core.emoji.dto.emoji_data import EmojiData
from src.frontend.view_model import BlurmojiViewModel

logger = logging.getLogger(__name__)


class EmojiGridSection:
    def __init__(self, view_model: BlurmojiViewModel):
        self._view_model = view_model
        self._selected_category: str | None = None

    @ui.refreshable
    def render(self):
        emoji_pool = self._view_model.emoji_pool
        logger.info('EmojiGridSection render start: emoji_pool_size=%d selected_category=%s', len(emoji_pool), self._selected_category)

        if not emoji_pool:
            logger.info('EmojiGridSection render skipped because emoji pool is empty')
            with ui.card().classes('w-full h-full bg-[#1e1e1e] border border-[#333] items-center justify-center'):
                ui.spinner(size='md')
            return

        try:
            categories = self._group_by_category(emoji_pool)
            logger.info('EmojiGridSection grouped pool into %d categories: %s', len(categories), list(categories.keys()))
            self._ensure_selected_category(categories)

            if self._selected_category is None:
                logger.warning('EmojiGridSection has no selected category after grouping')
                with ui.card().classes('w-full h-full bg-[#1e1e1e] border border-[#333] items-center justify-center'):
                    ui.label('No emojis available').classes('text-gray-400')
                return

            current_emojis = categories[self._selected_category]
            logger.info('EmojiGridSection rendering category=%s size=%d', self._selected_category, len(current_emojis))

            with ui.card().classes('w-full h-full min-h-0 overflow-hidden bg-[#1e1e1e] border border-[#333] p-2'):
                with ui.column().classes('w-full h-full min-h-0 gap-2 overflow-hidden'):
                    with ui.row().classes('w-full gap-1 overflow-x-auto flex-nowrap items-center'):
                        for category_name in categories:
                            is_active = category_name == self._selected_category
                            button = ui.button(
                                category_name,
                                on_click=lambda selected=category_name: self._select_category(selected)
                            ).props('dense no-caps')
                            if is_active:
                                button.props('color=primary')
                            else:
                                button.props('flat color=grey-7')

                    with ui.scroll_area().classes('w-full flex-1 min-h-0 border border-[#2a2a2a] rounded-md p-1').style('height: 100%;'):
                        with ui.row().classes('w-full justify-start items-start content-start gap-1 flex-wrap'):
                            for emoji in current_emojis:
                                self._create_emoji_button(emoji)

            logger.info(
                'EmojiGridSection render complete: total_emojis=%d rendered_buttons=%d selected_category=%s',
                len(emoji_pool),
                len(current_emojis),
                self._selected_category,
            )
        except Exception as exc:
            logger.exception('EmojiGridSection render failed: %s', exc)
            with ui.card().classes('w-full h-full bg-[#1e1e1e] border border-red-700 items-center justify-center'):
                ui.label('Keyboard failed to render').classes('text-red-400')

    def _ensure_selected_category(self, categories: OrderedDict[str, list[EmojiData]]) -> None:
        if not categories:
            self._selected_category = None
            logger.warning('EmojiGridSection _ensure_selected_category found no categories')
            return

        if self._selected_category in categories:
            logger.info('EmojiGridSection keeping selected category=%s', self._selected_category)
            return

        preferred_categories = [name for name in categories if name != 'Unknown']
        if preferred_categories:
            self._selected_category = max(preferred_categories, key=lambda name: len(categories[name]))
        else:
            self._selected_category = max(categories.keys(), key=lambda name: len(categories[name]))
        selected_category = self._selected_category
        logger.info('EmojiGridSection selected default category=%s size=%d', selected_category, len(categories[selected_category]))

    def _select_category(self, category_name: str) -> None:
        if category_name == self._selected_category:
            logger.info('EmojiGridSection category click ignored because already selected: %s', category_name)
            return

        logger.info('EmojiGridSection category changed from %s to %s', self._selected_category, category_name)
        self._selected_category = category_name
        self.render.refresh()

    @staticmethod
    def _group_by_category(emojis: tuple[EmojiData, ...]) -> OrderedDict[str, list[EmojiData]]:
        grouped: OrderedDict[str, list[EmojiData]] = OrderedDict()
        sorted_emojis = sorted(emojis, key=lambda value: (value.category, value.keyboard_position, value.name))
        for emoji in sorted_emojis:
            category_name = emoji.category or 'Unknown'
            grouped.setdefault(category_name, []).append(emoji)
        return grouped

    def _create_emoji_button(self, emoji: EmojiData):
        ui.button(
            emoji.character,
            on_click=lambda selected=emoji: self._on_emoji_selected(selected)
        ).props('flat').classes('text-2xl p-1 rounded-lg hover:bg-white/10 w-10 h-10')

    def _on_emoji_selected(self, emoji: EmojiData):
        logger.info('Emoji selected: category=%s codepoint=%s name=%s', emoji.category, emoji.codepoint, emoji.name)
        self._view_model.select_emoji(emoji)
