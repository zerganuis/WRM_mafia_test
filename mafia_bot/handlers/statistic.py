
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from mafia_bot import config
from mafia_bot.handlers.response import send_text_response
from mafia_bot.templates import render_template
from mafia_bot.services.user import (
    insert_statistic_edit,
    delete_statistic_edit,
    get_statistic_edit,
    update_statistic_parameter
)
from mafia_bot.handlers.menu import get_id, get_prev_callback


async def edit_statistic_parameter_start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return
    param_name = get_id(query.data)
    prev_callback = get_prev_callback(query.data)
    editor_id = update.effective_user.id
    user_id = get_id(prev_callback)
    prev_callback = get_prev_callback(prev_callback)
    event_id = get_id(prev_callback)
    await insert_statistic_edit(editor_id, user_id, event_id)
    await send_text_response(update, context, render_template("score_edit.j2"))
    return param_name


async def edit_statistic_parameter(update: Update, context: ContextTypes.DEFAULT_TYPE, param_name: str):
    editor_id = update.effective_user.id
    ids = await get_statistic_edit(editor_id)
    param_value = int(update.message.text.strip())
    await update_statistic_parameter(ids['user_id'], ids['event_id'], param_name, param_value)
    await delete_statistic_edit(editor_id)
    await send_text_response(update, context, render_template("done.j2"))
    return ConversationHandler.END


async def _edit_statistic_score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await edit_statistic_parameter(update, context, "score")


async def _edit_statistic_gamecount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await edit_statistic_parameter(update, context, "game_count")


async def _edit_statistic_wincount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await edit_statistic_parameter(update, context, "win_count")


async def _cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await send_text_response(
        update,
        context,
        render_template("cancel.j2")
    )
    return ConversationHandler.END


def get_edit_user_score_conversation() -> ConversationHandler:
    pattern = rf"^{config.GRADE_REQEST_CALLBACK_PATTERN}(.+)$"
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(edit_statistic_parameter_start_button, pattern=pattern)],
        states={
            "score": [MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                _edit_statistic_score
                )],
            "gamecount": [MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                _edit_statistic_gamecount
                )],
            "wincount": [MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                _edit_statistic_wincount
                )]
        },
        fallbacks=[MessageHandler(filters.COMMAND, _cancel)]
    )
