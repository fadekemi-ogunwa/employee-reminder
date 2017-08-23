#!/bin/bash
import yampy
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
from time import sleep


load_dotenv(find_dotenv())

yammer = yampy.Yammer(access_token=os.environ.get('YAMMER_TOKEN'))



recipient_email =  os.environ.get('RECIPIENT_EMAIL')
from_email = os.environ.get('SENDER_EMAIL')

def employee_anniversary(per_page, current_page, anniversaries=[]):
	url = 'https://rimon.namely.com/api/v1/profiles.json?filter[user_status]=active&per_page=' + str(per_page) + '&page=' + str(current_page)

	token = os.environ.get('TOKEN')

	payload = "{}"
	headers = {'authorization': 'Bearer ' + token}

	response = requests.request("GET", url, data=payload, headers=headers)

	json_data = json.loads(response.text)
	total_records = json_data['meta']['total_count']

	print "Total records: " + str(total_records) + "\n"
	print "Current Page: " + str(current_page)
	count = 1

	sleep(35)
	for row in json_data['profiles']:
		today = datetime.today()
		if row['start_date']:
			employed_date_obj = datetime.strptime(row['start_date'], '%Y-%m-%d') 
			year_difference = today.year - employed_date_obj.year

			current_year_employment_date = employed_date_obj + relativedelta(years=year_difference)
			days_left = (current_year_employment_date - today).days + 1

			employee = { "fullname": str(row["first_name"], ) + " " + str(row["last_name"],), "anniversary_date": current_year_employment_date.strftime('%Y-%m-%d'), "employed_date": employed_date_obj.strftime('%Y-%m-%d'), "number_of_years": year_difference }

			# Post to Yammer
			if days_left == 0 and year_difference > 0:
				if count % 8 == 0:
					sleep(35)
				yammer_post = "Happy Rimoniversary to " + employee['fullname'] + ". Today marks " + str(year_difference) + " year(s) with the firm." 
				yammer.messages.create(yammer_post, topics=["Rimonniversary"])
				count = count + 1

			if days_left == 14 and year_difference > 0:
				anniversaries.append(employee)

		else:
			print ""
			
		
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
		if celebrant_info['dietary_restrictions'] != None:
			msg_body += "<p><b>Allergies:</b> " + celebrant_info['dietary_restrictions'] + "</b></p><br>"


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



