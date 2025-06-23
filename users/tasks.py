from celery import  shared_task

import time
@shared_task
def send_otp_email(user_email, code):
    print("Sending...")
    time.sleep(2)   
    print('Email sent')

@shared_task
def send_daily_report():
    print('Sending daily report...')
    time.sleep(40)
    print('Daily finished')