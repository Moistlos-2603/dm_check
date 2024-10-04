# import schedule 
import time
import schedule

import imaplib
import email

from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

import getpass

orders = []
passwort = getpass.getpass()
print("From Mail")
from_mail = getpass.getuser
print("To Mail")
to_mail = getpass.getuser


def get_latest_mail_body():
    mail = imaplib.IMAP4_SSL('imap.web.de')
    mail.login(from_mail, passwort)
    mail.list()
    mail.select("inbox") # connect to inbox.
    result, data = mail.search(None, "ALL")

    ids = data[0]
    id_list = ids.split()
    result, data = mail.fetch(id_list[-1], "(RFC822)") 
    raw_email = data[0][1]
    email_massage = email.message_from_string(raw_email.decode("utf-8"))

    mail_body = get_mail_body(email_massage)
    return mail_body 


def get_mail_body(email:str)-> str:
    for part in email.walk():
        if part.get_content_type() == "text/plain":
            charset = part.get_content_charset()
            body = part.get_payload(decode=True)
        
            obj = body.decode("ascii")
            obj = obj.replace("\r\n" , ", ")
            obj = obj[:len(obj)-1].replace('', '')
            return obj


def get_new_f_and_a_num():
    is_in = False
    mail_body = get_latest_mail_body()
    f_num = mail_body.split("Filialnummer:")[1][:5].strip()
    a_num = mail_body.split("Auftrag:")[1][:7].strip()
    
    for order in orders:
        if f_num == order[0]:
            is_in = True

    if is_in == False:
        orders.append([f_num, a_num, "nicht_da"])





def check_order_state(f_num:str, a_num:str)->str:
    chrome_options = Options()
    chrome_options.add_argument("--disable-search-engine-choice-screen")
    chrome_options.add_argument('--headless=new')
    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://www.fotoparadies.de/service/auftragsstatus.html#/?orderid="+a_num+"&locationid="+ f_num)
    while(find_elemten("/html/body/cw-order-tracking-app/div/div", driver)):
        print(1)
    time.sleep(5)

    if(find_elemten("/html/body/cw-order-tracking-app/div/div", driver) != False):
        print("AAAAAAAAAA")
        return "nicht_da"
    

    img_link = find_elemten("/html/body/cw-order-tracking-app/cw-order-tracking/div/div/cw-accordion/div/div/cw-tile/cw-order-timeline/div[2]/div[1]/div/img", driver).get_attribute("src")
    if "_active" in img_link and img_link != "":
        return "erhalten"
    
    img_link = find_elemten("/html/body/cw-order-tracking-app/cw-order-tracking/div/div/cw-accordion/div/div/cw-tile/cw-order-timeline/div[2]/div[2]/div/img", driver).get_attribute("src")
    if "_active" in img_link and img_link != "":
        return "gefertig"
                            
    img_link = find_elemten("/html/body/cw-order-tracking-app/cw-order-tracking/div/div/cw-accordion/div/div/cw-tile/cw-order-timeline/div[2]/div[3]/div/img", driver).get_attribute("src")
    if "_active" in img_link and img_link != "":
        return "wird_geliefert"

    
    img_link = find_elemten("/html/body/cw-order-tracking-app/cw-order-tracking/div/div/cw-accordion/div/div/cw-tile/cw-order-timeline/div[2]/div[4]/div/img", driver).get_attribute("src")
    if "_active" in img_link and img_link != "":
        return "abholbereit"
    

def find_elemten(x_path:str,driver:webdriver.Chrome):
    try:
        element = driver.find_element(By.XPATH, x_path)
    except NoSuchElementException:
        return False
    return element

def send_mail(f_num:str, a_num:str, state:str):
    s = SMTP('smtp.web.de', 587)
    s.starttls()
    s.login(from_mail, passwort)#

    message = MIMEMultipart("alternative")
    message["Subject"] = "DM AUFTRAG " + state
    message["From"] = from_mail
    message["To"] = to_mail

    if state == "abholbereit":
        text = """\
        Hi,
        dein auftrag """ + a_num + """ in der Filiale """ + f_num + """ Abholbereit"""
    elif state == "erhalten":
        text = """\
        Hi,
        dein auftrag """ + a_num + """ wurde erhalten"""
    elif state == "wird_geliefert":
        text = """\
        Hi,
        dein auftrag """ + a_num + """ wird zu der Filiale  """ + f_num + """ geliefert"""
    elif state == "gefertig":
        text = """\
        Hi,
        dein auftrag """ + a_num + """ wird gearbeitet"""
    message.attach(MIMEText(text, "plain"))
    s.sendmail("db.zeug@web.de", "moritz.albach@gmail.com", message.as_string())
    s.quit()


def job():
 
    get_new_f_and_a_num()



    for i, order in  enumerate(orders):
        order_state = check_order_state(order[0], order[1])
   



        if(order_state == "abholbereit"):
            if(order_state != order[2]):
                send_mail(order[0], order[1], "abholbereit")
            
        if(order_state == "wird_geliefert"):
            if(order_state != order[2]):
                send_mail(order[0], order[1], "wird_geliefert")

        if(order_state == "gefertig"):
            if(order_state != order[2]):
                send_mail(order[0], order[1], "gefertig")     

        if(order_state == "erhalten"):
            if(order_state != order[2]):
            
                send_mail(order[0], order[1], "erhalten")

   

        orders[i][2] = order_state
   
    print(orders)


schedule.every(10).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(5)