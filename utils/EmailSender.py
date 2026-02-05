import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime

def send_email(email, value, origin_wallet, destiny_wallet, id, type):
        SMTP_SERVER = 'smtp.gmail.com'
        SMTP_PORT = 587

        REMETENTE = 'cryptradinc@gmail.com'
        SENHA_REMETENTE = 'adsi lhgq ukvf ypxc'
        DESTINO = email

        if type == 'confirm-code':
                template = 'emailsTemplate/confirm_template.html'
        elif type == 'transaction':
                template = 'emailsTemplate/email_template.html'
        else:
                return

        with open(template, 'r', encoding='utf-8') as f:
                html_content = f.read()

        atual = datetime.datetime.now()
        dia = atual.strftime('%d/%m/%Y')
        hora = atual.strftime('%H:%M')

        if type == 'transaction':
                html_content = html_content.replace('__VDT__', value)
                html_content = html_content.replace('__CDO__', origin_wallet)
                html_content = html_content.replace('__CDD__', destiny_wallet)
                html_content = html_content.replace('__IDT__', id)
                html_content = html_content.replace('__DATA__', dia)
                html_content = html_content.replace('__HORA__', hora)
        else:
                html_content = html_content.replace('__CODE__', value)

        msg = MIMEMultipart('alternative')
        msg['From'] = REMETENTE
        msg['To'] = DESTINO
        if type == 'transaction':
                msg['Subject'] = 'Comprovante de Transferência - CryptaBank'
        else:
                msg['Subject'] = 'Código de Confirmação - CryptaBank'

        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(REMETENTE, SENHA_REMETENTE)
                server.send_message(msg)
        print ('Email enviado pivete')