from flask import Flask, render_template, request, redirect, session, url_for
import requests
import json
import base64
import datetime
from datetime import timedelta
import time
import re
import csv
import codecs

application = Flask(__name__)

# Get required key to access Eloqua API
def getEloquaAccess():

    # Eloqua Login Credentials
    site = ''
    username = ''
    pw = ''

    # Necessary key to access Eloqua API
    key = site+'\\'+username+':'+pw
    authKey = base64.b64encode(key.encode('ascii'))

    # Key and JSON signals to Eloqua
    headers = {
        'Authorization' : 'Basic ' + authKey.decode('ascii').strip(),
        'content-type' : 'application/json',
        'Accept' : 'application/json; encoding="utf8"'
    }

    # Get Base URL
    r = requests.get('https://login.eloqua.com/id', headers=headers)
    baseUrl = r.json()['urls']['base']

    apiAccess = {}
    apiAccess['headers'] = headers
    apiAccess['baseUrl'] = baseUrl

    return apiAccess


@application.route("/webhook/eloqua-integration", methods=["GET", "POST"])
def eloqua_integration():

    if request.method == 'GET':

        return render_template("webhook-eloqua-integration-test.html")

    if request.method == 'POST':

        # retrieve and parse POST data
        emailAddress = request.form['emailAddress']
        country = request.form['country']
        try:
            firstname = request.form['firstname']
        except:
            firstname = ''
        try:
            lastname = request.form['lastname']
        except:
            lastname = ''
        try:
            campaignName = request.form['campaignName']
        except:
            campaignName = ''
        try:
            urlOfAppearance = request.form['urlOfAppearance']
        except:
            urlOfAppearance = ''
        try:
            gdprLanguage = request.form['gdprLanguage']
        except:
            gdprLanguage = ''
        try:
            optin = request.form['optin']
            optinValue = 'on'
        except:
            optinValue = 'off'

        apiAccess = getEloquaAccess()

        headers = apiAccess['headers']
        baseUrl = apiAccess['baseUrl']

        formData = {
            'fieldValues' : [
                {
                    'id' : '105758',
                    'value' : emailAddress
                },
                {
                    'id' : '105759',
                    'value' : firstname
                },
                {
                    'id' : '106362',
                    'value' : lastname
                },
                {
                    'id' : '106365',
                    'value' : country
                },
                {
                    'id' : '105760',
                    'value' : campaignName
                },
                {
                    'id' : '106364',
                    'value' : urlOfAppearance
                },
                {
                    'id' : '105761',
                    'value' : optinValue
                }
            ]
        }
        formData=json.dumps(formData)
        submitDataReq = requests.post(baseUrl + "/api/REST/2.0/data/form/5463", data=formData, headers=headers)
        if submitDataReq.status_code == 201:
            print('True')
            submitFlag = 'True'
            return submitFlag
        else:
            print('False')
            submitFlag = 'False'
            return submitFlag


@application.route("/webhook/email-notification", methods=["GET", "POST"])
def email_notification():

    if request.method == 'GET':

        return render_template("webhook-email-notification-test.html")

    if request.method == 'POST':

        apiAccess = getEloquaAccess()
        headers = apiAccess['headers']
        baseUrl = apiAccess['baseUrl']

        emailAddress = request.form['emailAddress']

        getCdoDataReq = requests.get(baseUrl + "/api/REST/2.0/data/customObject/2309/instances?search=uniqueCode='" + emailAddress + "'", headers=headers)

        cdoData = getCdoDataReq.json()['elements'][0]['fieldValues']
        for i in cdoData:
            
            if i['id'] == '29916':
                leadIdSummary = i['value']

            if i['id'] == '29917':
                serialNumberModelIdSummary = i['value']

            if i['id'] == '29918':
                productSummary = i['value']

        productSummarySplit = productSummary.split('::')
        productSummaryList = []
        for i in productSummarySplit:
            tempSplit = i.split(';')
            elem = {}
            elem['leadId'] = tempSplit[0]
            elem['locationId'] = tempSplit[1]
            elem['serialNumber'] = tempSplit[2]
            elem['modelId'] = tempSplit[3]
            productSummaryList.append(elem)

        for i in productSummaryList:

            emailSubjectLine = 'Product Summary for Product Serial Number : %s' % i['serialNumber']
            emailSendTo = ''

            emailHtmlMessage = """
                <!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.0 Transitional//EN' 'http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd'><html xmlns='http://www.w3.org/1999/xhtml'><head>
                <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
                <!--[if !mso]><!-->
                <meta http-equiv='X-UA-Compatible' content='IE=edge'>
                <!--<![endif]-->
                <meta name='viewport' content='width=device-width, initial-scale=1.0'>
                <title></title>
                <style type='text/css'>

                </style>
                <!--[if (gte mso 9)|(IE)]>
                <style type='text/css'>
                table {border-collapse: collapse !important;}
                </style>
                <![endif]-->
                <style type='text/css'>

                body {
                margin: 0 !important;
                padding: 0;
                background-color: #ffffff;
                }
                table {
                border-spacing: 0;
                font-family: Arial, Helvetica, sans-serif;
                color: #000000;
                }
                td {
                padding: 0;
                }
                img {
                border: 0;
                }
                div[style*='margin: 16px 0'] { 
                margin:0 !important;
                }
                .wrapper {
                width: 100%;
                table-layout: fixed;
                -webkit-text-size-adjust: 100%;
                -ms-text-size-adjust: 100%;
                }
                .webkit {
                max-width: 600px;
                margin: 0 auto;
                }
                .outer {
                margin: 0 auto;
                width: 100%;
                max-width: 600px;
                }
                .inner {
                padding: 10px;
                }
                .contents {
                width: 100%;
                }
                p, span {
                margin: 0;
                }
                a {
                color: #000000;
                text-decoration: underline;
                }

                .one-column .contents {
                text-align: left;
                }
                .one-column p {
                font-size: 14px;
                margin-bottom: 10px;
                }

                </style>
                </head>
                <body style='padding-top:0;padding-bottom:0;padding-right:0;padding-left:0;margin-top:0 !important;margin-bottom:0 !important;margin-right:0 !important;margin-left:0 !important;'>
                <center class='wrapper' style='width:100%;table-layout:fixed;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;'>
                <div class='webkit' style='max-width:600px;margin-top:0;margin-bottom:0;margin-right:auto;margin-left:auto;'>
                  <!--[if (gte mso 9)|(IE)]>
                <table height='100%' width='100%' cellpadding='0' cellspacing='0' border='0'>
                <tr>
                  <td valign='top' align='left' background=''>
                  <table width='600' align='center' style='border-spacing:0;font-family:Arial, Helvetica, sans-serif;color:#000000;' >
                  <tr>
                  <td style='padding-top:0;padding-bottom:0;padding-right:0;padding-left:0;' >
                  <![endif]-->
                  <table bgcolor='#ffffff' cellpadding='0' cellspacing='0' border='0' class='outer' align='left' style='border-spacing:0;font-family:Arial, Helvetica, sans-serif;color:#000000;margin-top:0;margin-bottom:0;margin-right:auto;margin-left:auto;width:100%;max-width:600px;'>
                    <tbody>
                      <tr>
                        <td class='one-column' style='padding-top:0;padding-bottom:0;padding-right:0;padding-left:0'>
                          <table cellpadding='0' cellspacing='0' border='0' width='100%'>
                            <tbody><tr>
                              <td class='inner contents' style='padding-left:30px;padding-right:30px;padding-top:10px;padding-bottom:10px;font-family:Avenir TT Book, Arial, Helvetica, sans-serif;font-size:16px;color:#000000;width:100%;text-align:left;'>
                                
                                <p>
                                Email Address: """ + emailAddress + """<br>
                                Lead ID: """ + i['leadId'] + """<br>
                                Location ID: """ + i['locationId'] + """<br>
                                Serial Number: """ + i['serialNumber'] + """<br>
                                Model ID: """ + i['modelId'] + """<br>
                                </p>
                              </td>
                            </tr>
                          </tbody></table>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  <!--[if (gte mso 9)|(IE)]>
                  </td>
                  </tr>
                  </table>
                <![endif]-->
                </div>
                </center>

                </body>
                </html>"""

            # Use Mailgun to send email
            MAILGUN_API_KEY = ''
            MAILGUN_DOMAIN_NAME = ''

            requests.post(
                MAILGUN_DOMAIN_NAME,
                auth=("api", MAILGUN_API_KEY),
                data={"from": "Email Notifications <email@test.com>",
                    "to": emailSendTo,
                    "subject": emailSubjectLine,
                    "html": emailHtmlMessage},)        



if __name__ == "__main__":
    application.run(host='0.0.0.0')
