import sys

full_name = sys.argv[1]

#Format the name
email = full_name.lower().replace(__old: " ", __new:".") + "company.com"

#Output
print("\n--- Your Profile")
print("Full Name:" , full_name)
print("Generated Email:",email)