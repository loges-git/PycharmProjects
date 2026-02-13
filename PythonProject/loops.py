name = ["Swetha","Safi","Logesh","Faisal","Prashanth"]

for i in name:
    print(i.upper())

correct_pin = '1234'
entered_pin=''

while entered_pin != correct_pin:
    entered_pin=input("Enter your correct pin: ")
print("Access granted")

for i in range (10):
    print(i)

for i in range (10):
    if i==5:
        break
    print(i)

names=[1,2,3,4,8,6,7,5,9,10]
for i in names:
    if i==5:
        break
    print(i)


n = [10,-5,7,-9,11]

for num in n:
    if num <0:
        continue
    print(num)

n = [10,-5,7,-9,11]

for num in n:
    pass #future logic implementation

count = 5
while count > 0:
    print(f"countdown: {count}")
    count -= 1

print("Time's up!")


items = []

while True:
    item = input("Add item (type 'done' to finish): ")
    if item.lower() == "done":
        break
    items.append(item)

print("items in cart:", items)