# pip install boto3
# pip install beautifulsoup4
# pip install requests
# pip install yagmail

import boto3
import email.utils
import os
import requests
import smtplib  
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

BASE_URL = [
'https://www.titan.fitness/racks/power-racks/x-3-series/x-3-half-rack/400406.html',
'https://www.titan.fitness/racks/squat-stands/x-3-series/x-3-series-short-squat-stand-with-spotter-arms/400422.html',
'https://www.titan.fitness/racks/squat-stands/x-3-series/x-3-series-tall-squat-stand-with-pull-up-bar-and-spotter-arms/400404.html',
'https://www.titan.fitness/racks/squat-stands/t-3-series/t-3-series-short-squat-stand-with-j-hooks/400925.2.html',
'https://www.titan.fitness/racks/squat-stands/t-3-series/titan-t-3-series-squat-stand-v2/400994.html',
'https://www.titan.fitness/strength/weight-plates/bumper-plates/230-lb-set-economy-black-bumper-plates/430117.html',
'https://www.titan.fitness/strength/dumbbells/rubber-coated-hex/pair-of-75-lb-black-rubber-coated-hex-dumbbells/421076.html',
'https://www.titan.fitness/strength/dumbbells/rubber-coated-hex/pair-of-100-lb-black-rubber-coated-hex-dumbbells/421101.html',
'https://www.titan.fitness/racks/bench-press-rack-with-flip-down-safeties/400597.html',
'https://www.titan.fitness/strength/barbells/olympic/atlas-bar---mens-20kg-barbell/430090.html',
'https://www.titan.fitness/racks/power-racks/t-3-series/t-3-series-short-space-saving-racks/SSRT3SHUP-SSRT3.html',
'https://www.titan.fitness/strength/specialty-machines/lower-body/economy-h-pnd/401027.html'
]

# loop through the URLs above
for page in BASE_URL:
    # query each website and return html, parse the html using Beautiful Soup and store in variable 'soup'
    soup = BeautifulSoup(requests.get(page).content, 'html.parser')

    # take out the <div> of name and get its value
    product_name_box = soup.find('span', attrs={'class': 'h1 product-name'})
    product_name = product_name_box.text.strip()

    price_box = soup.find('span', attrs={'class': 'sales'})
    price = price_box.text.strip()

    availability_box = soup.find('span', attrs={'class': 'availability-msg'})
    availability = availability_box.text.strip()

    status = 'Product Name: ' + product_name + '\n' + 'Price:        ' + price + '\n' + 'Availability: ' + availability

    # create a text file
    with open('titan.txt', 'a') as f:
        f.write(status + '\n' + '\n')

def send_email():
    CHARSET = 'utf-8'
    AWS_REGION = 'us-west-2'
    SENDER = 'george.davitiani@gmail.com'
    RECIPIENT = 'george.davitiani@gmail.com'
    SUBJECT = 'Titan Fitness Inventory Report'
    ATTACHMENT = 'titan.txt'
    BODY_TEXT = ('email body text.')
    BODY_HTML = """<html>
        <head></head>
        <body>
            <h1> email headline </h1>
            <p> email body text. </p>
        </body>
        </html>"""

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)

    # Create a multipart/mixed parent container.
    msg = MIMEMultipart('mixed')
    # Add subject, from and to lines.
    msg['Subject'] = SUBJECT 
    msg['From'] = SENDER 
    msg['To'] = RECIPIENT

    # Create a multipart/alternative child container.
    msg_body = MIMEMultipart('alternative')

    # Encode the text and HTML content and set the character encoding. This step is
    # necessary if you're sending a message with characters outside the ASCII range.
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)

    # Add the text and HTML parts to the child container.
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)

    # Define the attachment part and encode it using MIMEApplication.
    att = MIMEApplication(open(ATTACHMENT, 'rb').read())

    # Add a header to tell the email client to treat this part as an attachment, and to give the attachment a name.
    att.add_header('Content-Disposition','attachment',filename=os.path.basename(ATTACHMENT))

    # Attach the multipart/alternative child container to the multipart/mixed
    # parent container.
    msg.attach(msg_body)

    # Add the attachment to the parent container.
    msg.attach(att)

    response = client.send_raw_email(
        Source=SENDER,
        Destinations=[RECIPIENT],
        RawMessage={'Data':msg.as_string(),},
    )

# email if keywords are found in the text file
with open('titan.txt') as f:
    if 'In Stock' in f.read():
        send_email()
    elif 'Backorder' in f.read():
        send_email()
    elif 'Select Styles for Availability' in f.read():
        send_email()

# delete the text file
os.remove('titan.txt')