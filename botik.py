import random
import telebot
from telebot import types

bot = telebot.TeleBot('Token', parse_mode="HTML", skip_pending=True)
current_word = {}


def dictation_list(number_of_theme: str) -> dict:
    values = open(
        f'values {number_of_theme}.txt',
        encoding='utf-8',
    ).read().split('*')
    keys = open(
        f'keys {number_of_theme}.txt',
        encoding='utf-8',
    ).read().split('*')

    sorted_words = dict(zip(keys, values))
    return sorted_words


words_list = dictation_list('2')
for_copy = words_list


def pair_exists(dict1, dict2):
    for key in dict1:
        if key in dict2 and dict1[key] == dict2[key]:
            return True
    return False


def big_replace(string: str) -> str:
    return (string.replace(' ', '').
            replace('-', '').
            replace("'", '').
            replace('(', '').
            replace(')', ''))


def theme():
    themes = types.InlineKeyboardMarkup(row_width=2)
    theme_1 = types.InlineKeyboardButton(text="communication",
                                         callback_data="communication")
    theme_2 = types.InlineKeyboardButton(text="cultures",
                                         callback_data="cultures")
    theme_3 = types.InlineKeyboardButton(text="brands",
                                         callback_data="brands")
    theme_4 = types.InlineKeyboardButton(text="advertising",
                                         callback_data="advertising")
    themes.add(theme_1, theme_2, theme_3, theme_4)
    return themes


def make_list(theme_number: int, call, markup) -> dict:
    global words_list
    words_list = dictation_list(str(theme_number))
    bot.send_message(call.message.chat.id,
                     'Жми на кнопочку',
                     reply_markup=markup)
    return words_list


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,
                     'Привет, {0.first_name}!'
                     '\nЯ  недоделанный бот,'
                     'который поможет вам выучить слова (надеюсь).'
                     '\nЯ буду отправлять вам слова на русском, а вы пишите их на английском.'
                     '\n<b>Пожалуйста, отключите Т9, '
                     'чтобы думать самостоятельно!!</b>'
                     .format(message.from_user),
                     reply_markup=theme())


@bot.callback_query_handler(func=lambda call: True)
def select_theme_inline(call):
    global words_list
    next_step = types.InlineKeyboardMarkup()
    next_step.add(types.InlineKeyboardButton(text="хорошо",
                                             callback_data="next_question"))
    match call.data:
        case 'communication':
            make_list(1, call, next_step)
        case 'cultures':
            make_list(2, call, next_step)
        case 'brands':
            make_list(3, call, next_step)
        case 'advertising':
            make_list(4, call, next_step)
        case 'next_question':
            send_key(call.message)
        case 'another_theme':
            bot.send_message(call.message.chat.id,
                             'Выбирайте тему:',
                             reply_markup=theme())


@bot.message_handler(commands=['next'])
def send_key(message):
    global words_list, current_word, for_copy
    if not pair_exists(for_copy, words_list):
        for_copy = words_list
    copied_list = for_copy.copy()
    key = random.choice(list(copied_list.keys()))
    value = copied_list[key]
    copied_list.pop(key)
    for_copy = copied_list
    current_word[message.chat.id] = {'key': key, 'value': value}
    bot.send_message(message.chat.id, key)


@bot.message_handler(func=lambda message: True)
def check_answer(message):
    if message.chat.id in current_word:
        question = (big_replace(current_word[message.chat.id]['value']).
                    strip('\n').
                    split('или'))
        answer = big_replace(message.text.lower())
        next_step = types.InlineKeyboardMarkup()
        next_question = types.InlineKeyboardButton(text="дальше",
                                                   callback_data="next_question")
        select_theme = types.InlineKeyboardButton(text="поменять тему",
                                                  callback_data="another_theme")
        next_step.add(next_question, select_theme)
        if answer in question:
            bot.send_message(message.chat.id, '<b>Верно!</b>',
                             reply_markup=next_step)
        else:
            bot.send_message(message.chat.id, f'Не верно! '
                                              f'\n<b>Правильный ответ: '
                                              f'\n{(current_word[message.chat.id]['value'].
                                                    strip('\n').
                                                    split(' ответ ')
                                                    [-1])}</b>',
                             reply_markup=next_step)
        del current_word[message.chat.id]
    else:
        bot.send_message(message.chat.id, 'Отправьте /start, чтобы начать')


if __name__ == '__main__':
    bot.polling()
