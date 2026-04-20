import logging
import asyncio

from nicegui import ui

from ..abstract_guess_submitter import AbstractGuessSubmitter
from .emoji_grid_mode import EmojiGridMode
from .keyboard_emoji_picker_mode import KeyboardEmojiPickerMode
from .search_emoji_picker_mode import SearchEmojiPickerMode
from src.core.emoji.dto.emoji_category_data import EmojiCategoryData
from src.core.emoji.dto.emoji_data import EmojiData
from src.frontend.ui_constants import UIClasses, UIContent, UIProps
from src.frontend.view_model import BlurmojiViewModel

logger = logging.getLogger(__name__)


class EmojiGridSection:
    def __init__(self, view_model: BlurmojiViewModel, guess_submitter: AbstractGuessSubmitter):
        self._view_model = view_model
        self._guess_submitter = guess_submitter
        self._selected_category: str = UIContent.UNKNOWN_CATEGORY
        self._picker_mode: EmojiGridMode = EmojiGridMode.KEYBOARD
        self._keyboard_picker = KeyboardEmojiPickerMode(self._create_category_button, self._create_emoji_button)
        self._search_picker = SearchEmojiPickerMode(
            self._create_emoji_button,
            self._on_emoji_selected,
            self._submit_guess_from_shortcut,
            self._remove_last_selection,
            lambda: self._view_model.can_submit,
        )

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
            with ui.card().classes(f'{UIClasses.EMOJI_LOADING_CARD} flex-1'):
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
                with ui.card().classes(f'{UIClasses.PANEL_CARD_CENTERED} flex-1'):
                    ui.label(UIContent.NO_EMOJIS_LABEL).classes(UIClasses.MUTED_TEXT)
                return

            current_category = categories_by_name[self._selected_category]
            current_emojis = current_category.emojis
            logger.info('EmojiGridSection rendering category=%s size=%d', self._selected_category, len(current_emojis))

            with ui.card().classes(UIClasses.EMOJI_CARD):
                with ui.column().classes(UIClasses.EMOJI_COLUMN_IN_CARD):
                    self._render_mode_selector()
                    if self._picker_mode == EmojiGridMode.SEARCH:
                        self._search_picker.render(emoji_categories, is_locked)
                    elif self._picker_mode == EmojiGridMode.KEYBOARD:
                        self._keyboard_picker.render(emoji_categories, self._selected_category, current_emojis, is_locked)

            logger.info(
                'EmojiGridSection render complete: total_emojis=%d rendered_buttons=%d selected_category=%s',
                sum(len(category.emojis) for category in emoji_categories),
                len(current_emojis),
                self._selected_category,
            )
        except Exception as exc:
            logger.exception('EmojiGridSection render failed: %s', exc)
            with ui.card().classes(f'{UIClasses.EMOJI_ERROR_CARD} flex-1'):
                ui.label(UIContent.EMOJI_GRID_ERROR_LABEL).classes(UIClasses.ERROR_TEXT)

    def _ensure_selected_category(self, categories: tuple[EmojiCategoryData, ...]) -> str:
        if not categories:
            logger.warning('EmojiGridSection _ensure_selected_category found no categories')
            return UIContent.UNKNOWN_CATEGORY

        selected_category = self._selected_category
        category_names = {category.category for category in categories}
        if selected_category and selected_category in category_names and selected_category != UIContent.UNKNOWN_CATEGORY:
            logger.info('EmojiGridSection keeping selected category=%s', selected_category)
            return selected_category

        for category in categories:
            if category.category != UIContent.UNKNOWN_CATEGORY:
                logger.info('EmojiGridSection selected default category=%s', category.category)
                return category.category

        logger.info('EmojiGridSection selected default category=%s', UIContent.UNKNOWN_CATEGORY)
        return UIContent.UNKNOWN_CATEGORY

    def _select_category(self, category_name: str) -> None:
        if self._view_model.is_interaction_locked:
            return
        selected_category = self._selected_category or UIContent.UNKNOWN_CATEGORY
        if category_name == selected_category:
            return

        self._selected_category = category_name
        self.render.refresh()

    def _set_picker_mode(self, mode: EmojiGridMode) -> None:
        if mode == self._picker_mode:
            return
        self._picker_mode = mode
        self.render.refresh()

    def _render_mode_selector(self) -> None:
        with ui.row().classes(UIClasses.EMOJI_MODE_ROW):
            self._create_mode_button(EmojiGridMode.KEYBOARD, UIContent.EMOJI_MODE_KEYBOARD_LABEL)
            self._create_mode_button(EmojiGridMode.SEARCH, UIContent.EMOJI_MODE_SEARCH_LABEL)

    def _create_mode_button(self, mode: EmojiGridMode, label: str) -> None:
        button = ui.button(label, on_click=lambda: self._set_picker_mode(mode)).props(UIProps.EMOJI_MODE_BUTTON).classes(UIClasses.EMOJI_MODE_BUTTON)
        if self._picker_mode == mode:
            button.props(UIProps.EMOJI_MODE_ACTIVE_BUTTON)
        else:
            button.props(UIProps.EMOJI_MODE_INACTIVE_BUTTON)

    def _create_category_button(self, category_name: str, is_active: bool, is_locked: bool) -> None:
        button = ui.button(category_name, on_click=lambda: self._select_category(category_name)).props(UIProps.EMOJI_CATEGORY_BUTTON)
        button.enabled = not is_locked
        if is_active:
            button.props(UIProps.EMOJI_CATEGORY_ACTIVE_BUTTON)
        else:
            button.props(UIProps.EMOJI_CATEGORY_INACTIVE_BUTTON)

    def _create_emoji_button(self, emoji: EmojiData, is_locked: bool, extra_classes: str | None = None):
        with ui.button(
            emoji.character,
            on_click=lambda selected=emoji: self._on_emoji_selected(selected)
        ).props(UIProps.EMOJI_PICKER_BUTTON).classes(UIClasses.EMOJI_BUTTON) as button:
            button.enabled = not is_locked
            ui.tooltip(emoji.name)
            if extra_classes:
                button.classes(extra_classes)
            return button

    def _on_emoji_selected(self, emoji: EmojiData):
        logger.info('Emoji selected: category=%s codepoint=%s name=%s', emoji.category, emoji.codepoint, emoji.name)
        self._view_model.select_emoji(emoji)
        if self._picker_mode == EmojiGridMode.SEARCH:
            self._search_picker.clear_search_query()

    def _submit_guess_from_shortcut(self) -> None:
        asyncio.ensure_future(self._guess_submitter.submit_guess())

    def _remove_last_selection(self) -> bool:
        return self._view_model.remove_last_selection()

