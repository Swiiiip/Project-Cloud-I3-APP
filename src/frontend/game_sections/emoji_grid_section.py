# pyright: reportArgumentType=false

import logging

from nicegui import ui

from src.core.emoji.dto.emoji_category_data import EmojiCategoryData
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
        emoji_categories = self._view_model.emoji_pool
        is_locked = self._view_model.is_interaction_locked
        logger.info(
            'EmojiGridSection render start: category_count=%d selected_category=%s locked=%s',
            len(emoji_categories),
            self._selected_category,
            is_locked,
        )

        if not emoji_categories:
            logger.info('EmojiGridSection render skipped because emoji pool is empty')
            with ui.card().classes(UIClasses.EMOJI_LOADING_CARD):
                ui.spinner(size='md')
            return

        try:
            categories_by_name = {category.category: category for category in emoji_categories}
            logger.info(
                'EmojiGridSection received grouped categories: %s',
                [category.category for category in emoji_categories],
            )
            self._selected_category = self._ensure_selected_category(emoji_categories)

            if self._selected_category not in categories_by_name:
                logger.warning('EmojiGridSection has no selected category after grouping')
                with ui.card().classes(UIClasses.PANEL_CARD_CENTERED):
                    ui.label(UIContent.NO_EMOJIS_LABEL).classes(UIClasses.MUTED_TEXT)
                return

            current_category = categories_by_name[self._selected_category]
            current_emojis = current_category.emojis
            logger.info('EmojiGridSection rendering category=%s size=%d', self._selected_category, len(current_emojis))

            with ui.card().classes(UIClasses.EMOJI_CARD):
                with ui.column().classes(UIClasses.EMOJI_COLUMN_IN_CARD):
                    with ui.row().classes(UIClasses.CATEGORY_ROW):
                        for category in emoji_categories:
                            self._create_category_button(category.category, category.category == self._selected_category, is_locked)

                    with ui.scroll_area().classes(UIClasses.EMOJI_SCROLL_AREA):
                        with ui.row().classes(UIClasses.EMOJI_BUTTON_ROW):
                            for emoji in current_emojis:
                                self._create_emoji_button(emoji, is_locked)

            logger.info(
                'EmojiGridSection render complete: total_emojis=%d rendered_buttons=%d selected_category=%s',
                sum(len(category.emojis) for category in emoji_categories),
                len(current_emojis),
                self._selected_category,
            )
        except Exception as exc:
            logger.exception('EmojiGridSection render failed: %s', exc)
            with ui.card().classes(UIClasses.EMOJI_ERROR_CARD):
                ui.label(UIContent.EMOJI_GRID_ERROR_LABEL).classes(UIClasses.ERROR_TEXT)

    def _ensure_selected_category(self, categories: tuple[EmojiCategoryData, ...]) -> str:
        if not categories:
            logger.warning('EmojiGridSection _ensure_selected_category found no categories')
            return UIContent.UNKNOWN_CATEGORY

        selected_category = self._selected_category
        category_sizes = {category.category: len(category.emojis) for category in categories}
        category_names = set(category_sizes)
        if selected_category and selected_category in category_names:
            logger.info('EmojiGridSection keeping selected category=%s', selected_category)
            return selected_category

        preferred_categories = [category for category in categories if category.category != UIContent.UNKNOWN_CATEGORY]
        if preferred_categories:
            selected_category = max(preferred_categories, key=lambda category: len(category.emojis)).category
        else:
            selected_category = max(categories, key=lambda category: len(category.emojis)).category
        logger.info(
            'EmojiGridSection selected default category=%s size=%d',
            selected_category,
            category_sizes[selected_category],
        )
        return selected_category

    def _select_category(self, category_name: str) -> None:
        if self._view_model.is_interaction_locked:
            return
        selected_category = self._selected_category or UIContent.UNKNOWN_CATEGORY
        if category_name == selected_category:
            return

        self._selected_category = category_name
        self.render.refresh()

    def _create_category_button(self, category_name: str, is_active: bool, is_locked: bool) -> None:
        button = ui.button(category_name, on_click=lambda: self._select_category(category_name)).props(UIProps.EMOJI_CATEGORY_BUTTON)
        button.enabled = not is_locked
        if is_active:
            button.props(UIProps.EMOJI_CATEGORY_ACTIVE_BUTTON)
        else:
            button.props(UIProps.EMOJI_CATEGORY_INACTIVE_BUTTON)


    def _create_emoji_button(self, emoji: EmojiData, is_locked: bool):
        button = ui.button(
            emoji.character,
            on_click=lambda selected=emoji: self._on_emoji_selected(selected)
        ).props(UIProps.EMOJI_PICKER_BUTTON).classes(UIClasses.EMOJI_BUTTON)
        button.enabled = not is_locked

    def _on_emoji_selected(self, emoji: EmojiData):
        logger.info('Emoji selected: category=%s codepoint=%s name=%s', emoji.category, emoji.codepoint, emoji.name)
        self._view_model.select_emoji(emoji)
