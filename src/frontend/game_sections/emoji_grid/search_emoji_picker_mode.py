from nicegui import ui

from src.core.emoji.dto.emoji_category_data import EmojiCategoryData
from src.core.emoji.dto.emoji_data import EmojiData
from src.frontend.ui_constants import UIClasses, UIContent


class SearchEmojiPickerMode:
    def __init__(self, create_emoji_button, select_emoji, submit_guess, remove_last_selection, can_submit):
        self._create_emoji_button = create_emoji_button
        self._select_emoji = select_emoji
        self._submit_guess = submit_guess
        self._remove_last_selection = remove_last_selection
        self._can_submit = can_submit
        self._search_query = ''
        self._emoji_categories: tuple[EmojiCategoryData, ...] = ()
        self._is_locked = False
        self._search_input = None

    def render(self,
               emoji_categories: tuple[EmojiCategoryData, ...],
               is_locked: bool):
        self._emoji_categories = emoji_categories
        self._is_locked = is_locked
        search_input = ui.input(
            value=self._search_query,
            placeholder=UIContent.EMOJI_SEARCH_PLACEHOLDER,
        ).classes(UIClasses.EMOJI_SEARCH_INPUT)
        self._search_input = search_input
        search_input.on_value_change(lambda event: self._set_search_query(str(event.value or '')))
        search_input.on('keydown.enter', lambda _: self._on_enter_pressed())
        search_input.on('keydown.backspace', lambda _: self._on_backspace_pressed())

        self._render_search_results()

    @ui.refreshable
    def _render_search_results(self):
        with ui.scroll_area().classes(UIClasses.EMOJI_SCROLL_AREA):
            with ui.row().classes(UIClasses.EMOJI_BUTTON_ROW):
                matched_emojis = self._search_emojis(self._emoji_categories)
                if not self._search_query:
                    ui.label(UIContent.EMOJI_SEARCH_HINT).classes(UIClasses.MUTED_TEXT)
                    return

                if not matched_emojis:
                    ui.label(UIContent.EMOJI_SEARCH_NO_RESULTS).classes(UIClasses.MUTED_TEXT)
                    return

                for index, emoji in enumerate(matched_emojis):
                    highlight_class = UIClasses.EMOJI_BUTTON_SUGGESTED if index == 0 else None
                    self._create_emoji_button(emoji, self._is_locked, highlight_class)

    def _set_search_query(self, query: str):
        normalized_query = query.strip()
        if normalized_query == self._search_query:
            return
        self._search_query = normalized_query
        self._render_search_results.refresh()

    def _on_enter_pressed(self) -> None:
        if self._can_submit() and not self._is_locked:
            self._submit_guess()
            return
        if self._search_query:
            self._select_top_result()

    def _on_backspace_pressed(self) -> None:
        if self._search_query:
            return
        self._remove_last_selection()

    def _select_top_result(self) -> None:
        if self._is_locked:
            return
        matched_emojis = self._search_emojis(self._emoji_categories)
        if not matched_emojis:
            return
        self._select_emoji(matched_emojis[0])
        self._clear_search_query()

    def _clear_search_query(self) -> None:
        if self._search_query == '':
            return
        self._search_query = ''
        if self._search_input is not None:
            self._search_input.set_value('')
        self._render_search_results.refresh()

    def clear_search_query(self) -> None:
        self._clear_search_query()

    @staticmethod
    def _all_emojis(categories: tuple[EmojiCategoryData, ...]) -> tuple[EmojiData, ...]:
        unique_emojis: list[EmojiData] = []
        seen_codepoints: set[str] = set()
        for category in categories:
            for emoji in category.emojis:
                if emoji.codepoint in seen_codepoints:
                    continue
                seen_codepoints.add(emoji.codepoint)
                unique_emojis.append(emoji)
        return tuple(unique_emojis)

    def _search_emojis(self, categories: tuple[EmojiCategoryData, ...]) -> tuple[EmojiData, ...]:
        query_terms = tuple(term for term in self._search_query.lower().split() if term)
        if not query_terms:
            return ()

        ranked_matches: list[tuple[int, int, str, EmojiData]] = []
        for emoji in self._all_emojis(categories):
            score = self._score_emoji_relevance(emoji, query_terms)
            if score <= 0:
                continue
            ranked_matches.append((score, emoji.keyboard_position, emoji.name.casefold(), emoji))

        ranked_matches.sort(key=lambda item: (-item[0], item[1], item[2]))
        return tuple(item[3] for item in ranked_matches)

    @staticmethod
    def _score_emoji_relevance(emoji: EmojiData, query_terms: tuple[str, ...]) -> int:
        name = emoji.name.casefold()
        keywords = tuple(keyword.casefold() for keyword in emoji.keywords)

        score = 0
        for term in query_terms:
            term_score = 0
            if term == name:
                term_score = max(term_score, 160)
            elif name.startswith(term):
                term_score = max(term_score, 120)
            elif term in name:
                term_score = max(term_score, 80)

            for keyword in keywords:
                if term == keyword:
                    term_score = max(term_score, 200)
                elif keyword.startswith(term):
                    term_score = max(term_score, 140)
                elif term in keyword:
                    term_score = max(term_score, 100)

            score += term_score

        return score

