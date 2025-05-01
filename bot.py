import json
import asyncio
import aiohttp
from telegram import Bot, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, PreCheckoutQueryHandler
from telegram.error import TelegramError

TOKEN = '2200791277:AAGBpquvOx3RtXVVsrZ3hkgYhxy8zRnc0VY/test'  # Замените на действительный токен от BotFather
bot = Bot(token=TOKEN)
autizm = asyncio.Semaphore(100)  # Ограничение на 100 одновременных запросов

async def start(update, context):
    """Обработчик команды /start с инлайн-кнопками"""
    keyboard = [
        [InlineKeyboardButton("Обезьяна 🐵", callback_data='monkey')],
        [InlineKeyboardButton("Сердечки 💕", callback_data='love')],
        [InlineKeyboardButton("Хлопушки 🎉", callback_data='extra')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = (
        "Привет! Это Gift Bot 🎁\n\n"
        "Выбери тип подарков, которые хочешь отправить:\n"
    )
    try:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    except TelegramError as e:
        print(f"Ошибка при отправке сообщения /start: {e}")
        await update.message.reply_text("Произошла ошибка, попробуйте позже.")

async def stop(update, context):
    """Обработчик команды /stop для прерывания отправки подарков"""
    try:
        if context.user_data.get('sending_gifts', False):
            context.user_data['stop_sending'] = True
            await update.message.reply_text("Отправка подарков прервана!")
        else:
            await update.message.reply_text("Сейчас не выполняется отправка подарков.")
    except TelegramError as e:
        print(f"Ошибка при выполнении /stop: {e}")
        await update.message.reply_text("Произошла ошибка, попробуйте позже.")

async def penisi(target_id, description):
    """Отправка подарка через sendGift"""
    url = f'https://api.telegram.org/bot{TOKEN}/sendGift?chat_id={target_id}&gift_id=5453972608896729089&text={description}'
    async with autizm, aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return True
                else:
                    error_text = await resp.text()
                    print(f"Ошибка API (penisi): {error_text}")
                    return False
        except Exception as e:
            print(f"Ошибка (penisi): {e}")
            return False

async def penisi_love(target_id, description):
    """Отправка подарка через sendGift (для команды /love)"""
    url = f'https://api.telegram.org/bot{TOKEN}/sendGift?chat_id={target_id}&gift_id=5453972608896729089&text={description}'
    async with autizm, aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return True
                else:
                    error_text = await resp.text()
                    print(f"Ошибка API (penisi_love): {error_text}")
                    return False
        except Exception as e:
            print(f"Ошибка (penisi_love): {e}")
            return False

async def penisi_extra(target_id, description):
    """Отправка подарка через sendGift (для команды /extra)"""
    url = f'https://api.telegram.org/bot{TOKEN}/sendGift?chat_id={target_id}&gift_id=5453972608896729089&text={description}'
    async with autizm, aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return True
                else:
                    error_text = await resp.text()
                    print(f"Ошибка API (penisi_extra): {error_text}")
                    return False
        except Exception as e:
            print(f"Ошибка (penisi_extra): {e}")
            return False

async def popolnenie_naxyi(update, context):
    """Создание счёта для оплаты в XTR"""
    try:
        invoice = await bot.create_invoice_link(
            title="ём хуй",
            description="с любовью Lemon man",
            payload="я хз зачем оно",
            currency="XTR",
            prices=[LabeledPrice(label="10000", amount=100000)],
        )
        await update.message.reply_text(f"{invoice}\n")
    except TelegramError as e:
        print(f"Ошибка при создании счёта: {e}")
        await update.message.reply_text("Не удалось создать счёт. Попробуйте позже.")

async def xyi(update, context):
    """Обработка предварительного запроса на оплату"""
    try:
        query = update.pre_checkout_query
        await query.answer(ok=True)
    except TelegramError as e:
        print(f"Ошибка в pre_checkout_query: {e}")
        await query.answer(ok=False, error_message="Ошибка обработки платежа")

async def sosal(update, context):
    """Обработка успешного платежа"""
    try:
        payment = update.message.successful_payment
        await update.message.reply_text(
            f"успешна\nайди платежа: {payment.telegram_payment_charge_id}"
        )
    except TelegramError as e:
        print(f"Ошибка при обработке успешного платежа: {e}")
        await update.message.reply_text("Ошибка при обработке платежа.")

async def button_callback(update, context):
    """Обработчик нажатий на инлайн-кнопки"""
    try:
        query = update.callback_query
        await query.answer()

        # Обработка выбора типа подарка
        if query.data in ['monkey', 'love', 'extra']:
            context.user_data['gift_type'] = query.data  # Сохраняем тип подарка
            keyboard = [
                [InlineKeyboardButton("10", callback_data='count_10')],
                [InlineKeyboardButton("50", callback_data='count_50')],
                [InlineKeyboardButton("100", callback_data='count_100')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                "Сколько подарков отправить?",
                reply_markup=reply_markup
            )
            await query.message.delete()  # Удаляем предыдущее сообщение с кнопками

        # Обработка выбора количества
        elif query.data.startswith('count_'):
            count = int(query.data.split('_')[1])
            gift_type = context.user_data.get('gift_type')
            if not gift_type:
                await query.message.reply_text("Ошибка: выберите тип подарка заново с помощью /start")
                await query.message.delete()
                return

            # Выбор функции в зависимости от типа подарка
            if gift_type == 'monkey':
                gift_function = penisi
            elif gift_type == 'love':
                gift_function = penisi_love
            elif gift_type == 'extra':
                gift_function = penisi_extra
            else:
                await query.message.reply_text("Неизвестный тип подарка")
                await query.message.delete()
                return

            target_id = query.from_user.id
            description = "с любовью @Iol_man"

            # Устанавливаем флаг отправки
            context.user_data['sending_gifts'] = True
            context.user_data['stop_sending'] = False

            # Отправка подарков группами по 3 с интервалом 1 секунда
            results = []
            for i in range(0, count, 3):
                if context.user_data.get('stop_sending', False):
                    break  # Прерываем цикл, если получена команда /stop

                batch = [gift_function(target_id, description) for _ in range(min(3, count - i))]
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                results.extend(batch_results)
                if i + 3 < count and not context.user_data.get('stop_sending', False):
                    await asyncio.sleep(1)  # Задержка 1 секунда между группами

            # Сбрасываем флаги после завершения
            context.user_data['sending_gifts'] = False
            context.user_data['stop_sending'] = False

            success_count = sum(1 for r in results if r is True)
            if context.user_data.get('stop_sending', False):
                await query.message.reply_text(
                    f"Отправка прервана! Отправлено {success_count} из {count} подарков."
                )
            elif success_count == count:
                await query.message.reply_text("🎁 Все подарки отправлены!")
            else:
                await query.message.reply_text(
                    f"⚠️ Отправлено {success_count} из {count} подарков. Попробуйте позже."
                )
            await query.message.delete()  # Удаляем сообщение с выбором количества

    except TelegramError as e:
        print(f"Ошибка в button_callback: {e}")
        await query.message.reply_text("Произошла ошибка при отправке подарков.")
        context.user_data['sending_gifts'] = False
        context.user_data['stop_sending'] = False
    except Exception as e:
        print(f"Общая ошибка в button_callback: {e}")
        await query.message.reply_text("Произошла ошибка, попробуйте позже.")
        context.user_data['sending_gifts'] = False
        context.user_data['stop_sending'] = False

async def error_handler(update, context):
    """Глобальный обработчик ошибок"""
    print(f"Ошибка: {context.error}")
    if update and hasattr(update, 'message'):
        try:
            await update.message.reply_text("Произошла ошибка, попробуйте позже.")
        except TelegramError as e:
            print(f"Ошибка при отправке сообщения об ошибке: {e}")

def main():
    try:
        application = Application.builder().token(TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("stop", stop))
        application.add_handler(CommandHandler("xyi", popolnenie_naxyi))
        application.add_handler(PreCheckoutQueryHandler(xyi))
        application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, sosal))
        application.add_handler(CallbackQueryHandler(button_callback))
        application.add_error_handler(error_handler)  # Глобальный обработчик ошибок
        
        application.run_polling()
    except TelegramError as e:
        print(f"Ошибка при запуске бота: {e}")

if __name__ == '__main__':
    main()