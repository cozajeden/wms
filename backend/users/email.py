from django.core.mail import EmailMultiAlternatives

def non_existing_job_alert():
    subject = "SMTP TEST 2"
    text_content = f'Test'
    html_content = f'''<p style="font-size:3rem;">Test</p>'''
    msg = EmailMultiAlternatives(
        subject, text_content,
        to=['cozajeden@gmail.com'],
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()