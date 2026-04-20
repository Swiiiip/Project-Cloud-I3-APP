class UIColors:
    BODY_BACKGROUND = '#121212'
    BODY_TEXT = 'white'
    PANEL_BACKGROUND = '#1e1e1e'
    PANEL_BORDER = '#333'
    SLOT_BACKGROUND = '#111'
    SLOT_BORDER = '#555'
    ATTEMPT_BACKGROUND = '#151515'
    ATTEMPT_BORDER = '#222'
    GRID_SCROLL_BORDER = '#2a2a2a'
    SUBMIT_ENABLED = '#16a34a'
    SUBMIT_DISABLED = '#6b7280'
    ERROR_ICON = 'red-500'
    SUCCESS_ICON = 'green-500'


class UIContent:
    APP_TITLE = '🤫 BLURMOJI'
    SOLVED_LABEL = 'SOLVED'
    NO_EMOJIS_LABEL = 'No emojis available'
    EMOJI_GRID_ERROR_LABEL = 'Keyboard failed to render'
    UNKNOWN_CATEGORY = 'Unknown'
    DEFAULT_SLOT_CHAR = '?'
    EMPTY_ATTEMPT_LABEL = '• •'
    GUESS_PAIR_SEPARATOR = ' • '
    DAILY_CHALLENGE_TEMPLATE = 'Daily Challenge - {date}'
    ATTEMPTS_TITLE = 'ATTEMPTS'
    SUCCESS_MESSAGE = 'Well played!'
    FAILURE_MESSAGE = 'Better luck next time.'
    CHALLENGE_NAME_TEMPLATE = 'The emoji mashup was a "{name}"'


class UIClasses:
    BODY = f'bg-[{UIColors.BODY_BACKGROUND}] text-[{UIColors.BODY_TEXT}]'
    HEADER = f'bg-[{UIColors.PANEL_BACKGROUND}] border-b border-[{UIColors.PANEL_BORDER}] items-center justify-center w-full'
    HEADER_TITLE = 'text-2xl font-black tracking-tighter p-4'

    MAIN_LAYOUT = 'w-full gap-3 p-3 items-start content-start flex-wrap'
    COLUMN_BASE = 'flex flex-col flex-1'
    IMAGE_COLUMN = 'flex-[2_1_420px] min-w-[320px]'
    HISTORY_COLUMN = 'flex-[1_1_300px] min-w-[280px]'
    EMOJI_COLUMN = 'flex-[2_1_420px] min-w-[320px]'

    PANEL_CARD = f'w-full bg-[{UIColors.PANEL_BACKGROUND}] border border-[{UIColors.PANEL_BORDER}]'
    PANEL_CARD_CENTERED = f'{PANEL_CARD} items-center justify-center'
    PANEL_CARD_PADDED = f'{PANEL_CARD} p-3'

    WORKBENCH_CONTAINER = 'w-full gap-3 flex flex-col flex-1'
    WORKBENCH_CARD = f'w-full bg-[{UIColors.PANEL_BACKGROUND}] border border-[{UIColors.PANEL_BORDER}] p-3'
    WORKBENCH_ROW = 'w-full items-center justify-center gap-3'
    SLOT_ROW = 'items-center justify-center gap-2'
    SLOT_LABEL = f'w-14 h-14 flex items-center justify-center bg-[{UIColors.SLOT_BACKGROUND}] rounded-lg text-3xl border border-[{UIColors.SLOT_BORDER}]'

    HISTORY_CARD = f'w-full bg-[{UIColors.PANEL_BACKGROUND}] border border-[{UIColors.PANEL_BORDER}] p-3 flex flex-col flex-1'
    HISTORY_SCROLL = 'w-full gap-2 flex flex-col'
    ATTEMPTS_META = 'text-gray-400 text-xs font-black text-center'
    ATTEMPTS_COUNTER_ROW = 'w-full items-center justify-center gap-2'
    ATTEMPTS_COUNTER_SLOT = f'w-14 h-14 flex items-center justify-center bg-[{UIColors.SLOT_BACKGROUND}] rounded-lg text-lg border border-[{UIColors.SLOT_BORDER}]'
    ATTEMPT_ROW = 'w-full items-center justify-center gap-2'
    ATTEMPT_PAIR = 'items-center justify-center gap-2'
    ATTEMPT_GUESS = f'w-14 h-14 flex items-center justify-center bg-[{UIColors.SLOT_BACKGROUND}] rounded-lg text-3xl border border-[{UIColors.SLOT_BORDER}]'
    ATTEMPT_EMPTY = f'w-14 h-14 flex items-center justify-center bg-[{UIColors.SLOT_BACKGROUND}] rounded-lg text-3xl border border-[{UIColors.SLOT_BORDER}] text-gray-600'
    ATTEMPT_GUESS_CORRECT = f'w-14 h-14 flex items-center justify-center bg-green-700 rounded-lg text-3xl border border-green-600'
    ATTEMPT_GUESS_INCORRECT = f'w-14 h-14 flex items-center justify-center bg-red-900 rounded-lg text-3xl border border-red-700'
    MUTED_TEXT = 'text-gray-400'
    ERROR_TEXT = 'text-red-400'

    EMOJI_LOADING_CARD = PANEL_CARD_CENTERED
    EMOJI_CARD = f'{PANEL_CARD} p-2 flex flex-col flex-1'
    EMOJI_ERROR_CARD = f'{PANEL_CARD} border-red-700 items-center justify-center'
    EMOJI_COLUMN_IN_CARD = 'w-full gap-2 flex flex-col flex-1'
    CATEGORY_ROW = 'w-full gap-1 overflow-x-auto flex-nowrap items-center'
    EMOJI_SCROLL_AREA = f'w-full border border-[{UIColors.GRID_SCROLL_BORDER}] rounded-md p-1'
    EMOJI_BUTTON_ROW = 'w-full justify-start items-start content-start gap-1 flex-wrap'
    EMOJI_BUTTON = 'text-2xl p-1 rounded-lg hover:bg-white/10 w-10 h-10'

    CHALLENGE_IMAGE = 'w-full h-auto max-h-[340px] object-contain rounded-lg'
    DAILY_CHALLENGE_TEXT = 'w-full text-center text-lg text-gray-300 mb-2 font-semibold'
    SOLVED_LABEL = 'text-center font-bold text-xl mt-2 text-green-400'
    COMMUNICATION_CARD = f'w-full min-h-[110px] bg-[{UIColors.PANEL_BACKGROUND}] border border-[{UIColors.PANEL_BORDER}] p-3'
    COMMUNICATION_TITLE = 'text-gray-400 text-xs font-black mb-2'
    COMMUNICATION_TEXT = 'text-sm text-gray-200'
    COMMUNICATION_SUCCESS = 'text-sm text-green-400 font-semibold'
    COMMUNICATION_FAILURE = 'text-sm text-red-400 font-semibold'
    COMMUNICATION_PLACEHOLDER = 'text-sm text-gray-500'


class UIProps:
    ROUND_BUTTON = 'round'
    DELETE_BUTTON = 'round flat color=grey'
    EMOJI_CATEGORY_BUTTON = 'dense no-caps'
    EMOJI_CATEGORY_ACTIVE_BUTTON = 'color=primary'
    EMOJI_CATEGORY_INACTIVE_BUTTON = 'flat color=grey-7'
    EMOJI_PICKER_BUTTON = 'flat'


class UIIcons:
    SUBMIT = 'check'
    RESET = 'delete'
    FAILED_ATTEMPT = 'close'


def format_guess_pair(first_character: str, second_character: str) -> str:
    return f'{first_character}{UIContent.GUESS_PAIR_SEPARATOR}{second_character}'


def format_daily_challenge_label(formatted_date: str) -> str:
    return UIContent.DAILY_CHALLENGE_TEMPLATE.format(date=formatted_date)
