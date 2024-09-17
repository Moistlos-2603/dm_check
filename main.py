# import schedule 
import time
from Auftrag import Auftrag
import imaplib

orders = []

print(orders[0].orderid)

mail = imaplib.IMAP4_SSL('imap.web.de')
mail.login("db.zeug@web.de", "")
mail.list()
mail.select("inbox") 
result, data = mail.search("orderid", "ALL")











# schedule.erver(10).minutes.do(job)
# 
# while True:
    # schedule.run_pending()
    # time.sleep(1)