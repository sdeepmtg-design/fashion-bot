import os
import logging
import time
from telegram.ext import Application, CommandHandler
import feedparser
from bs4 import BeautifulSoup

# Настройка логирования для Docker
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def check_environment():
    """Проверяем все environment variables"""
    logger.info("🔍 Проверяем environment variables...")
    
    # Получаем все переменные окружения
    all_env_vars = dict(os.environ)
    
    # Логируем все переменные (без значений для безопасности)
    logger.info(f"📋 Найдено переменных окружения: {len(all_env_vars)}")
    
    # Проверяем конкретно TELEGRAM_BOT_TOKEN
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if token:
        logger.info("✅ TELEGRAM_BOT_TOKEN: найден")
        # Показываем только первые 10 символов для безопасности
        logger.info(f"🔐 Токен (первые 10 символов): {token[:10]}...")
        return token
    else:
        logger.error("❌ TELEGRAM_BOT_TOKEN: не найден!")
        logger.info("💡 Доступные переменные окружения:")
        for key in sorted(all_env_vars.keys()):
            if any(word in key.lower() for word in ['token', 'key', 'secret', 'pass']):
                # Для чувствительных переменных показываем только наличие
                logger.info(f"   {key}: [скрыто]")
            else:
                # Для остальных показываем значение
                logger.info(f"   {key}: {all_env_vars[key]}")
        return None

class ArticleFetcher:
    def __init__(self):
        self.rss_feeds = [
            'https://www.vogue.com/feed/rss',
            'https://www.harpersbazaar.com/feed/rss', 
            'https://www.elle.com/feed/rss',
            'https://www.gq.com/feed/rss'
        ]
    
    def fetch_articles(self, num_articles=2):
        """Получает последние статьи о моде"""
        articles = []
        
        for feed_url in self.rss_feeds:
            try:
                logger.info(f"Загружаем статьи из: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:3]:
                    article = {
                        'title': entry.title,
                        'link': entry.link,
                        'summary': self._clean_summary(getattr(entry, 'summary', 'Нет описания')),
                        'source': getattr(feed.feed, 'title', 'Неизвестный источник')
                    }
                    articles.append(article)
                    
                    if len(articles) >= num_articles:
                        return articles
                        
            except Exception as e:
                logger.error(f"Ошибка загрузки {feed_url}: {e}")
        
        return articles[:num_articles]
    
    def _clean_summary(self, summary):
        """Очищает HTML из описания"""
        try:
            soup = BeautifulSoup(summary, 'html.parser')
            text = soup.get_text()
            return text[:300] + "..." if len(text) > 300 else text
        except:
            return summary[:300] + "..." if len(summary) > 300 else summary

async def start(update, context):
    """Обработчик команды /start"""
    welcome_text = """
👗 Добро пожаловать в Fashion Bot!

Я буду присылать вам самые свежие статьи из мира моды!

Команды:
/latest - Получить свежие статьи о моде
/help - Помощь
    """
    await update.message.reply_text(welcome_text)

async def latest(update, context):
    """Обработчик команды /latest - получает свежие статьи"""
    await update.message.reply_text("🔄 Ищу свежие статьи о моде...")
    
    fetcher = ArticleFetcher()
    articles = fetcher.fetch_articles(2)
    
    if not articles:
        await update.message.reply_text("❌ Статьи не найдены. Попробуйте позже.")
        return
    
    for article in articles:
        try:
            message_text = f"""
👗 **{article['title']}**

📖 {article['summary']}

📰 Источник: {article['source']}
🔗 [Читать статью]({article['link']})

#мода #стиль
            """
            
            await update.message.reply_text(
                message_text,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.error(f"Ошибка отправки статьи: {e}")
            await update.message.reply_text(f"📰 {article['title']}\n🔗 {article['link']}")

async def help(update, context):
    """Обработчик команды /help"""
    help_text = """
🤖 Fashion Bot - Помощь

Команды:
/start - Начать работу
/latest - Получить свежие статьи о моде
/help - Эта справка
    """
    await update.message.reply_text(help_text)

def main():
    """Основная функция запуска бота"""
    logger.info("🚀 Запускаем Fashion Bot...")
    
    # Проверяем environment variables
    token = check_environment()
    
    if not token:
        logger.error("❌ Не могу запустить бота без TELEGRAM_BOT_TOKEN")
        logger.info("🔄 Перезапуск через 10 секунд...")
        time.sleep(10)
        main()  # Рекурсивный перезапуск
        return
    
    try:
        # Создаем приложение бота
        app = Application.builder().token(token).build()
        
        # Регистрируем команды
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("latest", latest)) 
        app.add_handler(CommandHandler("help", help))
        
        logger.info("🤖 Бот запущен и готов к работе!")
        logger.info("📱 Напишите /start вашему боту в Telegram")
        
        # Запускаем бота
        app.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        logger.info("🔄 Перезапуск через 10 секунд...")
        time.sleep(10)
        main()  # Рекурсивный перезапуск

if __name__ == "__main__":
    main()
