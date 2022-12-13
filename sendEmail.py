from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib, ssl, typer, os, unidecode


host = "smtp.gmail.com"
port = "587"
login = ""
senha = ""

def search_file(filename):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    for root, dirs, files in os.walk(dir_path):
        for file in files:
                file = str(file)
                filet = unidecode.unidecode(file)
                if file.endswith('.epub'):
                    if filename.lower().strip() in filet.lower():
                        return f'{root}/{file}'

def send_email(email: str, id: str, tipo: str, nome: str):

    if tipo == 'None':
        with open(f'request_per_id/{id}.txt', 'r+') as filenam:
            filenam = filenam.readline()
            filenam = search_file(filenam)
            nome = filenam
        
    elif tipo == 'pessoal':
        with open(f'request_per_id/{id}_pessoal.txt', 'r+') as filerequest:
            filerequest = filerequest.readline()
            filenam = f"./request_per_id/{filerequest}"
        
    

    server = smtplib.SMTP(host, port)
    server.ehlo()
    context= ssl.create_default_context()
    server.starttls(context=context)

    server.login(login, senha)

    email_msg = MIMEMultipart()
    email_msg["From"] = login
    email_msg["To"] = email
    email_msg["Subject"] = ""
    cam = open(filenam, "rb")
    epub = MIMEApplication(
        cam.read())
    epub.add_header('Content-Disposition', 'attachment', filename=nome)
    email_msg.attach(epub)

    server.sendmail(email_msg['From'], email_msg['To'], email_msg.as_string())
    server.quit()
    cam.close()

    if tipo == 'pessoal':
        os.remove(filenam)




if __name__ == "__main__":
    typer.run(send_email)
