import subprocess
options = '''
1. Main Script
2. Login
3. Member Scrapper
4. Message Sender
5. User Scrapper
6. Group Scrapper
7. Group Poster
'''

print(options)
res = input("Choose: ")

if res == '1':
    subprocess.run(['py', 'main.py'])
elif res == '2':
    subprocess.run(['py', 'login.py'])
elif res == '3':
    subprocess.run(['py', '-m', 'member_extracter.member_scrapper'])
elif res == '4':
    subprocess.run(['py', '-m', 'message_sender.msg_sender'])
elif res == '5':
    subprocess.run(['py', '-m', 'user_scrapper.user_scrapper'])
elif res == '6':
    subprocess.run(['py', '-m', 'group_scrapper.group_scrapper'])
elif res == '7':
    subprocess.run(['py', '-m', 'group_poster.group_poster'])
# elif res == '8':
#     subprocess.run(['py', '-m', 'like_scrapper.like_scrapper'])
else:
    print("Invalid Option")
