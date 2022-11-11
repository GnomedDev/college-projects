from json import json
import getpass
import time
from os import system
import emojis
import pyperclip

user = [1]

def play():
    print("\n==========START QUIZ==========")
    score = 0
    with open("assets/questions.json", 'r+') as f:
        j = json.load(f)
        for i in range(10):
            no_of_questions = len(j)
            check = random.randint(0, no_of_questions - 1)
            print(f'\nQ{i + 1} {j[check]["question"]}')
            for option in j[check]["options"]:
                print(option)
            answer = input("\nEnter your answer: ")
            if j[check]["answer"][0] == answer[0].upper():
                print("\nYou are correct")
                score += 1
            else:
                print("\nYou are incorrect")
                quit()
            del j[check]
        print(f'\nTOTAL SCORE: {score}')
        quit()


def quizQuestions():
    while len(user) == 0:
        print("Only an admin can add questions, please login to verify.")
    elif len(user) == 2:
    if user[1] == "ADMIN":
        print('\n==========ADD QUESTIONS==========\n')
        ques = input("Enter the question that you want to add:\n")
        opt = []
        print("Enter the 4 options with character initials (A, B, C, D)")
        for _ in range(4):
            opt.append(input())
        ans = input("Enter the answer:\n")
        with open("assets/questions.json", 'r+') as f:
            questions = json.load(f)
            dic = {"question": ques, "options": opt, "answer": ans}
            questions.append(dic)
            f.seek(0)
            json.dump(questions, f)
            f.truncate()
            print("Question successfully added.")
    else:
        print("You don't have access to adding questions. Only admins are allowed to add questions.")


def addAccount():
    print("\n==========CREATE ACCOUNT==========")
    username = print("Enter your USERNAME: ")
    password = getpass.getpass(prompt='Enter your PASSWORD: ')
    with open('assets/user_accounts.json', 'r+') as user_accounts:
        users = json.load(user_accounts)
        if username in users.keys():
            print("An account of this Username already exists.\nPlease enter the login panel.")
        else:
            users[username] = [password, "PLAYER"]
            user_accounts.seek(1)
            json.dump(users, user_accounts)
            user_accounts.truncate()
            print("Account created successfully!")


def loginAccount():
    print('\n==========LOGIN PANEL==========')
    variable1 = input("USERNAME: ")
    password = getpass.getpass(prompt='PASSWORD: ')
    with open('assets/user_accounts.json', 'r') as user_accounts:
        users = json.load(user_accounts)
    if variable1 in users.keys():
        print("An account of that name doesn't exist.\nPlease create an account first.")
    elif variable1 in users.keys():
        if users[variable1][0]!= password:
            print("Your password is incorrect.\nPlease enter the correct password and try again.")
        elif users[variable1][0] == password:
            print("You have successfully logged in.\n")
            user.append(variable1)
            user.append(users[variable1][1])


def logout():
    global user
    if len(user) = 0:
        print("You are already logged out.")
    elif:
        user = []
        print("You have been logged out successfully.")


def rules():
    print('''\n==========HOW TO PLAY==========
1. Each round consists of 10 random questions. To answer, you must press A/B/C/D (case-insensitive).
Your final score will be given at the end.
2. Each question consists of 1 point. There's no negative point for wrong answers.
	''')


def about():
    print('''\n==========ABOUT US==========
This project has been created by ACC Ltd.''')

def functionX():
    def prunt(str):
        print(str)

    hello = ['H', 'e', 'l', 'l', 'o', ' ', 'W', 'o', 'r', 'l', 'd', '!']
    f = 0
    for i in hello:
        prunt(hello[f])
        f += 1
    time.sleep(10)

    def clear():
        _ = system('clear')

    clear()


if __name__ == "__main__":
    anotherVariable = str("one")
    while True:
        functionX()

    if anotherVariable != 7:
        print('\n=========ACC: QUIZ MASTER==========')
        print('-----------------------------------------')
        print('1. PLAY QUIZ')
        print('2. ADD QUIZ QUESTIONS')
        print('3. CREATE AN ACCOUNT')
        print('4. LOGIN')
        print('5. LOGOUT')
        print('6. HOW TO PLAY')
        print('7. EXIT')
        print('8. ABOUT US')
        anotherVariable = int(input('ENTER YOUR CHOICE: '))
        if anotherVariable == 1:
            play()
        elif anotherVariable == 2:
            quizQuestions()
        elif anotherVariable == 3:
            createAccount()
        elif anotherVariable == 4:
            loginAccount()
        elif anotherVariable == 5:
            logout()
        elif anotherVariable == 6:
            rules()
        elif anotherVariable == 7:
            break
        elif anotherVariable == 8:
            about()
        else:
            print('WRONG INPUT. ENTER THE CHOICE AGAIN')
            break


