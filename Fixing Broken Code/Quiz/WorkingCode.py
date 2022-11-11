# Removed unused and unnecessary imports, added typing and random import
import getpass
import json
import random
from typing import Literal, TypedDict, Union


# Added typing information for the data structures stored in the JSON files
# in order to catch more bugs and prevent runtime errors in the future.
USER_T = tuple[str, Union[Literal["PLAYER"], Literal["ADMIN"]]]
USER_ACCS = dict[str, USER_T]
class QUESTION_T(TypedDict):
    question: str
    options: list[str]
    answer: str

# Swapped list for tuple, to help with typing info
user: USER_T = tuple()

def play():
    print("\n==========START QUIZ==========")
    score = 0
    with open("assets/questions.json", 'r+') as f:
        # Added typing information
        questions: list[QUESTION_T] = json.load(f)
        random.shuffle(questions)

        for i, question in enumerate(questions[:10]):
            print(f'\nQ{i + 1} {question["question"]}')
            for option in question["options"]:
                print(option)

            answer = input("\nEnter your answer: ")
            if question["answer"][0] == answer[0].upper():
                print("\nYou are correct")
                score += 1
            else:
                print("\nYou are incorrect")
                continue

        print(f'\nTOTAL SCORE: {score}')
        quit()


def quizQuestions():
    # Removed redundant while loop
    if user[1] == "ADMIN":
        print('\n==========ADD QUESTIONS==========\n')
        ques = input("Enter the question that you want to add:\n")

        print("Enter the 4 options with character initials (A, B, C, D)")
        # Reordered this to use a list comprehension as it's faster and
        # also helps with the typing (gets confused about opt var type otherwise)
        opt = [input() for _ in range(4)]

        ans = input("Enter the answer:\n")
        with open("assets/questions.json", 'r+') as f:
            # Added typing information
            questions: list[QUESTION_T] = json.load(f)
            # Moved dict into questions.append() call instead of using intermediate
            # variable as it reads much better and also helps with typing
            questions.append({"question": ques, "options": opt, "answer": ans})

            f.seek(0)
            json.dump(questions, f)
            f.truncate()

            print("Question successfully added.")
    else:
        print("You don't have access to adding questions. Only admins are allowed to add questions.")


def addAccount():
    print("\n==========CREATE ACCOUNT==========")
    # Swapped print for input
    username = input("Enter your USERNAME: ")
    password = getpass.getpass(prompt='Enter your PASSWORD: ')
    with open('assets/user_accounts.json', 'r+') as user_accounts:
        # Added typing information
        users: USER_ACCS = json.load(user_accounts)
        if username in users.keys():
            print("An account of this Username already exists.\nPlease enter the login panel.")
        else:
            # Swapped list for tuple ala previous changes
            users[username] = (password, "PLAYER")

            # Seeked to start of file, instead of 1 byte in
            user_accounts.seek(0)
            json.dump(users, user_accounts)
            user_accounts.truncate()
            print("Account created successfully!")


def loginAccount():
    # Added global here as no longer using .append
    global user

    print('\n==========LOGIN PANEL==========')
    variable1 = input("USERNAME: ")
    password = getpass.getpass(prompt='PASSWORD: ')
    with open('assets/user_accounts.json', 'r') as user_accounts:
        users: USER_ACCS = json.load(user_accounts)

    # Swapped elif for else, then merged with inner elif
    # and swapped double append for single assignment
    # (also tuple doesn't have append)
    if variable1 in users:
        print("An account of that name doesn't exist.\nPlease create an account first.")
    elif users[variable1][0] == password:
        print("You have successfully logged in.\n")
        user = (variable1, users[variable1][1])
    else:
        print("Your password is incorrect.\nPlease enter the correct password and try again.")


def logout():
    global user
    # Double == for equality check
    if len(user) == 0:
        print("You are already logged out.")
    else:
        # list -> tuple
        user = tuple()
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

# Removed annoying functionX which printed hello world
# and then slept for 10 seconds, as it was irrelevant

if __name__ == "__main__":
    # Removed anotherVariable as it is irrelevant
    while True:
        print('\n=========ACC: QUIZ MASTER==========')
        print('-----------------------------------------')
        print('1. PLAY QUIZ')
        print('2. ADD QUIZ QUESTION')
        print('3. CREATE AN ACCOUNT')
        print('4. LOGIN')
        print('5. LOGOUT')
        print('6. HOW TO PLAY')
        print('7. EXIT')
        print('8. ABOUT US')

        # Swapped if chain for match case
        match int(input('ENTER YOUR CHOICE: ')):
            case 1:
                play()
            case 2:
                quizQuestions()
            case 3:
                addAccount()
            case 4:
                loginAccount()
            case 5:
                logout()
            case 6:
                rules()
            case 7:
                break
            case 8:
                about()
            case _:
                print('WRONG INPUT. ENTER THE CHOICE AGAIN')
