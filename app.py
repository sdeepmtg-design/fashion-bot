import os
import logging
from telegram.ext import Application, CommandHandler
import feedparser
from datetime import datetime
from bs4 import BeautifulSoup

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

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
                print(f"📡 Загружаем статьи из: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:3]:  # Берем первые 3 статьи
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
                print(f"❌ Ошибка загрузки {feed_url}: {e}")
        
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
            print(f"Ошибка отправки статьи: {e}")
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
    # Получаем токен из environment variables
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ ОШИБКА: TELEGRAM_BOT_TOKEN не установлен!")
        print("💡 Добавьте TELEGRAM_BOT_TOKEN в Environment Variables на Render")
        return
    
    print("✅ TELEGRAM_BOT_TOKEN найден")
    print("🚀 Запускаем Fashion Bot...")
    
    # Создаем приложение бота
    app = Application.builder().token(token).build()
    
    # Регистрируем команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("latest", latest)) 
    app.add_handler(CommandHandler("help", help))
    
    print("🤖 Бот запущен и готов к работе!")
    print("📱 Напишите /start вашему боту в Telegram")
    print("⏹️  Для остановки нажмите Ctrl+C")
    
    # Запускаем бота
    app.run_polling()

if __name__ == "__main__":
    main()
