# Creating lists for different apps

playlist = ["Shape of you","Naa Ready","Believer","Tum hi ho"]  #Spotify
favourite_foods = ["Pizza", "Burger", "Dosa", "Briyani"]        #Zomato
recent_locations = ["Home","Airport","Work","Mall"]             #Uber


print("Spotify playlist :", playlist)
print("Zomato Foods :", favourite_foods)
print("Uber locations: ", recent_locations)

#list methods

playlist.append("Oo antevva")
print (playlist)

playlist.insert(1,"kiss me")
print(playlist)

playlist.remove("Naa Ready")
print("After removing:", playlist)

playlist.pop()
print("After pop:", playlist)

playlist.reverse()
print("After reverse:", playlist)

print("Count:", playlist.count('Believer'))

#list slicing

print ("Top 2 songs", playlist[0:2])

print ("Last 2 songs", playlist[-2:])

#list iteration

for food in favourite_foods:
    print("all food ", food)

for song in playlist:
    print(song+ " By logesh")

#check if
if "Dosa" in favourite_foods:
    print("yes")

favourite_foods[1]='shawarma'
print(favourite_foods)

#########################
mixed = ["Logesh","30",5.5]

for a in mixed:
    print(a)

#########################
recent_locations = ["Home","Airport","Work","Mall"]             #Uber

for i, location in enumerate(recent_locations):
    print(f"location {i}: {location}")

#########################
recent_locations = ["Home","Airport","Work","Mall"]             #Uber

for i, location in enumerate(recent_locations,start=1):
    print(f"location {i}: {location}")