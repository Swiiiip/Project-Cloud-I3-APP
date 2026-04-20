# pyright: reportArgumentType=false

import logging
from typing import cast, OrderedDict

from nicegui import ui

from src.core.emoji.dto.emoji_data import EmojiData
from src.frontend.ui_constants import UIClasses, UIContent, UIProps
from src.frontend.view_model import BlurmojiViewModel

logger = logging.getLogger(__name__)


class EmojiGridSection:
    def __init__(self, view_model: BlurmojiViewModel):
        self._view_model = view_model
        self._selected_category: str = UIContent.UNKNOWN_CATEGORY

    @ui.refreshable
    def render(self):
        emoji_pool = self._view_model.emoji_pool
        logger.info('EmojiGridSection render start: emoji_pool_size=%d selected_category=%s', len(emoji_pool), self._selected_category)

        if not emoji_pool:
            logger.info('EmojiGridSection render skipped because emoji pool is empty')
            with ui.card().classes(UIClasses.EMOJI_LOADING_CARD):
                ui.spinner(size='md')
            return

        try:
            categories = self._group_by_category(emoji_pool)
            logger.info('EmojiGridSection grouped pool into %d categories: %s', len(categories), list(categories.keys()))
            self._selected_category = self._ensure_selected_category(categories)

            if self._selected_category not in categories:
                logger.warning('EmojiGridSection has no selected category after grouping')
                with ui.card().classes(UIClasses.PANEL_CARD_CENTERED):
                    ui.label(UIContent.NO_EMOJIS_LABEL).classes(UIClasses.MUTED_TEXT)
                return

            current_emojis = categories[self._selected_category]
            logger.info('EmojiGridSection rendering category=%s size=%d', self._selected_category, len(current_emojis))

            with ui.card().classes(UIClasses.EMOJI_CARD):
                with ui.column().classes(UIClasses.EMOJI_COLUMN_IN_CARD):
                    with ui.row().classes(UIClasses.CATEGORY_ROW):
                        for category_name in sorted(categories.keys()):
                            normalized_category_name: str = category_name
                            self._create_category_button(normalized_category_name, normalized_category_name == self._selected_category)

                    with ui.scroll_area().classes(UIClasses.EMOJI_SCROLL_AREA):
                        with ui.row().classes(UIClasses.EMOJI_BUTTON_ROW):
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
            with ui.card().classes(UIClasses.EMOJI_ERROR_CARD):
                ui.label(UIContent.EMOJI_GRID_ERROR_LABEL).classes(UIClasses.ERROR_TEXT)

    def _ensure_selected_category(self, categories: OrderedDict[str, list[EmojiData]]) -> str:
        if not categories:
            logger.warning('EmojiGridSection _ensure_selected_category found no categories')
            return UIContent.UNKNOWN_CATEGORY

        selected_category = self._selected_category
        if selected_category and selected_category in categories:
            logger.info('EmojiGridSection keeping selected category=%s', selected_category)
            return selected_category

        preferred_categories = [name for name in categories if name != UIContent.UNKNOWN_CATEGORY]
        if preferred_categories:
            selected_category = max(preferred_categories, key=lambda name: len(categories[name]))
        else:
            selected_category = max(categories.keys(), key=lambda name: len(categories[name]))
        logger.info('EmojiGridSection selected default category=%s size=%d', selected_category, len(categories[selected_category]))
        return selected_category

    def _select_category(self, category_name: str) -> None:
        selected_category = self._selected_category or UIContent.UNKNOWN_CATEGORY
        if category_name == selected_category:
            return

        self._selected_category = category_name
        self.render.refresh()

    def _create_category_button(self, category_name: str, is_active: bool) -> None:
        button = ui.button(category_name, on_click=lambda: self._select_category(category_name)).props(UIProps.EMOJI_CATEGORY_BUTTON)
        if is_active:
            button.props(UIProps.EMOJI_CATEGORY_ACTIVE_BUTTON)
        else:
            button.props(UIProps.EMOJI_CATEGORY_INACTIVE_BUTTON)

    @staticmethod
    def _group_by_category(emojis: tuple[EmojiData, ...]) -> OrderedDict[str, list[EmojiData]]:
        grouped: OrderedDict[str, list[EmojiData]] = {}
        sorted_emojis = sorted(emojis, key=EmojiGridSection._sort_emoji_key)
        for emoji in sorted_emojis:
            category_name = EmojiGridSection._normalize_category_name(emoji.category)
            if category_name not in grouped:
                grouped[category_name] = []
            grouped[category_name].append(emoji)
        return grouped

    @staticmethod
    def _sort_emoji_key(emoji: EmojiData) -> tuple[str, int, str]:
        return (
            EmojiGridSection._normalize_category_name(emoji.category),
            emoji.keyboard_position,
            emoji.name,
        )

    @staticmethod
    def _normalize_category_name(category_name: str | None) -> str:
        return UIContent.UNKNOWN_CATEGORY if category_name is None else category_name

    def _create_emoji_button(self, emoji: EmojiData):
        ui.button(
            emoji.character,
            on_click=lambda selected=emoji: self._on_emoji_selected(selected)
        ).props(UIProps.EMOJI_PICKER_BUTTON).classes(UIClasses.EMOJI_BUTTON)

    def _on_emoji_selected(self, emoji: EmojiData):
        logger.info('Emoji selected: category=%s codepoint=%s name=%s', emoji.category, emoji.codepoint, emoji.name)
        self._view_model.select_emoji(emoji)
