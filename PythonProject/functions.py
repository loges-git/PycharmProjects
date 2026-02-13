print("Logesh".upper())
'''
def function_name():
    #code logic
'''

def great():
    print("Welcome to the function")
great()


def great(name):
    print (f"Hello {name}, Welcome")

great('Logesh')

def add(a,b):
    print(a+b)

add(1,2)

def add(a,b):
    return (a+b)

result= add (1,3)
#print(result)

#*args

def add(*args):
    total=0
    for num in args:
        total += num
        #0 += 1
        #1+= 2
        #3+= 3
        #6
    return total

print(add(1,2,3))

#######################
def create_profile(**kwargs):
    print("User Profile")
    for key,value in kwargs.items():
        print(f"{key} : {value}")


create_profile(name="Logesh", age="30",gender="M", location='chennai')

#######################
def create_profile(location="Unknown", **kwargs): #setting default fixed value as location
    print("User Profile")
    for key, value in kwargs.items():
        print(f"{key} : {value}")
    print(f"location : {location}")

create_profile(name="Logesh", age="30", gender="M", hobby="chess")

#######################
def create_profile(**kwargs):
    print("User Profile")
    for i, (key, value) in enumerate(kwargs.items(), start=1): # for adding serial number
        print(f"{i}. {key} : {value}")

create_profile(name="Logesh", age="30", gender="M")









