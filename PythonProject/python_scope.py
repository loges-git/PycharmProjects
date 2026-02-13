#L --> E --> G --> B
#L-> LOCAL, E -> ENCLOSING , G -> GLOBAL, B -> BUILT-IN
from idlelib.pyshell import usage_msg


#L

def order():
    food="Curd Rice"
    print(food)

order()

##print(food) cant be called outside the function

#E
#inner function can use the outer function variable -> parent function and child function -> its called enclosing
def card():
    discount=10 #E

    def checkout():
        print("Applying discount :" , discount)

    checkout()

card()

#G

user_id ='Logesh'

def homepage():
    print("Welcome:" , user_id)

def profile():
    print("Welcome to the profile page:" , user_id)

homepage()
profile()

#B

print(__file__)