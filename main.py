# main.py

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from grammar_data import grammar_db
import random

TOKEN = "7390296832:AAFZtTOK6JlxJ9WR3tI07HE8Mw56b1MSoTs"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

user_quiz_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "هلا فيك في Easy Grammar!\n\n"
        "اكتبي اسم أي قاعدة (مثلاً: past simple) وأنا أشرحها لك مع كويز!\n"
        "أوامر سريعة:\n"
        "/rules - القواعد المتوفرة\n"
        "/quiz - كويز عشوائي\n"
        "/today - قاعدة اليوم\n"
    )

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rules_list = "\n".join([f"- {rule.title()}" for rule in grammar_db.keys()])
    await update.message.reply_text(f"القواعد:\n{rules_list}")

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rule = random.choice(list(grammar_db.keys()))
    data = grammar_db[rule]
    quiz = data["quiz"]
    response = f"**قاعدة:** {rule.title()}\n"
    response += f"{data['explanation']}\n\n"
    response += "**أمثلة:**\n"
    for ex in data['examples']:
        response += f"- {ex}\n"
    response += f"\n**سؤال:**\n{quiz['question']}\n"
    for i, opt in enumerate(quiz["options"]):
        response += f"{i+1}. {opt}\n"

    user_quiz_state[update.effective_user.id] = quiz["correct_answer"]
    await update.message.reply_text(response)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    user_id = update.effective_user.id

    if text in grammar_db:
        data = grammar_db[text]
        response = f"**شرح قاعدة {text.title()}**\n"
        response += f"{data['explanation']}\n\n**أمثلة:**\n"
        for ex in data['examples']:
            response += f"- {ex}\n"
        quiz = data["quiz"]
        response += f"\n**سؤال:** {quiz['question']}\n"
        for i, opt in enumerate(quiz["options"]):
            response += f"{i+1}. {opt}\n"
        user_quiz_state[user_id] = quiz["correct_answer"]
        await update.message.reply_text(response)

    elif text in ["1", "2", "3"]:
        correct = user_quiz_state.get(user_id)
        if not correct:
            await update.message.reply_text("ما في كويز حالياً، اكتبي اسم قاعدة أول.")
        else:
            answer = int(text) - 1
            options = list(grammar_db.values())[0]["quiz"]["options"]
            if options[answer] == correct:
                await update.message.reply_text("صح عليك! ممتازة!")
            else:
                await update.message.reply_text(f"غلط، الجواب الصحيح هو:\n{correct}")
            user_quiz_state[user_id] = None
    else:
        await update.message.reply_text("ما فهمت عليك، جربي تكتبين اسم قاعدة مثل: past simple.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()