# * import libraries
import telebot,json
from decouple import config
from telebot import types,formatting
from telebot.types import InputMediaPhoto

# * import agent :
from agent import AgentCRM

# Create Bot :
bot = telebot.TeleBot(token=config('HTTPTOKEN'))

# Basic Commands :
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,"Le bot est bien connecté 🚀")


@bot.message_handler(content_types=['text'])
def text_processing(message):
    print(message.content_type)


@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open('./audios/new_file.ogg', 'wb') as new_file:
        new_file.write(downloaded_file)

    # Init agent :
    myAgent = AgentCRM()

    myText = myAgent.whisper(path='./audios/new_file.ogg')
    print(myText)
    bot.reply_to(message, f'Tache demandée : "{myText}".', parse_mode='HTML')

    myDocs = myAgent.similarity(query=myText)

    for doc in myDocs:
        print(doc[1])

    myChat = myAgent.chat(docs=myDocs,input=myText)

    json.loads(myChat.replace("'", '"'))

    bot.reply_to(message, f"Tache effectuée ✅", parse_mode='HTML')


# Run TG Bot
bot.polling()