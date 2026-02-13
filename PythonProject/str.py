driver_name = 'logesh r'
print(driver_name.lower())
print(driver_name.upper())
print(driver_name.capitalize())

##################################
mobile = "8667020280"
masked = mobile[:2] + "******" + mobile[-2:-1] + "*"
#masked=mobile[-6:-4]
#[from:to]
print(masked)

##################################
song = "shape OF you"
Artist = "LOGESH ramaIYA"

formatted=f"{song.title()} - {Artist.title()}"
print(song.title() + '-' + Artist.title())
print(formatted)

##################################
location = "Chennai central"
fixed_location = location.replace("Chennai central","Tambaram")
print(fixed_location)

##################################
message = "your uber booking id is: UB12345. Please keep it safe"
booking_id = message.split(":")[1].split(".")[0].strip() #[1] -> means after the : #[0] means before the :
print(booking_id)

##################################
promo_msg="use zomato100 to get 100 off on your first order"
if "zomato100" in promo_msg:
    print("offer applied")

##################################
feedback = "the driver was polite and the ride was smooth"
print ("position is :", feedback.find("polite"))

##################################
name = "logesh ramaiya"
initials = "".join([word[0].upper() for word in name.split()])
print (initials)

##################################
dirty_input = "       airport   "
clean=dirty_input.strip()
print(clean)

##################################
word1="the trip was amazing and the car was clean"
word_count=word1.split()
print(word_count)

##################################
word1="the trip was amazing and the car was clean"
word_count=len(word1.split())
print(word_count)

##################################
word1 = "the trip was amazing and the car was clean"
print(", ".join(f"'{ch}'" for ch in word1))

##################################
word1 = "the trip was amazing and the car was clean"
words = word1.split()

# Create a dictionary of word counts
word_count = {}
for w in words:
    word_count[w] = word_count.get(w, 0) + 1

print(word_count)

