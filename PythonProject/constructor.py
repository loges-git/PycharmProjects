class student:
    def __init__(self,fname,age):
        self.name = fname
        self.age = age

    def display(self):
        print(f"Name: {self.name}, Age: {self.age}")

#s1 = student(fname="Gowtham",age=33)
s1 = student("Gowtham",33)
s1.display()

class Employee:
    def __init__(self,name,aadhar):
        self.name = name #Stored once
        self.aadhar = aadhar #Stored once

    def enter_office(self):
        print(f"{self.name} Enters using Aadhar {self.aadhar}")

    def open_bank_account(self):
        print(f"Bank account opened for {self.name} with Aadhar {self.aadhar}.")

emp1 = Employee("Gowtham","1234-5678-9101")
emp1.enter_office()
emp1.open_bank_account()