from operator import truediv

x = 5+10
print(x)

a=10
b=3

#Arithmetic
print(a+b)
print(a-b)
print(a*b)
print(a/b)
print(a%b)
print(a**b) #10*10*10
print(a // b)

#Comparison

x=5
y=10

print(x==y)
print(x!=y)
print(x>y)
print(x<y)

#Logical

g=True
v=False

print(g and v)
print(g or v)
print (not g)


#Going to do a billing calculation by adding 18% tax and discounts

amount = 1200
tax = amount * 0.18
total = amount+tax
print(total)
if total > 1000 :
    discount = total * 0.10
    total -= discount

print(total)

#Going to give discounts to whom having age greater or equal to 60 or student

age = 65
student = 'yes'
'''
if age >= 60 or student == 'yes': # this is a conditional block
    print("yes discount")
else:
    print("no discount")
'''

"""
commenting
"""