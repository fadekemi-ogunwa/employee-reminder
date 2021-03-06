#!/bin/bash

import os
import requests
import json
import datetime
from dateutil.relativedelta import relativedelta
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText


load_dotenv(find_dotenv())


recipient_email =  os.environ.get('RECIPIENT_EMAIL')
from_email = os.environ.get('SENDER_EMAIL')

print os.environ.get('SMTP_USERNAME'), os.environ.get('SMTP_PASSWORD')

def employee_anniversary(per_page, current_page, anniversaries=[]):
	url = 'https://rimon.namely.com/api/v1/profiles.json?filter[status]=active&per_page=' + str(per_page) + '&page=' + str(current_page)

	token = os.environ.get('TOKEN')

	payload = "{}"
	headers = {'authorization': 'Bearer ' + token}

	response = requests.request("GET", url, data=payload, headers=headers)

	json_data = json.loads(response.text)
	total_records = json_data['meta']['count']

	print "Total records: " + str(total_records) + "\n"
	print "Current Page: " + str(current_page)
	count = 1

	for row in json_data['profiles']:
		today = datetime.today()
		if row['start_date']:
			employed_date_obj = datetime.strptime(row['start_date'], '%Y-%m-%d') 
			year_difference = today.year - employed_date_obj.year

			current_year_employment_date = employed_date_obj + relativedelta(years=year_difference)
			days_left = (current_year_employment_date - today).days + 1

			if days_left == 14:
				employee = { "fullname": str(row["first_name"], ) + " " + str(row["last_name"],), "anniversary_date": current_year_employment_date.strftime('%Y-%m-%d'), "employed_date": employed_date_obj.strftime('%Y-%m-%d'), "number_of_years": year_difference }
				anniversaries.append(employee)

		else:
			print ""
			
		count = count + 1
	return (anniversaries, (total_records > (per_page*current_page)))



per_page = 50
current_page = 1

api_call = employee_anniversary(per_page, current_page, [])

anniversaries = api_call[0]
run_again = api_call[1]

while run_again:
	current_page += 1
	api_call = employee_anniversary(per_page, current_page, anniversaries)
	anniversaries = api_call[0]
	run_again = api_call[1]


print anniversaries

total_celebrants = len(anniversaries)
if total_celebrants > 0:
	msg_body = "<p>Hey there,</p><p><b>The following people have their Rimoniversaries coming up in just two weeks! Please send the Rimoniversary gift to arrive by the scheduled date. Thank you.</b></p>"
	for celebrant_info in anniversaries:
		msg_body += "<p><b>" + celebrant_info['fullname'] + "</b>   -   Rimoniversary Date: " + celebrant_info['anniversary_date'] + " </p>"
		# msg_body += "<p><b>" + celebrant_info['fullname'] + "</b> - Rimoniversary Date: " + celebrant_info['anniversary_date'] + " <b>" + str(celebrant_info['number_of_years']) + "</b> year(s) in service</p>"
	msg = MIMEMultipart()
	msg['From'] = from_email
	msg['To'] = recipient_email
	import os
	msg['Subject'] = "Anniversary Reminder - " + datetime.today().strftime('%Y-%m-%d')
	msg.attach(MIMEText(msg_body, 'html'))

	text = msg.as_string()

	server = smtplib.SMTP('smtp.office365.com', 587)
	server.starttls()
	server.login(os.environ.get('SMTP_USERNAME'), os.environ.get('SMTP_PASSWORD'))
	response = server.sendmail(from_email, recipient_email, text)
	print response, " - Sent email to ", recipient_email
	server.quit()

	
