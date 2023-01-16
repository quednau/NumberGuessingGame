import logging
# Change logging level here:

logging.basicConfig(level=logging.DEBUG, filename="NGG.log", filemode="w",
format="%(asctime)s: %(levelname)s - %(message)s")

import random
import math
import tkinter

# Just initializing vars
the_number = 0
lower_bound = 1
upper_bound = 100
tries = int(0)
hints = []

# ISSUES
# No known bugs atm, but ...
# ... there's something wonky going on in process_guess(), I can feel it
#
# Could use a refactor, though:
# - Would benefit from Classes
# - esp. "process_guess" is a way too chunky function that at least should be split


def generate_number():
    num = random.randint(lower_bound, upper_bound)
    logging.info("Number %s generated", num)
    return num

def get_digit_sum(num):
    digits = [char for char in str(num)]
    digit_sum = 0

    for i in digits:
        digit_sum += int(i)

    while digit_sum > 9:
        digits = [char for char in str(digit_sum)]
        digit_sum = 0
        for i in digits:
            digit_sum += int(i)
    logging.debug('The digit sum of %s is %s', num, digit_sum)
    return digit_sum

# This generates the hints based on the target number (and independent from a user's guess)
def static_hints(num):
    num = the_number
    static_hint_list = []
    if num % 2 == 0:
        static_hint_list.append(f'The number is even.')
    if num % 3 == 0:
        static_hint_list.append(f'The number is divisible by three.')
    if num % 5 == 0:
        static_hint_list.append(f'The number is divisible by five.')
    if num == 42 or num == 69 or num == 34:
        # 42: Douglas Adams, 69: nice, 34: rule 34 of the internet
        static_hint_list.append('The number you\'re looking for is somewhat of a meme.')
    digsum = get_digit_sum(the_number)
    static_hint_list.append(f'The digit sum of the number is {digsum}')
    return static_hint_list

# GUI related functions
def user_guess_click():
    guess = user_guess_field.get()
    logging.debug("User input: %s", str(guess))
    global tries
    tries = tries + 1
    logging.debug("Number of tries incremented to %s because user clicked", tries)
    global hints
    process_guess(guess, hints)
    
def victory_message(num) -> str:
    message = ""
    logging.info("User's guess %s is equal to our number %s", num, the_number)
    if the_number == "42":
        message = "You got it, you found the answer to everything!"
    elif the_number == "69":
        message = "You got it! Nice!"
    elif the_number == "96":
        message = "You got it! Nice (kind of)."
    elif the_number == "34":
        message = "You got it! You found the most important rule of the internet."
    elif the_number == "1":
        message = f'You got it! {the_number} is the loneliest number (and the answer).'
    elif the_number == "12":
        message = "You got it! It's a dozen."
    else:
        message = f'You got it! {the_number} is the number!'
    message += f'\nIt took you {tries} attempts!'
    logging.debug("User found the number, message generated: %s", message)
    logging.info("User guessed %s, the number was %s, user won the game in %s attempts", num, the_number, tries)
    return message

def guess_out_of_bound(guessed, hints):
    out_of_bounds_message = f'You guess {guessed} was out of bounds.'
    hints.append(out_of_bounds_message)

    hints_string = ""
    for hint in reversed(hints):
        hints_string += (" " + hint + "\n")
    output_text = "Hints:\n" + hints_string

    logging.debug("Output set to: %s", output_text)
    output_field.configure(text=output_text)

# The mega function that probably should be broken down further
def process_guess(guessed, hints):
    global lower_bound
    global upper_bound
    
    if int(guessed) < int(lower_bound) or int(guessed) > int(upper_bound):
        guess_out_of_bound(guessed, hints)
        return None
        
    # We'll need to check further below if any unique new hint has been added.
    # Therefore we remember the most recent hint here (and take into account the case that there are no hints yet)
    if len(hints) > 0:
        most_recent_hint = hints[-1]
    else:
        most_recent_hint = ["just initialized"]
    
    logging.debug("Beginning processing the guess. %s hints in hints: %s", str(len(hints)), hints)
    guessed = int(guessed)
    hints_string = ""

    if guessed == the_number:
        output_text = victory_message(the_number)
        logging.debug("output_text = \"" + str(output_text) +"\"")
        output_field.configure(text=output_text)
        return None

    # After having checked if the user guessed correctly, we now gather new hints based on the guess
    new_hints = []
    if guessed > the_number and guessed != 0:
        new_hints.append(f"The number is smaller than {guessed}")
    if guessed < the_number and guessed != 0:
        new_hints.append(f"The number is greater than {guessed}")
    sqrt_as_int = int(math.sqrt(the_number))
    logging.debug("The square root of our number %s is %s", the_number, str(sqrt_as_int))
    if guessed < sqrt_as_int:
        new_hints.append(f'Your guess {guessed} is smaller than the square root of the number!')
    if guessed > (2*the_number):
        new_hints.append(f'Your guess {guessed} is bigger than twice the number!')
    if abs(guessed - the_number) > 50:
        new_hints.append(f'Guessing {guessed} you\'re off by more than 50!')
    if abs(guessed - the_number) < 5:
        new_hints.append(f'Guessing {guessed} you\'re less than 5 off! Getting close!')
    logging.debug("%s hint(s) generated: %s", str(len(new_hints)), new_hints)
    
    for new_hint in new_hints:
        if new_hint in hints:
            new_hints.remove(new_hint)
            logging.debug("New hint removed as duplicate: %s", new_hint)
    
    for static_hint in static_hints_list:
        if static_hint in hints:
            logging.debug("Static hint not added because it would be a duplicate: %s", static_hint)
        else:
            new_hints.append(static_hint)

    # From here on out, add, sort through, sort and output hints
    # And this is the part where something isn't quite right yet
    # (still works though, so ...)
    if len(new_hints) == 1:
        hints.append(new_hints[0])
    elif len(new_hints) == 0:
        pass
    else:
        hint_nr = random.randint(0, (len(new_hints) - 1))
        hints.append(new_hints[hint_nr])
        logging.debug("New hint added to hints: %s", new_hints[hint_nr])
    
    logging.debug("Hints before output is generated: %s", hints)
    updated_hints = []
    for hint in hints:
        if hint in updated_hints:
            logging.warning("Duplicate found after composing hints: %s, removed from hints", hint)
        else:
            updated_hints.append(hint)
    hints = updated_hints
    
    no_new_hint_message = "There is no new hint to give."
    if hints[-1] == most_recent_hint:
        hints.append(no_new_hint_message)
        logging.debug("No hints have been added, therefore adding hint that there are no new hints.")
    else:
        if no_new_hint_message in hints:
            hints.remove(no_new_hint_message)

    for hint in reversed(hints):
        hints_string += (" " + hint + "\n")
    output_text = "Hints:\n" + hints_string

    logging.debug("Output set to: %s", output_text)
    output_field.configure(text=output_text)

# GUI
root = tkinter.Tk()
root.title("Number Guessing Game!")

window_width, window_height = 420, 420
screen_w, screen_h = root.winfo_screenwidth(), root.winfo_screenheight()
winpos_x, winpos_y = int(screen_w/2 - window_width/2), int(screen_h/2 - window_height/2)
root.geometry(f'{window_width}x{window_height}+{winpos_x}+{winpos_y}')

intro_text = f'Welcome to the number guessing game!\nYou will need to guess a number between {lower_bound} and {upper_bound}.'
user_guess_button_text = "Guess!"

intro_label = tkinter.Label(root, text=intro_text, font=('Helvetica bold', 12), padx=12)
user_guess_field = tkinter.Entry(root, justify="center", width="8", font=('Helvetica bold', 12), borderwidth=2, relief="solid")
user_guess_button = tkinter.Button(root, text=user_guess_button_text, font=('Helvetica bold', 12), command=user_guess_click) 
output_field = tkinter.Label(root, text="Hints:", font=('Helvetica bold', 12))

intro_label.grid(row=0, column=0, pady=5, columnspan=2)
user_guess_field.grid(row=1, column=0, padx=5, sticky="E")
user_guess_button.grid(row=1, column=1, sticky="W")
output_field.grid(row=2, column=0, pady=5, columnspan=2)

# main routine
the_number = generate_number()
print(the_number)
global static_hints_list
static_hints_list = static_hints(the_number)
root.mainloop()