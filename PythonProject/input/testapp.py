import sys

#adding check condition to validate the argv

if len(sys.argv) ==2:
    print("Usage : python email_generator.py 'Full name and last name'")
    sys.exit()

# Get full name from command line argument
full_name = sys.argv[1]
last_name = sys.argv[2]

# Format the name into an email
email = full_name.lower().replace(" ", ".") +last_name+ "@company.com"

# Output
print("\n--- Your Profile")
print("Full Name:", full_name+last_name)
print("Generated Email:", email)

#scheduler will get the input from either database, frontend or file
