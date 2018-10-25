from .models import *


def create_users_company_by_chat(company, chat):
    users = []
    for company_user in company.users.all():
        user_by_chat = UserByChat.objects.get_or_create(            
            user_by_chat=company_user.user,
            chat=chat, defaults={
            	'create_user': chat.create_user, 
            	'user_by_chat': company_user.user,
            	'chat': chat
        	})