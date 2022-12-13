from fileinput import filename
from os import getenv
from socket import timeout
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import (
    ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
)
import os, unidecode, subprocess, json
from random import choice
from configparser import ConfigParser
import pyromod.listen


#

text_start = """
<strong>             ஜ🌹  ʙɪʙʟɪᴏᴛᴇᴄᴀ ᴅᴇ ʟɪᴠʀᴏs sᴀ́ғɪᴄᴏs  🌹ஜ</strong>


➲<strong>🌥 ʟɪsᴛᴀʀ ʟɪᴠʀᴏs ᴘᴏʀ:
                               
        •📂 /cat - ᴄᴀᴛᴇɢᴏʀɪᴀs

        •👩‍💼 AUT - ᴀᴜᴛᴏʀᴇs (ᴇᴍ ᴅᴇsᴇɴᴠᴏʟᴠɪᴍᴇɴᴛᴏ)</strong>  



<i>Você também pode:</i>
<i>🔎 /pesquisar - Para pesquisar um livro pelo nome, 
digite "/pesquisar + nome do livro" a qualquer momento.</i>
<i>📨 /enviar - Envie um livro da biblioteca ou qualquer 
outro arquivo externo para seu kindle.</i>


"""

ListOf = 'Aventura', 'Biografia', 'Drama', 'Fantasia', 'FiccaoCientifica', 'Romance'

list_callbacks = ['PDF', 'EPUB', 'MOBI']

emojis = {
    f'{ListOf[0]}': '🎈',
    f'{ListOf[1]}':'✒️',
    f'{ListOf[2]}':'☂️',
    f'{ListOf[3]}':'⚔️',
    f'{ListOf[4]}':'🛰️',
    f'{ListOf[5]}':'❤️‍🔥'
}

chat_to_replace = {
    '.epub': '',
    '.pdf': '',
    '.mobi': '',
    '.txt': '',
    "(zlib.org)": '',
    "(z-lib.org)": '',
    "-": '',
    "(": '',
    ")": '',
    ".tx": '',
    '.pd': '',
    '.ep': '',
    'by': '',
    '{BC}': ''
}

list_supported =  ['.doc', '.docx', '.rtf', '.htm', '.html', '.txt', '.zip', '.mobi', '.epub', '.pdf', '.jpg','.gif','.bmp', '.png', 'pdf', 'doc',
'docx', 'rtf', 'htm', 'html', 'txt', 'zip', 'mobi', 'epub', 'jpg', 'gif', 'bmp', 'png']



# FUNCTIONS

def gerador_pag(callback_data, titulos): 
    if callback_data in ListOf:
        atual = 1
    else:
        for letter in callback_data:
            if letter.isdigit():
                atual = int(letter)
                
    limite1 = titulos.find(f'THIS IS A LINE{atual-1}')
    limite2 = titulos.find(f'THIS IS A LINE{atual}')
    texto = titulos[limite1:limite2]
    pages = {
        callback_data: {
        f'pag{atual-1}': InlineKeyboardButton('Página Anterior', callback_data=f'pag{atual-1}'),
        f'pag{atual+1}': InlineKeyboardButton('Proxima Página', callback_data=f'pag{atual+1}'),
        'texto': texto,
        }
    }
    return pages

async def send_files(id, mensagem, format):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    for root, dirs, files in os.walk(dir_path):
        for file in files:
                file = str(file)
                filet = unidecode.unidecode(file)
                if file.endswith(format):
                    if mensagem.lower().strip() in filet.lower():
                        await app.send_message(id, "☁️  Estamos enviando o arquivo para você, por favor, aguarde...")
                        duck = open(f"{root}/{file}", "rb")
                        await app.send_document(id, duck, file_name=file)
                        duck.close()


def add_request(chatId, newRequest):
    with open(f'request_per_id/{chatId}.txt', 'w+') as file:
        file.write(f'{newRequest}')

def send_email_local(email, id, nome):
    a = f'sendEmail.py {email} {id} None "{nome}"'
    a = a.replace('\n', '')
    subprocess.Popen(r'python3 %s' % (a), shell=True)

def send_email_pessoal(email, id, nome):
    a = f'sendEmail.py {email} {id} pessoal "{nome}"'
    a = a.replace('\n', '')
    subprocess.Popen(r'python3 %s' % (a), shell=True)

def get_img_url(title):
    with open('picUrls.json') as json_file:
        url = json.load(json_file)
    return url[title]

async def add_email(id):

    config = ConfigParser()
    config.read('emails.ini')
    
    idList = list(config['emails'])
    
    if str(id) in idList:
        email = config['emails'][f'{id}']
        await app.send_message(id, f'🤖 Você só pode registrar um e-mail no sistema. \nSeu email cadastrado é <strong>{email}.</strong>')
    else:
        while True:
            emailN = await app.ask(id, 'Digite seu email Kindle: ')
            if '@kindle.com' in emailN.text:
                confirm = await app.ask(id, f'Você tem certeza que deseja cadastrar o email {emailN.text}? \n<strong>Digite S para Sim / N para não/ C para cancelar o cadastro.\nobs: você poderá cadastrar o email apenas uma vez.</strong>')
                if confirm.text.lower() == 's':
                    config.set('emails', f'{id}', f'{emailN.text}')
                    with open('emails.ini', 'w') as newini:
                        config.write(newini)
                    await app.send_message(id, '🤖 Seu email foi cadastrado, agora você pode enviar arquivos da biblioteca <strong>sem precisar registrá-lo novamente</strong> :)\nCaso ainda não tenha adicionado o e-mail da biblioteca na lista de e-mails aprovados, o endereço é: bibliotecabotlesb@gmail.com\nÉ necessário adicionar o email do bot na lista de emails aprovados, caso contrário não será possível recebê-lo em seu kindle.')
                    break
                elif confirm.text.lower() == 'n':
                    continue
                elif confirm.text.lower() == 'c':
                    await app.send_message(
                    id,
                    'Cadastro cancelado.'
                )
                    break
            else:
                await app.send_message(
                    id,
                    'Verifique o email e tente novamente. Note que email deve conter o provedor @kindle.com'
                )
                break




#

load_dotenv('cred.env')



app = Client(
    'Biblioteca_Safica',
    api_id = getenv('api_id'),
    api_hash = getenv('api_hash'),
    bot_token= getenv('CHAVE_API')
)


@app.on_callback_query()
async def callback(client, callback_query):  
    if callback_query.data in ListOf:
        categoria = callback_query.data

        with open(f"./Livros_PDF/lista{categoria}.txt", 'r', encoding='utf8') as file: #lista txt com livros
            line = file.readlines()
        with open(f"./Livros_PDF/lista{categoria}.txt", 'r', encoding='utf8') as file: #lista txt com livros
            titulos = file.read()
      



        await app.send_message(
            callback_query.from_user.id, 
            f'{emojis[callback_query.data]}LIVROS DISPONÍVEIS NA CATEGORIA {categoria.upper()}:</strong>'
            )


        if len(line) > 50:
            

            gerador = gerador_pag(callback_query.data, titulos)
            
            page = gerador[callback_query.data]
            texto = page['texto']

            if f'THIS IS A LINE0' in page['texto']:
                texto = texto.replace(f'THIS IS A LINE0', '')

            await app.send_message(
                callback_query.from_user.id,
                texto,
                reply_markup= InlineKeyboardMarkup (
                    [
                        [page['pag0'], page['pag2']
                    ]
                    ]
                )
            )

            request_cat = open(f'request_per_id/{callback_query.from_user.id}_cat.txt', 'w+')
            request_cat.write(callback_query.data)
            request_cat.close()
                
        else:
            await app.send_message(
                callback_query.from_user.id,
                titulos)


    elif callback_query.data in list_callbacks:
        with open(f'request_per_id/{callback_query.from_user.id}.txt', 'r+') as fileId:
            mensagem = fileId.readline()
        formato = f'.{callback_query.data.lower()}'
        await send_files(callback_query.from_user.id, mensagem, formato)

    elif callback_query.data == 'kindle':

        config = ConfigParser()
        config.read('emails.ini')
    
        idList = list(config['emails'])

        if str(callback_query.from_user.id) in idList:
            email = config['emails'][f'{callback_query.from_user.id}']

            await app.send_message(
                callback_query.from_user.id, 
            "☁️  Estou enviando o arquivo para seu kindle, por favor, aguarde..."
            )

            send_email_local(email=email, 
            id = callback_query.from_user.id,
            nome = 'nome'
            )

            await app.send_message(
                callback_query.from_user.id, 
                '🤖 Seu arquivo será entregue em poucos minutos, não é necessário reenviá-lo!'
                )

        else:

            await app.send_message(
                callback_query.from_user.id, 
                '🤖 Você precisa cadastrar seu email @kindle.com primeiro!'
                )
    
    elif callback_query.data == 'cadastrar':
        await add_email(callback_query.from_user.id)
    
    elif 'pag' in callback_query.data:
        with open(f'request_per_id/{callback_query.from_user.id}_cat.txt', 'r') as file:
            request_cat = file.read()
        with open(f"./Livros_PDF/lista{request_cat}.txt", 'r', encoding='utf8') as file:
            titulos = file.read()

        gerador = gerador_pag(callback_query.data, titulos)
        page = gerador[callback_query.data]
        texto = page['texto']

        for letter in callback_query.data:
            if letter.isdigit():
                atual = int(letter)
        
        try:
            if f'THIS IS A LINE' in page['texto']:
                texto = texto.replace(f'THIS IS A LINE', '')
            for letter in texto[0:1]:
                if letter.isdigit():
                    texto = texto.replace(letter, '')

            await callback_query.edit_message_text(
                texto,
                reply_markup = InlineKeyboardMarkup(
                    [
                        [
                            page[f'pag{atual-1}'], page[f'pag{atual +1}']
                        ]
                    ]
                )
            )
        except:
            None
                
                


@app.on_message(filters.command('start'))
async def start(client, message):
    my_list = [
    'https://static1.srcdn.com/wordpress/wp-content/uploads/2020/07/Marceline-and-Bubblegum-Lesbian-Pride-Flag.jpg',
    'https://www.thefandomentals.com/wp-content/uploads/2016/12/bubbline-cover2.png',
    'https://static1-br.millenium.gg/articles/4/67/24/@/99995-e4gjxrvvoamgz07-article_cover_bd-1.jpg',
    'https://i.pinimg.com/originals/0e/3f/ed/0e3fed55a757ff80c5d7ea458cebe99f.jpg',
    'https://static1-br.millenium.gg/articles/3/74/53/@/104896-arte-do-conto-ascenda-comigo-foto-riot-gamesreproducao-article_m-1.png']
    c = choice(my_list)
    await app.send_photo(message.chat.id, c, caption=text_start)


@app.on_message(filters.command('cat'))
async def cat(client, message):
    cats = InlineKeyboardMarkup([
            
            [InlineKeyboardButton('Aventura', callback_data='Aventura')],
            [InlineKeyboardButton('Biografia', callback_data='Biografia')],
            [InlineKeyboardButton('Drama', callback_data='Drama')],
            [InlineKeyboardButton('Fantasia', callback_data='Fantasia')],
            [InlineKeyboardButton('Ficção Científica', callback_data='FiccaoCientifica')],
            [InlineKeyboardButton('Romance', callback_data='Romance')]
    ])
    await app.send_message(
        message.chat.id,
        '<strong>           SELECIONE UMA OPÇÃO: </strong>',
        reply_markup=cats
    )

@app.on_message(filters.command('enviar'))
async def enviar(client, message):
    nome = message.chat.first_name
    if message.text == '/enviar':
        await app.send_message(message.chat.id, f"""💻  Olá <strong>{nome}</strong>, 
Há duas opções de envio para o kindle:
- Interno (arquivos dentro da biblioteca)
- Externos (seus próprios arquivos)

Para enviar um arquivo da biblioteca, você pode pesquisá-lo, digitando /pesquisar + nome do livro ou clicar em "ENVIAR PARA KINDLE" ao selecionar um dos arquivos dentro da biblioteca.

Se você deseja enviar um arquivo externo, digite </strong>/enviar meu arquivo</strong> e siga as instruções.

❗ E-mail do bot para adicionar na lista de e-mails aprovados: <strong>bibliotecabotlesb@gmail.com</strong>""")
        
    if message.text == '/enviar meu arquivo':


        button = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('Cadastrar email Kindle', callback_data='cadastrar')]
            ]
        )
        await app.send_message(
            message.chat.id, 
            f'''Para utilizar os serviços de envio, você precisa registrar seu endereço de email kindle no sistema. <strong>Caso ainda não tenha registrado, clique no botão abaixo para começar o cadastro</strong>. Senão, ignore esta mensagem.''',
            reply_markup=button)
        
        await app.send_message(
            message.chat.id,
            f'''Dicas <strong>necessárias</strong> para anexos de documentos pessoais:

❗ O Serviço de documentos pessoais do Kindle pode converter e entregar os seguintes tipos de documentos:
<strong>- Microsoft Word (.doc, .docx) 
- Formato Rich Text (.rtf) 
- HTML (.htm, .html) 
- Documentos de texto (.txt) 
- Documentos arquivados (zip, x-zip) e documentos compactados
- MOBI (.azw, .mobi) (não suporta os recursos mais novos do Kindle para documentos)
- EPUB (.epub)
- Formato Adobe PDF (.pdf)
- Imagens que são do tipo JPEGs (.jpg), GIFs (.gif), Bitmaps (.bmp), e imagens PNG (.png).</strong>

❗ O tamanho do arquivo de cada documento pessoal anexado deve ser inferior a 50 MB/50.000 KB (antes da compactação em um arquivo ZIP).

❗ Por ora, só é possível fazer envio de um arquivo por vez, portanto para cada arquivo a ser enviado é necessário digitar o comando /enviar meu arquivo.''')
        
        try:
            config = ConfigParser()
            config.read('emails.ini')
        
            idList = list(config['emails'])

            if str(message.chat.id) in idList:
                emailUser = config['emails'][f'{message.chat.id}']

            document = await app.ask(
                message.chat.id,
                'Quando estiver pronta, pode me enviar seu arquivo.',
                timeout = 60
            )

            document_type = document.document.file_name[-5:len(document.document.file_name)]
            document_type = document_type.partition((".")[0])
            print(document_type[2])

            if document_type[2] not in list_supported:
                await app.send_message(
                    message.chat.id,
                    'Tipo de arquivo não suportado. O envio foi cancelado.'
                )
            else:
                with open(f'request_per_id/{message.chat.id}_pessoal.txt', 'w+') as nome:
                    nome.write(document.document.file_name)
                await app.download_media(document, file_name=f'request_per_id/{document.document.file_name}')
                
                await app.send_message(message.chat.id,
                'O arquivo foi recebido.')

                await app.send_message(
                    message.chat.id, 
                "☁️  Estou enviando o arquivo para seu kindle, por favor, aguarde..."
                )

                send_email_pessoal(
                    email = emailUser,
                    id = message.chat.id,
                    nome = document.document.file_name
                )

                await app.send_message(
                    message.chat.id, 
                    '🤖 Seu arquivo será entregue em poucos minutos, não é necessário reenviá-lo!'
                    )



        except:
            await app.send_message(
                message.chat.id,
                'O envio de arquivo foi cancelado. Para tentar novamente, digite /enviar meu arquivo.')


@app.on_message()
async def main(client, message):
    if '/' in message.text:
        if "/pesquisar" in message.text and len(message.text) < 17:
            if "ash" in message.text:
                await app.send_message(
                    message.chat.id,
                    "Digite /pesquisar ash livro."
                )
            else:
                await app.send_message(message.chat.id, 'Livro não encontrado. Tente novamente utilizando o nome da autora, separado por um "-"\nExemplo: *Carol - Patricia Highsmith*')
        else:
            try:
                ######################################################################

                mensagem = message.text
                if '/pesquisar' not in mensagem:
                    for letter in mensagem:
                        if letter.isupper():
                            mensagem = mensagem.replace(f"{letter}", f" {letter}")
                        if letter.isdigit():
                            mensagem = mensagem.replace(f"{letter}", f" {letter}")
                else:
                    mensagem = mensagem.replace('/pesquisar', '')

                

                mensagem = unidecode.unidecode(mensagem)
                mensagem = mensagem.replace('/', '')
                mensagem = mensagem.replace('  ', ' ')
                mensagem = mensagem.strip()
                
                
                ######################################################################

                add_request(message.chat.id, mensagem)

                dir_path = os.path.dirname(os.path.realpath(__file__))
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        file = str(file)
                        filet = unidecode.unidecode(file)

                        if file.endswith(".txt"):
                            if mensagem.lower() in filet.lower():
                                with open(f"./Sinopse/{file}", "r", encoding='utf8') as sinopse:
                                    sinopse = sinopse.read()
                                
                                if "-" in file:
                                    until = file.find("-", 1, -1)
                                    autora = file[until:-1]
                                elif "by" in file:
                                    until = file.find("by", 7, -1)
                                    autora = file[until:-1]
                                elif "-" not in file and "by" not in file:
                                    until = len(file)
                                    autora = 'Undefined'
                                
                                for key, value in chat_to_replace.items():
                                    file = file.replace(key, value)
                                    autora = autora.replace(key, value)
                            
                                specific_filename = filet.replace('.txt', '')
                                await app.send_photo(message.chat.id, get_img_url(specific_filename))

                                await app.send_message(message.chat.id, f'''🌈  <i>Nome do livro:  <strong>{file[0:until].strip()}</strong>  </i>

👩‍💼  <i>Autora:  <strong>{autora.strip()}</strong></i>


📃  <strong>Sinopse</strong>: 


{sinopse}
'''
)
                                buttons = InlineKeyboardMarkup (
                                    [
                                        [
                                            InlineKeyboardButton('PDF', callback_data='PDF')
                                        ],
                                        [
                                            InlineKeyboardButton('MOBI', callback_data='MOBI')
                                        ],
                                        [
                                            InlineKeyboardButton('EPUB', callback_data='EPUB')
                                        ],
                                        [
                                            InlineKeyboardButton('Enviar para o Kindle', callback_data='kindle'),
                                
                                            InlineKeyboardButton('Cadastrar email Kindle', callback_data='cadastrar')
                                        ]
                                    ]
                                )

                                await app.send_message(message.chat.id,
                                '<strong>SELECIONE UMA OPÇÃO:</strong>',
                                reply_markup=buttons)

                            
            except:
                await app.send_message(
                    message.chat.id,
                    '🤖 Livro não encontrado.'
                )



print('O BOT FOI INICIADO!')


app.run()
