import scrapy
import sqlite3
import telebot
import locale


chaveapi = '2049395230:AAH0FVtI6AXSGjZbIJ7RFE_E8qt4YZzCDbw'

bot = telebot.TeleBot(chaveapi)

class KabumSpider(scrapy.Spider):
    name = 'kabum'
    start_urls = ['https://servicespub.prod.api.aws.grupokabum.com.br/catalog/v1/products-by-category/hardware/placa-de-video-vga?page_number=1&page_size=100&sort=-price&include=gift']

    def parse(self, response):
        json_response = response.json()
        json_data = json_response['data']
        gpu_list = []
        for i in json_data:
            if i['attributes']['available']:
                gpus= ['6800','6700','6600','vii','5700','5600','vega64','vega56','580'
                    ,'570','480','470','3090','3080','3070','3060','2080','2070','2060','1660','1080','1070','1060','1050']
                link = f"https://www.kabum.com.br/produto/{i['id']}"
                nome = i['attributes']['title'].replace(',', '')
                if any(gpu.lower() in nome.lower() for gpu in gpus):
                    preco = i['attributes']['price']
                    preco_desconto = i['attributes']['price_with_discount']
                    imagem = i['attributes']['photos']['m'][0]
                    if i['attributes']['is_marketplace']:
                        vendido = i['attributes']['marketplace']['seller_name']
                    else:
                        vendido = 'Kabum'
                    stock = i['attributes']['stock']
                    gpu = [nome,imagem,preco,preco_desconto,vendido,stock,link]
                    gpu_list.append(gpu)

        self.db(gpu_list)


    def db(self,gpu_list):

        conn = sqlite3.connect('gpus.db')
        # definindo um cursor
        cursor = conn.cursor()

        # criando a tabela (schema)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS gpus(
                nome TEXT NOT NULL,
                imagem TEXT NOT NULL,
                preco REAL NOT NULL,
                preco_desconto REAL NOT NULL,
                vendido TEXT NOT NULL,
                stock INT NOT NULL,
                link TEXT NOT NULL
        );
        """)

        for data in gpu_list:
            produto = self.searchdata(data[0])
            if not produto:
                cursor.execute("""
                            INSERT INTO gpus (nome, imagem, preco, preco_desconto, vendido, stock, link)
                            VALUES (?,?,?,?,?,?,?)
                            """, data)
                conn.commit()
                self.promocao(data[0], produto['preco'], precopix = False)
            elif produto['preco'] > data[2] :
                cursor.execute(f"""UPDATE gpus SET preco='{data[2]}'
                         WHERE nome='{data[0]}'""")
                conn.commit()
                self.promocao(data[0], produto['preco'], precopix = False)
                conn.close()
            elif produto['preco_desconto'] > data[3]:
                cursor.execute(f"""UPDATE gpus SET preco_desconto='{data[3]}'
                             WHERE nome='{data[0]}'""")
                conn.commit()
                self.promocao(data[0], produto['preco_desconto'], precopix = True)
                conn.close()


    def searchdata(self,term_search):

        conn = sqlite3.connect('gpus.db')
        # definindo um cursor
        cursor = conn.cursor()

        sql = f"SELECT nome, imagem, preco, preco_desconto, vendido, stock, link FROM gpus WHERE nome == '{term_search}'"
        #
        for row in cursor.execute(sql):
            produto = {
                'nome': row[0],
                'imagem': row[1],
                'preco': row[2],
                'preco_desconto': row[3],
                'vendido': row[4],
                'stock': row[5],
                'link': row[6]
            }
            if produto:
                return produto
            else:
                return None

    def promocao(self,nome, precoantigo, precopix):
        produto = self.searchdata(nome)
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        if not precopix:
            bot.send_message('-1001524638801', text=f"🤩 PROMOÇÃO 🤩\n\n"
                                               f"📌 {produto['nome']}\n\n"
                                               f"💸 Preço Antigo {locale.currency(precoantigo, grouping=True, symbol=True)}\n\n"
                                               f"😁 Preço Atual {locale.currency(produto['preco'], grouping=True, symbol=True)}\n\n"
                                               f"💸 Preço Pix {locale.currency(produto['preco_desconto'], grouping=True, symbol=True)}\n\n"
                                               f"🛒 Vendido Por: {produto['vendido']}\n\n"
                                               f"🛒 Estoque Disponível: {produto['stock']}\n\n"
                                               f"👉 {produto['link']}\n")
        else:
            bot.send_message('-1001524638801', text=f"🤩 PROMOÇÃO 🤩\n\n"
                                               f"📌 {produto['nome']}\n\n"
                                               f"💸 Preço {locale.currency(produto['preco'], grouping=True, symbol=True)}\n\n"
                                               f"💸 Preço Pix Antigo {locale.currency(precoantigo, grouping=True, symbol=True)}\n\n"
                                               f"😁 Preço Pix Atual {locale.currency(produto['preco_desconto'], grouping=True, symbol=True)}\n\n"
                                               f"🛒 Vendido Por: {produto['vendido']}\n\n"
                                               f"🛒 Estoque Disponível: {produto['stock']}\n\n"
                                               f"👉 {produto['link']}\n")
