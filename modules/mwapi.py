__version__ = (1, 0, 0)
# meta developer: @mwoffice & @zern18i
import aiohttp
import json
import base64
import io
from .. import loader, utils

@loader.tds
class MWAPIModule(loader.Module):
    """Модуль для работы с MW API"""

    strings = {
        "name": "MWAPI",
        "no_api_key": "❌ <b>API ключ не установлен</b>\n\n💡 Используйте: <code>.mwkey ваш_ключ</code>",
        "api_key_set": "✅ <b>API ключ сохранен</b>",
        "no_model": "❌ <b>Модель не установлена</b>",
        "model_set": "✅ <b>Модель установлена:</b> <code>{}</code>",
        "no_query": "❌ <b>Укажите запрос</b>\n\n💡 Пример: <code>.mw Привет, как дела?</code>",
        "processing": "⏳ <b>Обработка запроса...</b>",
        "error": "❌ <b>Ошибка:</b>\n<code>{}</code>",
        "response": "🤖 <b>Ответ ИИ:</b>\n\n{}",
        "history_cleared": "🗑 <b>История диалога очищена</b>\n\n💡 Начните новый диалог с ИИ",
        "history_empty": "📭 <b>История диалога пуста</b>\n\n💡 Отправьте запрос командой <code>.mw</code>",
        "config_menu": "⚙️ <b>Конфигурация MWAPI</b>\n\n"
                      "📊 <b>Модель:</b> <code>{}</code>\n"
                      "🔑 <b>API ключ:</b> <code>{}</code>\n"
                      "🌡 <b>Температура:</b> <code>{}</code>\n"
                      "📝 <b>Макс. токенов:</b> <code>{}</code>\n\n"
                      "💡 Используйте кнопки ниже для настройки",
        "enter_model": "📊 <b>Выберите модель ИИ:</b>\n\n"
                      "💡 <b>По умолчанию:</b> gpt-4o, gpt-3.5-turbo\n\n"
                      "📋 <b>Список моделей и цены:</b>\n<code>https://api.mwshark.host/pricing</code>\n\n"
                      "⚠️ <i>Или введите название модели командой:</i> <code>.mwmodel название</code>",
        "enter_temp": "🌡 <b>Введите температуру (0-1):</b>\n\n💡 Чем выше значение, тем более креативные ответы",
        "enter_tokens": "📝 <b>Введите максимальное количество токенов:</b>\n\n💡 Рекомендуется: 512-2048",
        "temp_set": "✅ <b>Температура установлена:</b> <code>{}</code>",
        "tokens_set": "✅ <b>Макс. токенов установлено:</b> <code>{}</code>",
        "invalid_temp": "❌ <b>Температура должна быть от 0 до 1</b>",
        "invalid_tokens": "❌ <b>Количество токенов должно быть положительным числом</b>",
        "first_time_setup": "👋 <b>Добро пожаловать в MW API!</b>\n\n"
                           "🚀 <b>Быстрая настройка за 4 шага:</b>\n\n"
                           "1️⃣ Регистрация на платформе\n"
                           "2️⃣ Получение API ключа\n"
                           "3️⃣ Установка ключа в модуль\n"
                           "4️⃣ Активация тест-периода\n\n"
                           "💡 <i>Нажмите \"Начать\" для пошаговой инструкции</i>",
        "setup_step1": "1️⃣ <b>Регистрация на платформе</b>\n\n"
                      "📝 Создайте аккаунт на MW API\n\n"
                      "🔹 Нажмите кнопку \"Регистрация\" ниже\n"
                      "🔹 Заполните форму регистрации\n"
                      "🔹 Запомните ваш username в биллинге\n\n"
                      "⚠️ <b>Важно:</b> Username понадобится для тест-периода",
        "setup_step2": "2️⃣ <b>Получение API ключа</b>\n\n"
                      "🔑 Создайте токен в консоли\n\n"
                      "🔹 Откройте консоль токенов\n"
                      "🔹 Нажмите \"Создать токен\"\n"
                      "🔹 Скопируйте полученный ключ\n\n"
                      "💡 <b>Совет:</b> Сохраните ключ в надежном месте",
        "setup_step3": "3️⃣ <b>Установка API ключа</b>\n\n"
                      "📋 Добавьте ключ в модуль\n\n"
                      "🔹 Скопируйте команду ниже\n"
                      "🔹 Вставьте ваш API ключ после команды\n"
                      "🔹 Отправьте команду в чат\n\n"
                      "📝 <b>Формат:</b> <code>.mwkey ваш_api_ключ</code>",
        "setup_step4": "4️⃣ <b>Активация тест-периода</b>\n\n"
                      "🎁 Получите 15₽ для тестирования\n\n"
                      "🔹 Скопируйте команду ниже\n"
                      "🔹 Добавьте ваш username после команды\n"
                      "🔹 Отправьте команду в чат\n\n"
                      "📝 <b>Формат:</b> <code>.mwtest ваш_username</code>\n\n"
                      "⚠️ <b>Важно:</b> Используйте username из биллинга",
        "test_period_info": "🎁 <b>Тест-период MW API</b>\n\n"
                           "📝 <b>Что вы получите:</b>\n"
                           "• 15₽ на баланс для тестирования\n"
                           "• Доступ ко всем моделям\n"
                           "• Возможность оценить качество сервиса\n\n"
                           "⚠️ <b>Важно:</b>\n"
                           "• Тест-период можно получить только 1 раз\n"
                           "• Требуется username из биллинга\n\n"
                           "💡 Нажмите \"Продолжить\" для получения",
        "test_period_email": "👤 <b>Введите ваш username</b>\n\n"
                            "💡 Укажите username, который вы использовали при регистрации в биллинге MW\n\n"
                            "⚠️ Username должен быть действительным",
        "test_period_sent": "✅ <b>Запрос отправлен!</b>\n\n"
                           "📨 Ваш запрос на тест-период отправлен администратору\n\n"
                           "⏳ Ожидайте подтверждения\n"
                           "💬 Вы получите уведомление после проверки",
        "test_period_spam": "⚠️ <b>Обнаружен спамбан</b>\n\n"
                           "😔 К сожалению, вы не можете отправить запрос напрямую\n\n"
                           "💡 <b>Как решить проблему:</b>\n\n"
                           "1️⃣ Скопируйте сообщение ниже кнопкой \"Копировать\"\n"
                           "2️⃣ Попросите друга или знакомого (без спамбана)\n"
                           "3️⃣ Пусть он отправит это сообщение администратору\n\n"
                           "📱 <b>Сообщение для отправки:</b>\n\n"
                           "<code>{}</code>\n\n"
                           "⚠️ <b>Важно:</b> Укажите ваш username в сообщении",
        "test_period_already": "⚠️ <b>Вы уже запрашивали тест-период</b>\n\n"
                              "💡 Тест-период можно получить только один раз",
        "quota_exceeded": "💰 <b>Квота токена исчерпана</b>\n\n"
                         "📊 У вашего API ключа закончился лимит запросов\n\n"
                         "💡 <b>Решение проблемы:</b>\n\n"
                         "🔹 <b>Первый раз используете?</b>\n"
                         "   Увеличьте лимит токена в консоли\n\n"
                         "🔹 <b>Лимит уже максимальный?</b>\n"
                         "   Пополните баланс через администратора\n\n"
                         "🔹 <b>Хотите протестировать?</b>\n"
                         "   Запросите тест-период (15₽)",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "api_key",
                None,
                lambda: "MW API ключ",
                validator=loader.validators.Hidden(),
            ),
            loader.ConfigValue(
                "model",
                "gpt-4o",
                lambda: "Модель ИИ",
            ),
            loader.ConfigValue(
                "temperature",
                0.7,
                lambda: "Случайность ответа (0-1)",
                validator=loader.validators.Float(minimum=0, maximum=1),
            ),
            loader.ConfigValue(
                "max_tokens",
                512,
                lambda: "Максимум токенов в ответе",
                validator=loader.validators.Integer(minimum=1),
            ),
            loader.ConfigValue(
                "api_url",
                "https://api.mwshark.host/v1/chat/completions",
                lambda: "API эндпоинт",
            ),
        )

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self._test_period_requests = self.db.get("MWAPI", "test_period_requests", {})
        self._chat_history = self.db.get("MWAPI", "chat_history", {})

    async def _get_config_menu(self):
        api_key = self.config["api_key"]
        key_display = f"{api_key[:8]}...{api_key[-4:]}" if api_key else "Не установлен"

        return {
            "text": self.strings["config_menu"].format(
                self.config["model"],
                key_display,
                self.config["temperature"],
                self.config["max_tokens"],
            ),
            "reply_markup": [
                [
                    {"text": "📊 Модель", "callback": self._set_model},
                ],
                [
                    {"text": "🌡 Температура", "callback": self._set_temp},
                    {"text": "📝 Токены", "callback": self._set_tokens},
                ],
                [{"text": "🔄 Обновить", "callback": self._refresh_config}],
                [{"text": "❌ Закрыть", "action": "close"}],
            ],
        }

    async def _refresh_config(self, call):
        await call.edit(**await self._get_config_menu())

    async def _set_model(self, call):
        current_model = self.config["model"]

        gpt4o_text = "✅ gpt-4o" if current_model == "gpt-4o" else "gpt-4o"
        gpt35_text = "✅ gpt-3.5-turbo" if current_model == "gpt-3.5-turbo" else "gpt-3.5-turbo"

        await call.edit(
            self.strings["enter_model"],
            reply_markup=[
                [
                    {"text": gpt4o_text, "callback": self._model_gpt4o},
                ],
                [
                    {"text": gpt35_text, "callback": self._model_gpt35},
                ],
                [
                    {"text": "📋 Список моделей", "url": "https://api.mwshark.host/pricing"},
                ],
                [{"text": "◀️ Назад", "callback": self._refresh_config}],
            ],
        )

    async def _model_gpt4o(self, call):
        self.config["model"] = "gpt-4o"
        await call.answer("✅ Модель: gpt-4o")
        await call.edit(**await self._get_config_menu())

    async def _model_gpt35(self, call):
        self.config["model"] = "gpt-3.5-turbo"
        await call.answer("✅ Модель: gpt-3.5-turbo")
        await call.edit(**await self._get_config_menu())

    async def _set_temp(self, call):
        await call.edit(
            self.strings["enter_temp"],
            reply_markup=[
                [
                    {"text": "0.3", "callback": self._temp_03},
                    {"text": "0.5", "callback": self._temp_05},
                    {"text": "0.7", "callback": self._temp_07},
                ],
                [
                    {"text": "0.9", "callback": self._temp_09},
                    {"text": "1.0", "callback": self._temp_10},
                ],
                [{"text": "◀️ Назад", "callback": self._refresh_config}],
            ],
        )

    async def _temp_03(self, call):
        self.config["temperature"] = 0.3
        await call.answer("✅ Температура: 0.3")
        await call.edit(**await self._get_config_menu())

    async def _temp_05(self, call):
        self.config["temperature"] = 0.5
        await call.answer("✅ Температура: 0.5")
        await call.edit(**await self._get_config_menu())

    async def _temp_07(self, call):
        self.config["temperature"] = 0.7
        await call.answer("✅ Температура: 0.7")
        await call.edit(**await self._get_config_menu())

    async def _temp_09(self, call):
        self.config["temperature"] = 0.9
        await call.answer("✅ Температура: 0.9")
        await call.edit(**await self._get_config_menu())

    async def _temp_10(self, call):
        self.config["temperature"] = 1.0
        await call.answer("✅ Температура: 1.0")
        await call.edit(**await self._get_config_menu())

    async def _set_tokens(self, call):
        await call.edit(
            self.strings["enter_tokens"],
            reply_markup=[
                [
                    {"text": "512", "callback": self._tokens_512},
                    {"text": "1024", "callback": self._tokens_1024},
                ],
                [
                    {"text": "2048", "callback": self._tokens_2048},
                    {"text": "4096", "callback": self._tokens_4096},
                ],
                [{"text": "◀️ Назад", "callback": self._refresh_config}],
            ],
        )

    async def _tokens_512(self, call):
        self.config["max_tokens"] = 512
        await call.answer("✅ Токены: 512")
        await call.edit(**await self._get_config_menu())

    async def _tokens_1024(self, call):
        self.config["max_tokens"] = 1024
        await call.answer("✅ Токены: 1024")
        await call.edit(**await self._get_config_menu())

    async def _tokens_2048(self, call):
        self.config["max_tokens"] = 2048
        await call.answer("✅ Токены: 2048")
        await call.edit(**await self._get_config_menu())

    async def _tokens_4096(self, call):
        self.config["max_tokens"] = 4096
        await call.answer("✅ Токены: 4096")
        await call.edit(**await self._get_config_menu())

    @loader.command()
    async def mwconfig(self, message):
        """Открыть меню настроек"""
        if not self.config["api_key"]:
            await self.inline.form(
                self.strings["first_time_setup"],
                reply_markup=[
                    [{"text": "🚀 Начать настройку", "callback": self._setup_step1}],
                    [{"text": "❌ Закрыть", "action": "close"}],
                ],
                message=message,
            )
            return
        await self.inline.form(**await self._get_config_menu(), message=message)

    @loader.command()
    async def mwkey(self, message):
        """<ключ> - Установить API ключ"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_api_key"])
            return

        self.config["api_key"] = args
        await utils.answer(message, self.strings["api_key_set"])

    @loader.command()
    async def mwmodel(self, message):
        """<модель> - Установить модель ИИ"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_model"])
            return

        self.config["model"] = args
        await utils.answer(message, self.strings["model_set"].format(args))

    @loader.command()
    async def mwclear(self, message):
        """Очистить историю диалога в текущем чате"""
        chat_id = str(utils.get_chat_id(message))

        if chat_id in self._chat_history and self._chat_history[chat_id]:
            self._chat_history[chat_id] = []
            self.db.set("MWAPI", "chat_history", self._chat_history)
            await utils.answer(message, self.strings["history_cleared"])
        else:
            await utils.answer(message, self.strings["history_empty"])

    async def _clear_history_callback(self, call):
        """Очистить историю через callback кнопку"""
        chat_id = str(call.message.chat_id)

        if chat_id in self._chat_history and self._chat_history[chat_id]:
            self._chat_history[chat_id] = []
            self.db.set("MWAPI", "chat_history", self._chat_history)
            await call.answer("✅ История очищена", show_alert=True)
            await call.delete()
        else:
            await call.answer("История уже пуста", show_alert=True)

    async def _first_time_setup(self, call):
        await call.edit(
            self.strings["first_time_setup"],
            reply_markup=[
                [{"text": "🚀 Начать настройку", "callback": self._setup_step1}],
                [{"text": "❌ Закрыть", "action": "close"}],
            ],
        )

    async def _setup_step1(self, call):
        await call.edit(
            self.strings["setup_step1"],
            reply_markup=[
                [{"text": "📝 Регистрация", "url": "https://api.mwshark.host/register"}],
                [{"text": "📋 Копировать ссылку", "copy": "https://api.mwshark.host/register"}],
                [{"text": "▶️ Далее", "callback": self._setup_step2}],
                [{"text": "❌ Закрыть", "action": "close"}],
            ],
        )

    async def _setup_step2(self, call):
        await call.edit(
            self.strings["setup_step2"],
            reply_markup=[
                [{"text": "🔑 Консоль токенов", "url": "https://api.mwshark.host/console/token"}],
                [{"text": "📋 Копировать ссылку", "copy": "https://api.mwshark.host/console/token"}],
                [{"text": "▶️ Далее", "callback": self._setup_step3}],
                [{"text": "◀️ Назад", "callback": self._setup_step1}],
                [{"text": "❌ Закрыть", "action": "close"}],
            ],
        )

    async def _setup_step3(self, call):
        await call.edit(
            self.strings["setup_step3"],
            reply_markup=[
                [{"text": "📋 Копировать команду", "copy": ".mwkey "}],
                [{"text": "▶️ Далее", "callback": self._setup_step4}],
                [{"text": "◀️ Назад", "callback": self._setup_step2}],
                [{"text": "❌ Закрыть", "action": "close"}],
            ],
        )

    async def _setup_step4(self, call):
        await call.edit(
            self.strings["setup_step4"],
            reply_markup=[
                [{"text": "📋 Копировать команду", "copy": ".mwtest "}],
                [{"text": "◀️ Назад", "callback": self._setup_step3}],
                [{"text": "❌ Закрыть", "action": "close"}],
            ],
        )

    async def _test_period_start(self, call):
        user_id = str(call.from_user.id)
        if user_id in self._test_period_requests:
            await call.edit(self.strings["test_period_already"])
            return

        await call.edit(
            self.strings["test_period_info"],
            reply_markup=[
                [{"text": "❌ Закрыть", "action": "close"}],
            ],
        )

    @loader.command()
    async def mwtest(self, message):
        """<username> - Получить тест-период (только 1 раз)"""
        args = utils.get_args_raw(message)
        user_id = str(message.from_id)

        if user_id in self._test_period_requests:
            await utils.answer(message, self.strings["test_period_already"])
            return

        if not args:
            await utils.answer(message, "❌ <b>Укажите username</b>\n\n💡 Использование: <code>.mwtest ваш_username</code>")
            return

        billing_username = args.strip()
        if not billing_username:
            await utils.answer(message, "❌ <b>Username не может быть пустым</b>")
            return

        try:
            user = await message.client.get_entity(message.from_id)
            username = f"@{user.username}" if user.username else "Нет username"
            user_id_int = message.from_id
            user_link = f"<a href='tg://user?id={user_id_int}'>{user.first_name}</a>"

            admin_message = (
                f"🎁 <b>Запрос на тест-период MW API</b>\n\n"
                f"👤 <b>Пользователь:</b> {user_link}\n"
                f"🆔 <b>ID:</b> <code>{user_id_int}</code>\n"
                f"📱 <b>Username TG:</b> {username}\n"
                f"👤 <b>Username в биллинге:</b> <code>{billing_username}</code>\n\n"
                f"💰 <b>Запрос:</b> 15₽ на баланс для тестирования"
            )

            try:
                await message.client.send_message("mwoffice", admin_message)

                self._test_period_requests[user_id] = {
                    "billing_username": billing_username,
                    "timestamp": message.date.timestamp()
                }
                self.db.set("MWAPI", "test_period_requests", self._test_period_requests)

                await utils.answer(message, self.strings["test_period_sent"])
            except Exception as e:
                error_str = str(e).lower()
                if "spamban" in error_str or "flood" in error_str or "peer" in error_str:
                    request_text = (
                        f"🎁 Запрос на тест-период MW API\n\n"
                        f"ID: {user_id_int}\n"
                        f"Username TG: {username}\n"
                        f"Username в биллинге: {billing_username}\n"
                        f"Запрос: 15₽ на баланс\n\n"
                        f"Примечание: У пользователя спамбан"
                    )

                    await self.inline.form(
                        self.strings["test_period_spam"].format(request_text),
                        reply_markup=[
                            [{"text": "📋 Копировать сообщение", "copy": request_text}],
                            [{"text": "👤 Связаться с админом", "url": "https://t.me/mwoffice"}],
                            [{"text": "❌ Закрыть", "action": "close"}],
                        ],
                        message=message,
                    )
                else:
                    await utils.answer(message, "❌ <b>Ошибка отправки запроса</b>\n\n💡 Попробуйте позже")
        except Exception:
            await utils.answer(message, "❌ <b>Произошла ошибка</b>\n\n💡 Попробуйте позже")

    def _translate_error(self, error_text):
        """Переводит китайские ошибки API на русский"""
        error_translations = {
            "未提供令牌": ("token_missing", "Токен не предоставлен"),
            "该令牌已过期": ("token_expired", "Токен истек"),
            "该令牌额度已用尽": ("insufficient_balance", "Квота токена исчерпана"),
            "余额不足": ("insufficient_balance", "Недостаточно средств на балансе"),
            "预扣费额度失败": ("insufficient_balance", "Недостаточно средств на балансе"),
            "无效的令牌": ("invalid_token", "Недействительный токен"),
            "请求过于频繁": ("rate_limit", "Слишком частые запросы"),
            "模型不存在": ("model_not_found", "Модель не существует"),
            "超出速率限制": ("rate_limit_exceeded", "Превышен лимит запросов"),
            "该令牌无权访问模型": ("model_access_denied", "Токен не имеет доступа к данной модели"),
            "Invalid content type. image_url is only supported by certain models": ("unsupported_image", "Данная модель не поддерживает изображения"),
        }

        try:
            error_data = json.loads(error_text)
            if "error" in error_data:
                if "code" in error_data["error"] and error_data["error"]["code"] == "insufficient_user_quota":
                    return "insufficient_balance", "Недостаточно средств на балансе"

                if "message" in error_data["error"]:
                    original_message = error_data["error"]["message"]
                    for chinese, (error_type, russian) in error_translations.items():
                        if chinese in original_message:
                            return error_type, russian
        except:
            pass

        return None, None

    async def _encode_image(self, photo):
        """Кодирует изображение в base64"""
        try:
            photo_bytes = await self.client.download_media(photo, bytes)
            return base64.b64encode(photo_bytes).decode('utf-8')
        except Exception:
            return None

    @loader.command()
    async def mw(self, message):
        """<запрос> [+ картинка] - Отправить запрос к ИИ"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()

        chat_id = str(utils.get_chat_id(message))

        if chat_id not in self._chat_history:
            self._chat_history[chat_id] = []

        has_image = False
        image_base64 = None

        if reply and reply.photo:
            has_image = True
            image_base64 = await self._encode_image(reply.photo)
            if not image_base64:
                await utils.answer(message, "❌ <b>Ошибка обработки изображения</b>")
                return

        if not args and not has_image:
            await utils.answer(message, self.strings["no_query"])
            return

        api_key = self.config["api_key"]
        if not api_key:
            await self.inline.form(
                self.strings["no_api_key"],
                reply_markup=[
                    [{"text": "🚀 Начать настройку", "callback": self._first_time_setup}],
                    [{"text": "📥 Скачать модуль", "copy": "dlm https://raw.githubusercontent.com/mwdevpy/mwmodules/refs/heads/main/modules/mwapi.py"}],
                    [{"text": "❌ Закрыть", "action": "close"}],
                ],
                message=message,
            )
            return

        await utils.answer(message, self.strings["processing"])

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                }

                if has_image:
                    content = []
                    if args:
                        content.append({"type": "text", "text": args})
                    content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    })
                    user_message = {"role": "user", "content": content}
                else:
                    user_message = {"role": "user", "content": args}

                self._chat_history[chat_id].append(user_message)
                self.db.set("MWAPI", "chat_history", self._chat_history)

                messages = self._chat_history[chat_id].copy()

                payload = {
                    "model": self.config["model"],
                    "messages": messages,
                    "max_tokens": self.config["max_tokens"],
                    "temperature": self.config["temperature"],
                }

                async with session.post(
                    self.config["api_url"],
                    headers=headers,
                    json=payload,
                ) as resp:
                    if resp.status != 200:
                        self._chat_history[chat_id].pop()
                        self.db.set("MWAPI", "chat_history", self._chat_history)

                        error_text = await resp.text()
                        error_type, translated_error = self._translate_error(error_text)

                        if translated_error:
                            error_msg = f"❌ <b>{translated_error}</b>\n\n"

                            if error_type in ["token_expired", "token_missing", "invalid_token"]:
                                error_msg += "🔑 <b>Проблема с токеном</b>\n\n"
                                error_msg += "💡 <b>Решение:</b>\n"
                                error_msg += "1. Получите новый токен\n"
                                error_msg += "2. Установите его: <code>.mwkey новый_токен</code>"

                                await self.inline.form(
                                    error_msg,
                                    reply_markup=[
                                        [{"text": "🔑 Получить токен", "url": "https://api.mwshark.host/console/token"}],
                                        [{"text": "📋 Копировать ссылку", "copy": "https://api.mwshark.host/console/token"}],
                                        [{"text": "📝 Копировать команду", "copy": ".mwkey "}],
                                        [{"text": "❌ Закрыть", "action": "close"}],
                                    ],
                                    message=message,
                                )
                            elif error_type == "insufficient_balance":
                                await self.inline.form(
                                    self.strings["quota_exceeded"],
                                    reply_markup=[
                                        [{"text": "🔑 Увеличить лимит", "url": "https://api.mwshark.host/console/token"}],
                                        [{"text": "📋 Копировать ссылку", "copy": "https://api.mwshark.host/console/token"}],
                                        [{"text": "💰 Пополнить баланс", "url": "https://t.me/mwoffice"}],
                                        [{"text": "🎁 Тест-период", "callback": self._test_period_start}],
                                        [{"text": "📝 Копировать команду", "copy": ".mwtest "}],
                                        [{"text": "❌ Закрыть", "action": "close"}],
                                    ],
                                    message=message,
                                )
                            elif error_type == "unsupported_image":
                                error_msg += "🖼 <b>Проблема с изображением в истории</b>\n\n"
                                error_msg += "💡 <b>Причина:</b>\n"
                                error_msg += "В истории диалога есть сообщение с изображением,\n"
                                error_msg += "а текущая модель не поддерживает изображения\n\n"
                                error_msg += "💡 <b>Решение:</b>\n"
                                error_msg += "1. Очистите историю командой <code>.mwclear</code>\n"
                                error_msg += "2. Или используйте модель с поддержкой изображений (gpt-4o)"

                                await self.inline.form(
                                    error_msg,
                                    reply_markup=[
                                        [{"text": "🗑 Очистить историю", "callback": self._clear_history_callback}],
                                        [{"text": "⚙️ Изменить модель", "callback": self._set_model}],
                                        [{"text": "📋 Копировать команду", "copy": ".mwclear"}],
                                        [{"text": "❌ Закрыть", "action": "close"}],
                                    ],
                                    message=message,
                                )
                            elif error_type == "model_access_denied":
                                error_msg += "🚫 <b>Нет доступа к модели</b>\n\n"
                                error_msg += "💡 <b>Решение:</b>\n"
                                error_msg += "1. Выберите другую модель (например, gpt-3.5-turbo)\n"
                                error_msg += "2. Или обратитесь к администратору для получения доступа"

                                await self.inline.form(
                                    error_msg,
                                    reply_markup=[
                                        [{"text": "⚙️ Изменить модель", "callback": self._set_model}],
                                        [{"text": "💬 Связаться с админом", "url": "https://t.me/mwoffice"}],
                                        [{"text": "❌ Закрыть", "action": "close"}],
                                    ],
                                    message=message,
                                )
                            else:
                                await utils.answer(message, error_msg.strip())
                        else:
                            await utils.answer(message, "❌ <b>Произошла неизвестная ошибка</b>\n\n💡 Попробуйте позже или обратитесь в поддержку")
                        return

                    data = await resp.json()
                    response_text = data["choices"][0]["message"]["content"]

                    self._chat_history[chat_id].append({
                        "role": "assistant",
                        "content": response_text
                    })
                    self.db.set("MWAPI", "chat_history", self._chat_history)

                    formatted_response = (
                        f"🤖 <b>Модель:</b> <code>{self.config['model']}</code>\n\n"
                        f"💬 <b>Вопрос:</b>\n{args if args else 'Изображение'}\n\n"
                        f"🎯 <b>Ответ:</b>\n{response_text}"
                    )

                    await self.inline.form(
                        formatted_response,
                        reply_markup=[
                            [
                                {"text": "🗑 Очистить", "callback": self._clear_history_callback},
                                {"text": "⚙️ Модели", "callback": self._set_model}
                            ],
                            [
                                {"text": "📥 Скачать данный модуль", "copy": "dlm https://raw.githubusercontent.com/mwdevpy/mwmodules/refs/heads/main/modules/mwapi.py"}
                            ],
                        ],
                        message=message,
                    )

        except aiohttp.ClientError as e:
            if chat_id in self._chat_history and self._chat_history[chat_id]:
                self._chat_history[chat_id].pop()
                self.db.set("MWAPI", "chat_history", self._chat_history)
            await utils.answer(message, f"❌ <b>Ошибка соединения</b>\n\n💡 Проверьте интернет-соединение\n\n🔍 <b>Детали:</b>\n<code>{str(e)}</code>")
        except KeyError as e:
            if chat_id in self._chat_history and self._chat_history[chat_id]:
                self._chat_history[chat_id].pop()
                self.db.set("MWAPI", "chat_history", self._chat_history)
            await utils.answer(message, f"❌ <b>Неверный формат ответа API</b>\n\n💡 Обратитесь в поддержку\n\n🔍 <b>Детали:</b>\n<code>{str(e)}</code>")
        except Exception as e:
            if chat_id in self._chat_history and self._chat_history[chat_id]:
                self._chat_history[chat_id].pop()
                self.db.set("MWAPI", "chat_history", self._chat_history)
            import traceback
            error_details = traceback.format_exc()
            await utils.answer(message, f"❌ <b>Произошла неизвестная ошибка</b>\n\n💡 Попробуйте позже\n\n🔍 <b>Детали:</b>\n<code>{error_details[:500]}</code>")
