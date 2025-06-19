# meta developer: @mwmodules 

import asyncio
import aiohttp
import logging
import re
import random
from telethon.tl.functions.messages import ReportSpamRequest, ReportRequest
from telethon.errors import ChatIdInvalidError, MessageIdInvalidError, PeerIdInvalidError
from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class AutoReportMod(loader.Module):
    """Модуль для автоматической отправки жалоб"""
    
    strings = {
        "name": "AutoReport",
        "token_required": "🔑 Установите токен командой .setreporttoken <токен>\nПолучить токен: @mwapitokbot",
        "token_saved": "✅ Токен сохранен\n🤖 Автоотправка жалоб запущена",
        "auto_started": "🤖 Автоотправка жалоб запущена (интервал: 15 сек)",
        "task_created": "✅ Задача создана: {}",
        "invalid_link": "❌ Неверная ссылка на сообщение",
        "report_sent": "✅ Жалоба отправлена: {}\n📝 Задача: {}",
        "report_failed": "❌ Жалоба не отправлена: {}\n📝 Задача: {}",
        "api_success": "✅ API: Задача выполнена успешно\n🆔 ID: {}",
        "api_failed": "❌ API: Ошибка выполнения\n🆔 ID: {}\n📄 Причина: {}",
        "no_tasks": "📭 Нет доступных задач",
        "blocked": "🚫 Токен заблокирован",
        "error": "❌ Ошибка: {}",
        "status": "📊 Статус:\n🤖 Авто: Включен\n🔑 Токен: {}\n📈 Всего жалоб: {}\n✅ Успешных: {}\n❌ Ошибок: {}",
        "usage_snos": "Использование:\n.snos <ссылка> - добавить по ссылке\n.snos (ответ на сообщение) - добавить по ответу",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "api_url",
                "http://noderu2.mwhost.store:2000",
                "URL API сервера",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "token",
                "",
                "Токен доступа к API",
                validator=loader.validators.String()
            ),
        )
        self._auto_task = None
        self._stats = {"total": 0, "success": 0, "failed": 0}

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        if self.config["token"]:
            await self._start_auto()

    async def _make_request(self, method, endpoint, **kwargs):
        url = f"{self.config['api_url']}{endpoint}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, **kwargs) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    elif resp.status == 403:
                        return {"error": "blocked"}
                    else:
                        error_text = await resp.text()
                        return {"error": f"HTTP {resp.status}: {error_text}"}
        except Exception as e:
            return {"error": str(e)}

    def _parse_telegram_link(self, link):
        """Парсит ссылку на сообщение Telegram"""
        patterns = [
            r"https://t\.me/([a-zA-Z0-9_]+)/(\d+)",
            r"https://t\.me/c/(\d+)/(\d+)"
        ]
        
        for pattern in patterns:
            match = re.match(pattern, link.strip())
            if match:
                if pattern.startswith(r"https://t\.me/c/"):
                    chat_id = -int("100" + match.group(1))
                    message_id = int(match.group(2))
                else:
                    chat_id = match.group(1)
                    message_id = int(match.group(2))
                return chat_id, message_id
        return None, None

    async def _send_report(self, chat_id, message_id):
        """Отправляет жалобу на сообщение"""
        try:
            chat = await self._client.get_entity(chat_id)
            
            # Первый запрос с пустым option для получения доступных причин
            result = await self._client(ReportRequest(
                peer=chat,
                id=[message_id],
                option=b'',  # Пустой bytes вместо reason
                message=""
            ))
            
            # Если сервер вернул варианты выбора
            if hasattr(result, 'options') and result.options:
                # Выбираем случайную опцию из доступных
                selected_option = random.choice(result.options)
                
                # Второй запрос с выбранной опцией
                await self._client(ReportRequest(
                    peer=chat,
                    id=[message_id],
                    option=selected_option.option,
                    message=""
                ))
            
            return True, "Жалоба отправлена"
        except ChatIdInvalidError:
            return False, "Чат не найден"
        except MessageIdInvalidError:
            return False, "Сообщение не найдено"
        except PeerIdInvalidError:
            return False, "Неверный ID чата"
        except Exception as e:
            return False, f"Ошибка: {str(e)}"

    @loader.command()
    async def setreporttoken(self, message):
        """Установить токен API"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "Использование: .setreporttoken <токен>\nПолучить токен: @mwapitokbot")
            return
        
        self.config["token"] = args
        await utils.answer(message, self.strings["token_saved"])
        await self._start_auto()

    @loader.command()
    async def snos(self, message):
        """Добавить задачу сноса (ссылка или ответ на сообщение)"""
        if not self.config["token"]:
            await utils.answer(message, self.strings["token_required"])
            return

        args = utils.get_args_raw(message)
        link = None

        if message.is_reply and not args:
            reply = await message.get_reply_message()
            if reply.chat:
                if hasattr(reply.chat, 'username') and reply.chat.username:
                    link = f"https://t.me/{reply.chat.username}/{reply.id}"
                else:
                    chat_id = str(reply.chat.id)
                    if chat_id.startswith("-100"):
                        chat_id = chat_id[4:]
                    link = f"https://t.me/c/{chat_id}/{reply.id}"
        elif args:
            if args.startswith("https://t.me/"):
                link = args
            else:
                await utils.answer(message, self.strings["usage_snos"])
                return
        else:
            await utils.answer(message, self.strings["usage_snos"])
            return

        if not link:
            await utils.answer(message, self.strings["invalid_link"])
            return

        result = await self._make_request(
            "POST",
            f"/tasks/{self.config['token']}",
            json={"task_text": link}
        )

        if "error" in result:
            await utils.answer(message, self.strings["error"].format(result["error"]))
            return

        await utils.answer(message, self.strings["task_created"].format(result.get("task_id", "Неизвестно")))

    @loader.command()
    async def reportstats(self, message):
        """Показать статистику жалоб"""
        token_status = "Установлен" if self.config["token"] else "Не установлен"
        
        await utils.answer(
            message,
            self.strings["status"].format(
                token_status,
                self._stats["total"],
                self._stats["success"],
                self._stats["failed"]
            )
        )

    async def _process_single_task(self):
        """Обработка одной задачи"""
        result = await self._make_request("GET", f"/tasks/{self.config['token']}")
        
        if "error" in result:
            if result["error"] == "blocked":
                await self._client.send_message("me", self.strings["blocked"])
                return
            return

        if "message" in result:
            return

        task_id = result["task_id"]
        task_url = result["task_text"]
        
        chat_id, message_id = self._parse_telegram_link(task_url)
        
        if not chat_id or not message_id:
            api_result = await self._make_request(
                "POST",
                f"/result/{self.config['token']}/{task_id}",
                json={"success": False, "error_message": "Неверная ссылка на сообщение"}
            )
            self._stats["total"] += 1
            self._stats["failed"] += 1
            
            await self._client.send_message(
                "me", 
                self.strings["api_failed"].format(task_id, "Неверная ссылка на сообщение")
            )
            return

        success, error_msg = await self._send_report(chat_id, message_id)
        
        self._stats["total"] += 1
        
        if success:
            self._stats["success"] += 1
            api_result = await self._make_request(
                "POST",
                f"/result/{self.config['token']}/{task_id}",
                json={"success": True}
            )
            
            await self._client.send_message(
                "me",
                self.strings["report_sent"].format(error_msg, task_url)
            )
            
            if "error" not in api_result:
                await self._client.send_message(
                    "me",
                    self.strings["api_success"].format(task_id)
                )
        else:
            self._stats["failed"] += 1
            api_result = await self._make_request(
                "POST",
                f"/result/{self.config['token']}/{task_id}",
                json={"success": False, "error_message": error_msg}
            )
            
            await self._client.send_message(
                "me",
                self.strings["report_failed"].format(error_msg, task_url)
            )
            
            await self._client.send_message(
                "me",
                self.strings["api_failed"].format(task_id, error_msg)
            )

    async def _start_auto(self):
        if self._auto_task:
            return
        self._auto_task = asyncio.create_task(self._auto_worker())
        await self._client.send_message("me", self.strings["auto_started"])

    async def _stop_auto(self):
        if self._auto_task:
            self._auto_task.cancel()
            self._auto_task = None

    async def _auto_worker(self):
        while True:
            try:
                if not self.config["token"]:
                    await asyncio.sleep(15)
                    continue

                await self._process_single_task()
                await asyncio.sleep(15)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Ошибка в автоворкере: {e}")
                await asyncio.sleep(60)

    async def on_unload(self):
        if self._auto_task:
            self._auto_task.cancel()
