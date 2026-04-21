from src.core.emoji.dto.emoji_category_data import EmojiCategoryData
from src.core.emoji.dto.emoji_data import EmojiData
from src.frontend.view.ui_constants import UIClasses
from nicegui import ui


class KeyboardEmojiPickerMode:
    def __init__(self, create_category_button, create_emoji_button):
        self._create_category_button = create_category_button
        self._create_emoji_button = create_emoji_button

    def render(self,
               emoji_categories: tuple[EmojiCategoryData, ...],
               selected_category: str,
               current_emojis: tuple[EmojiData, ...],
               is_locked: bool):
        with ui.row().classes(UIClasses.CATEGORY_ROW):
            for category in emoji_categories:
                self._create_category_button(category.category, category.category == selected_category, is_locked)

        with ui.scroll_area().classes(UIClasses.EMOJI_SCROLL_AREA):
            with ui.row().classes(UIClasses.EMOJI_BUTTON_ROW):
                for emoji in current_emojis:
                    self._create_emoji_button(emoji, is_locked)

