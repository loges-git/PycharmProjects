age = 15

if age >= 18:
    print("You can vote")
else:
    print("You cant vote")

marks = 75

if marks >= 90:
    print("Grade A")
elif marks >= 70:
    print("Grade B")
elif marks >= 50:
    print("Grade C")
else:
    print("Fail")


age = 18
has_license = 'NO'.upper()

if age>= 18:
    if has_license == 'Yes':
        print("You can drive")
    else:
        print("Go and take license")
else:
    print("you are too young to drive")

mark = 55
attendance = 7

if mark >= 55 or attendance >= 70:
    print("Allowed for Exams")
else:
    print("Not Allowed for Exams")

Order_amount = 1000
days = 'mon'.lower()
membership = 'gold'

if (Order_amount>=1000 and days in ['sat','sun']) or membership=='gold':
    print("20% discount")
else:
    print("no discount")