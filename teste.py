from telegram import Bot

# Definir o token e o chat_id
TOKEN = '7233451695:AAF9gRHm2vL8kEAM2ZV-svSSf31yvVyRe8Y'
CHAT_ID = '5273027483'

# Criar o bot com o token fornecido
bot = Bot(token=TOKEN)

# Enviar a mensagem
bot.send_message(chat_id=CHAT_ID, text="Oi")

print("Mensagem enviada com sucesso!")