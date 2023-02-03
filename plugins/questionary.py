from main import *

name = Interview("lastname")  # first question should in callback, in button, starting registration "proceed_lastname"
name.datatest = vd.is_letter

name = Interview("name")
name.datatest = vd.is_letter

name = Interview("patronymic")
name.datatest = vd.is_letter

email = Interview("email")
email.datatest = vd.is_email

phone = Interview("phone")
phone.datatest = vd.is_phone

passport = Interview("passport")

regaddress = Interview("regaddress")

gender = Interview("gender")
gender.but_main1 = ('🕺', 'proceed_male')
gender.but_main2 = ('💃', 'proceed_female')

confirm = Interview("confirm")