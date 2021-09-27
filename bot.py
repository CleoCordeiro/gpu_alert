import sqlite3
import telebot
import locale
conn = sqlite3.connect('gpus.db', check_same_thread=False)
# definindo um cursor
cursor = conn.cursor()

chaveapi = '2049395230:AAH0FVtI6AXSGjZbIJ7RFE_E8qt4YZzCDbw'


bot = telebot.TeleBot(chaveapi)


def searchdata(term_search):
    data = []
    sql = f"SELECT nome, imagem, preco, preco_desconto, vendido, link FROM gpus WHERE nome LIKE '%{term_search}%'"
    #
    for row in cursor.execute(sql):
        produto = {
            'nome': row[0],
            'imagem': row[1],
            'preco': row[2],
            'preco_desconto': row[3],
            'vendido': row[4],
            'link': row[5]
        }
        data.append(produto)
    if data:
        return data
    else:
        return None





@bot.message_handler(commands=['preco'])
def respose(mensagem):
    search = mensagem.text.split('preco ')
    if len(search) > 1:
        data = searchdata(search[1])
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        for row in data:
            print(mensagem.chat.id)
            bot.send_message(mensagem.chat.id, text=f"📌 {row['nome']}\n\n"
                                                    f"😁 Preço {locale.currency(row['preco'], grouping=True, symbol=True)}\n\n"
                                                    f"💸 Preço Pix {locale.currency(row['preco_desconto'], grouping=True, symbol=True)}\n\n"
                                                    f"🛒 Vendido Por: {row['vendido']}\n"
                                                    f"👉 {row['link']}\n")

    else:
        bot.send_message(mensagem.chat.id, text=f'Produto Não Encontrado')



@bot.message_handler(commands=['start','help'])
def respose(mensagem):
    menu = """
Bem Vindo ao bot de buscar preços de gpus
    Menu:
        Para pesquisar por gpus digite
        /preco - Busca gpus pelo nome
        exemplo: /preco rtx 3070"""
    bot.reply_to(mensagem,menu)

bot.polling()
