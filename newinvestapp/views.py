from django.shortcuts import render, redirect, reverse

from django.core.mail import BadHeaderError, send_mail

from django.http import HttpResponse,HttpResponseRedirect

from django.contrib import messages

from django.contrib.auth import login, authenticate, logout

from django.contrib.auth.forms import UserCreationForm

from django.core.mail import EmailMessage, EmailMultiAlternatives

from django.conf import settings

from django.template.loader import render_to_string

from .models import *

from .forms import *

from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth.decorators import login_required

from django.utils.html import strip_tags

import datetime
import json
import requests
import uuid
import os

# Create your views here.

def home(request):
	return render(request, 'newinvestapp/index.html')

def about(request):
	return render(request, 'newinvestapp/about.html')

def affiliate(request):
	return render(request, 'newinvestapp/affiliate.html')

def team(request):
	return render(request, 'newinvestapp/index.html')

def stocks(request):
	return render(request, 'newinvestapp/stocks.html')

def realestate(request):
	return render(request, 'newinvestapp/realestate.html')

def immigration(request):
	return render(request, 'newinvestapp/immigration.html')

def contact(request):
	if request.method == 'GET':
		form= ContactForm()
	else:
		form = ContactForm(request.POST)
		if form.is_valid():
			name= form.cleaned_data['name']
			email= form.cleaned_data['email']
			message = form.cleaned_data['message']

			try:
				send_mail(name, "Investor {} has sent a message saying: {}".format(email, message),email, ['support@assetarbor.org'])
			except BadHeaderError:
				return HttpResponse('Invalid header found.')

			return HttpResponse('Your message has been sent successfully')
	context={'form': form}
	return render(request, 'newinvestapp/contact.html', context)

def services(request):
	return render(request, 'newinvestapp/investment-services.html')

def signin(request):
	if request.user.is_authenticated:
		return redirect('dashboard')

	else:
		if request.method == "POST":
			username= request.POST.get('username')
			password= request.POST.get('password')

			user= authenticate(request, username=username, password=password)

			if user is not None:
				email= User.objects.get(username=username).email
				print(email)
				template= render_to_string('newinvestapp/loginAlert.html', {'name':username})
				plain_message= strip_tags(template)
				email_message= EmailMultiAlternatives(
					'Login alert on your account!',
					plain_message,
					settings.EMAIL_HOST_USER,
					[email]

					)
				email_message.attach_alternative(template, 'text/html')
				email_message.fail_silently= False
				email_message.send()
				login(request, user)
				return redirect('dashboard')

			else:
				messages.error(request, "username or password is incorrect")

	context={}
	return render(request, 'newinvestapp/login.html')


def main_view(request, *args, **kwargs):
	code= str(kwargs.get('ref_code'))

	try:
		client = Client.objects.get(code=code)
		request.session['ref_client'] = client.id
		print('id', client.id)
	except:
		pass
	print(request.session.get_expiry_age())

	return render(request, 'newinvestapp/main.html')


def signup(request):
	user_check = request.user.is_authenticated
	if user_check:
		return redirect('dashboard')
	client_id= request.session.get('ref_client')
	print('client_id', client_id)
	form = CreateUserForm(request.POST or None)
	if form.is_valid():
		if client_id is not None:
			recommended_by_client= Client.objects.get(id=client_id)
			recommended_by_client_email= recommended_by_client.email_address
			recommended_by_client_name= recommended_by_client.first_name
			username=form.cleaned_data.get('username')

			instance= form.save()
			registered_user= User.objects.get(id=instance.id)
			registered_client= Client.objects.get(user=registered_user)
			registered_client.recommended_by= recommended_by_client.user
			referral_template= render_to_string('newinvestapp/referalsignupmail.html', {'name':recommended_by_client_name, 'refereed':username})
			plain_message= strip_tags(referral_template)
			email_message= EmailMultiAlternatives(
				'You refered a user using your referral link',
				plain_message,
				settings.EMAIL_HOST_USER,
				[recommended_by_client_email],
				)
			email_message.attach_alternative(referral_template, 'text/html')
			email_message.send()
			registered_client.save()

		else:
			form.save()

		username=form.cleaned_data.get('username')
		password= form.cleaned_data.get('password1')
		password_reminder= password[:1]
		password_reminder_two= password[-1:]
		email= form.cleaned_data.get('email')
		template= render_to_string('newinvestapp/welcomeEmail.html', {'name':username,'password':password})
		plain_message= strip_tags(template)
		email_message= EmailMultiAlternatives(
			'Welcome to Asset Arbor',
			plain_message,
			settings.EMAIL_HOST_USER,
			[email],

			)
		email_message.attach_alternative(template, 'text/html')
		email_message.send()

		second_template= render_to_string('newinvestapp/securityEmail.html', {'name': username, 'password_reminder':password_reminder, 'password_reminder_two':password_reminder_two})
		second_plain_message= strip_tags(second_template)
		second_email_message= EmailMultiAlternatives(
			"Stay updated and discover more with Asset Arbor!",
			second_plain_message,
			settings.EMAIL_HOST_USER,
			[email]
			)
		second_email_message.attach_alternative(second_template, 'text/html')
		second_email_message.send()

		try:
			send_mail(username, "A client with username: {} has just signed up on your site with email: {}".format(username, email),settings.EMAIL_HOST_USER, ['support@assetarbor.org'])
		except BadHeaderError:
			return HttpResponse("Your account has been created but you can't login at this time. please, try to login later")
		user= authenticate(username=username, password=password)
		login(request, user)
		return redirect('dashboard')
	context={'form':form}
	return render(request, 'newinvestapp/signup.html', context)
def faq(request):
	return render(request, 'newinvestapp/faq.html')

def pricing(request):
	return render(request, 'bukasonapp/pricing.html')


def bounty(request):
	return HttpResponse('bounty')

def terms(request):
	return render(request, 'bukasonapp/terms.html')

def privacy(request):
	return render(request, 'empireInvestApp/privacy.html')


@login_required(login_url='signin')
def dashboard(request):
	client= request.user.client
	client_firstname= request.user.username
	client_email= request.user.email
	client_pk= client.pk
	client_deposit= client.deposit
	client_profit= client.profit
	client_bal= float(client_deposit) + float(client_profit)
	client_withdrawal= client.withdrawal
	client_date_joined= client.created
	client_code= client.code
	client.save()
	context={'client': client, 'client_deposit':client_deposit, 'client_bal':client_bal,'client_profit':client_profit, 'client_date_joined':client_date_joined,
	'client_withdrawal':client_withdrawal, 'client_code':client_code }
	return render(request, 'newinvestapp/dashboardtwo.html', context)

@login_required(login_url='signin')
def deposit(request):
	if request.method == 'POST':
		client= request.user.client
		client_name= request.user.username
		client_email= client.email_address
		#post data to create invoice for payment
		price_amount= request.POST.get('price_amount')
		price_currency= "usd"
		investment_info= request.POST.get('investment_info')
		investment_info_split= investment_info.split('#')
		investment_plan= investment_info_split[0]
		investment_plan_name= investment_info_split[1]
		investment_contract_duration= investment_info_split[2]
		print(investment_plan)
		print(investment_plan_name)
		pay_currency= request.POST.get('pay_currency')
		order_id= 'Algorithm Trades'
		order_description= "This is a plan subscription"
		if price_amount and pay_currency:
			# Api's url link
			url= 'https://api.nowpayments.io/v1/invoice'
			payload=json.dumps({
				"price_amount": price_amount,
				"price_currency": price_currency,
				"pay_currency": pay_currency,
				"order_id": order_id,
				"order_description": order_description,
				"ipn_callback_url": "https://nowpayments.io",
				"success_url": "https://www.AssetArbor.org/dashboard",
				#our success url will direct us to the get_payment_status view for balance top ups
				"cancel_url": "https://www.AssetArbor.org/dashboard"
			})
			headers={'x-api-key':'', 'Content-Type': 'application/json'}
			response= requests.request('POST', url, headers=headers, data=payload)
			res= response.json()
			print(res)
			generated_link= res["invoice_url"]
			generated_payment_id= res["id"]
			#Now get the user and add the payment ID to the database as we will be using it to know their payment status
			Payment_id.objects.create(
				client=client,
				payment_id= generated_payment_id,
				price_amount= price_amount,
				investment_plan=investment_plan,
				investment_plan_name=investment_plan_name,
				contract_duration= investment_contract_duration,
				)
			template= render_to_string('newinvestapp/pendingDepositEmail.html', {'name': client_name, 'amount':price_amount, 'transaction_id':generated_payment_id})
			plain_message= strip_tags(template)
			emailmessage= EmailMultiAlternatives(
				'Pending Deposit Order',
				plain_message,
				settings.EMAIL_HOST_USER,
				[client_email],
				)
			emailmessage.attach_alternative(template, 'text/html')
			emailmessage.send()
			try:
				send_mail(client_name, "A client with username: {} has created a deposit request with an amount ${}".format(client_name, price_amount),settings.EMAIL_HOST_USER, ['info@assetarbor.org'])
			except BadHeaderError:
				pass
			return redirect(generated_link)
	context={}
	return render(request, 'newinvestapp/deposittwo.html')

def carddeposit(request):
	return HttpResponse('Currently not available at the moment, please try again later.')

@login_required(login_url='signin')
def withdrawal(request):
	client= request.user.client
	client_id= client.id
	client_username= request.user.username
	client_email= client.email_address
	client_deposit= client.deposit
	client_withdrawal= client.withdrawal
	print(client_deposit)
	client_profit= client.profit
	client_info= Client.objects.filter(id=client_id)
	if request.method =='POST':
		withdrawal_option = request.POST.get('withdrawal_category')
		amount= request.POST.get('amount')
		withdrawal_address= request.POST.get('withdrawal_address')
		crypto= request.POST.get('crypto')
		if withdrawal_option == 'deposit' and float(client_deposit)>10:
			client_deposit_balance= float(client_deposit) - float(amount)
			client_withdrawal_balance= float(client_withdrawal) + float(amount)
			if client_deposit_balance < 0:
				messages.error(request, "Amount requested is greater than deposit")
			else:
				client_update= client_info.update(deposit=client_deposit_balance, withdrawal=client_withdrawal_balance)
				Withdrawal_request.objects.create(
					client= client,
					client_username= client_username,
					client_email= client_email,
					crypto_used_for_requesting_withdrawal= crypto,
					withdrawal_address= withdrawal_address,
					amount= amount
					)
				try:
					send_mail(client_username, "A client with username: {} has requested a withdrawal of {}".format(client_username, amount),client_email, ['support@assetarbor.org'])

				except BadHeaderError:
					return HttpResponse('Something went wrong, please try again later')


		if withdrawal_option == 'deposit' and float(client_deposit)<=10:
			messages.error(request, "Your deposit is too low for this withdrawal.")

		if withdrawal_option == 'profit' and float(client_profit) > 10:
			client_profit_balance= float(client_profit) - float(amount)
			client_withdrawal_balance= float(client_withdrawal) + float(amount)
			if client_profit_balance < 0:
				messages.error(request, "Amount requested is greater than profit")
			else:
				client_update= client_info.update(profit= client_profit_balance, withdrawal=client_withdrawal_balance)
				Withdrawal_request.objects.create(
					client= client,
					client_username= client_username,
					client_email= client_email,
					crypto_used_for_requesting_withdrawal= crypto,
					withdrawal_address= withdrawal_address,
					amount= amount
					)
				try:
					send_mail(client_username, "A client with username: {} has requested a withdrawal of {}".format(client_username, amount),client_email, ['support@assetarbor.org'])
				except BadHeaderError:
					return HttpResponse('Something went wrong, please try again later')

		if withdrawal_option == 'profit' and float(client_profit) <=10:
			messages.error(request, "Your profit is too low for this withdrawal" )
	context={}
	return render(request, 'newinvestapp/withdrawal.html', context)

def history(request):
	return HttpResponse('history')

@login_required(login_url='signin')
def myreferals(request):
    info= request.user
    client= Client.objects.get(user=info)
    ref_info= client.get_recommended_profiles()
    client_code= client.code
    context={'ref_info': ref_info, 'client_code':client_code}
    return render(request, 'newinvestapp/referralprofilestwo.html', context)

@login_required(login_url='signin')
@staff_member_required
def confirm_withdrawal(request):
	withdrawalInfo= Withdrawal_request.objects.all()
	context={'withdrawalInfo': withdrawalInfo}
	return render(request, 'newinvestapp/confirmWithdrawal.html', context)

@login_required(login_url='signin')
@staff_member_required
def update_withdrawal(request, pk):
	withdrawalInfo= Withdrawal_request.objects.get(id=pk)
	withdrawalInfo_id= withdrawalInfo.id
	withdrawalInfo_amount= withdrawalInfo.amount
	withdrawal_address= withdrawalInfo.withdrawal_address
	client_id= withdrawalInfo.client.id
	client= Client.objects.get(id=client_id)
	client_bal= client.deposit
	client_name= client.first_name
	client_email= client.email_address
	client_withdrawal= client.withdrawal
	template= render_to_string('newinvestapp/withdrawalEmail.html', {'name': client_name, 'amount':withdrawalInfo_amount, 'wallet_address':withdrawal_address})
	plain_message= strip_tags(template)
	emailmessage= EmailMultiAlternatives(
		'Congratulations, Your withdrawal request has been approved!',
		plain_message,
		settings.EMAIL_HOST_USER,
		[client_email],
		)
	email_message.attach_alternative(template, 'text/html')
	emailmessage.fail_silently=False
	emailmessage.send()
	delete_withdrawal= withdrawalInfo.delete()
	return HttpResponse('Update withdrawal')

@login_required(login_url='signin')
@staff_member_required
def decline_wihdrawal(request, pk):
	withdrawalInfo= Withdrawal_request.objects.get(id=pk)
	withdrawalInfo_id= withdrawalInfo.id
	withdrawalInfo_amount= withdrawalInfo.amount
	withdrawal_address= withdrawalInfo.withdrawal_address
	client_id= withdrawalInfo.client.id
	client= Client.objects.get(id=client_id)
	client_info= Client.objects.filter(id=client_id)
	client_bal= client.deposit
	client_name= client.first_name
	client_email= client.email_address
	client_withdrawal= client.withdrawal
	client_balance_reup= float(withdrawalInfo_amount) + float(client_bal)
	client_withdrawal_reup= float(client_withdrawal) - float(withdrawalInfo_amount)
	client_info_update= client_info.update(deposit=client_balance_reup, withdrawal=client_withdrawal_reup)
	template= render_to_string('newinvestapp/declineWithdrawalEmail.html', {'name': client_name, 'amount':withdrawalInfo_amount, 'wallet_address':withdrawal_address})
	plain_message= strip_tags(template)
	emailmessage= EmailMultiAlternatives(
		'Withdrawal request declined!',
		plain_message,
		settings.EMAIL_HOST_USER,
		[client_email],
		)
	email_message.attach_alternative(template, 'text/html')
	emailmessage.fail_silently=False
	emailmessage.send()
	Transaction.objects.create(
		client=client,
		transaction_type='Withdrawal',
		amount= withdrawalInfo_amount,
		status= 'Declined'
		)
	delete_withdrawal= withdrawalInfo.delete()
	return HttpResponse('Withdrawal request declined')


@login_required(login_url='signin')
@staff_member_required
def confirm_deposit(request):
	paymentInfo= Payment_id.objects.all()
	context={'paymentInfo': paymentInfo}
	return render(request, 'newinvestapp/confirmdeposit.html', context)


@login_required(login_url='signin')
@staff_member_required
def update_payment(request, pk):
	payment_info= Payment_id.objects.get(id=pk)
	payment_info_id= payment_info.id
	payment_info_amount= payment_info.price_amount
	client_id= payment_info.client.id
	client= Client.objects.get(id=client_id)
	client_deposit= client.deposit
	client_name= client.first_name
	client_email= client.email_address
	client_pk= client.id
	print(client_deposit)
	client_info= Client.objects.filter(id=client_pk)
	newClientbal= float(payment_info_amount) + float(client_deposit)
	update_payment= client_info.update(deposit=newClientbal)
	template= render_to_string('newinvestapp/confirmDepositEmail.html', {'name':client_name, 'amount':payment_info_amount})
	plain_message= strip_tags(template)
	emailmessage= EmailMultiAlternatives(
		'Congratulations, Your deposit was successful!',
		plain_message,
		settings.EMAIL_HOST_USER,
		[client_email],

		)
	email_message.attach_alternative(template, 'text/html')
	emailmessage.fail_silently=False
	emailmessage.send()

	Transaction.objects.create(
		client=client,
		transaction_type='Deposit',
		amount= payment_info_amount,
		status= 'Approved'
		)
	delete_payment_info= payment_info.delete()
	if update_payment:
		return HttpResponse('Account Updated successfully')
	return HttpResponse('Update payment')

@login_required(login_url='signin')
def account_settings(request):

	client= request.user.client

	form=ClientForm(instance=client)

	if request.method=='POST':
		form= ClientForm(request.POST, request.FILES, instance=client)
		if form.is_valid():
			form.save()

	context= {"form":form}
	return render(request, 'newinvestapp/account_settings.html', context)

@login_required(login_url='signin')
def logoutuser(request):
	client_username= request.user.username
	client_email= request.user.email
	template= render_to_string('newinvestapp/logoutMail.html', {'name':client_username})
	plain_message= strip_tags(template)
	emailmessage= EmailMultiAlternatives(
		'Logout Notification',
		plain_message,
		settings.EMAIL_HOST_USER,
		[client_email],

		)
	emailmessage.attach_alternative(template, 'text/html')
	emailmessage.send()
	logout(request)
	return redirect('signin')

def crypto(request):
	return render(request, 'crypto.html')

def oilandgas(request):
	return render(request, 'oil&gas.html')

def forex(request):
	return render(request, 'forex.html')

def agriculture(request):
	return render(request, 'agriculture.html')

def retirement(request):
	return render(request, 'retirement.html')