"""
trip = {
    "trip_id" : "UB12345",
    "pickup" : "chennai central",
    "drop" : ["Airport","Tambaram","Medavakkam"],
    "fare" : 430.75,
    "driver" : "Swetha",
    "status" : "Completed"
}

print (trip["drop"])

#print (trip["Airport"]) #cant use value. only the key can be used

print(trip.get("pickup"))
print(trip.get("Airport"))

print(trip.keys())
print(trip.values())

for key, value in trip.items():
    print(key,":",value)

trip.update({"car.model":"suzuki"})
print(trip)

trip.update({"car.model":"abc"})
print(trip)

trip.pop("status")
print(trip)

for k,v in trip.items():
    print(k,":",v)

print(trip["drop"][1])

for location in trip["drop"]:
    print(location)
 """
trips = [
    {"trip_id": "UB001", "pickup":"chennai", "drop":"Airport", "fare":430},
    {"trip_id": "UB002", "pickup":"Tambaram", "drop":"Central", "fare":320},
    {"trip_id": "UB003", "pickup":"T-Nagar", "drop":"Velachery", "fare":210}
]

for trip in trips:
    print(trip["trip_id"])

trips = {
   "UB001": {"trip_id": "UB001", "pickup":"chennai", "drop":"Airport", "fare":430},
   "UB002": {"trip_id": "UB002", "pickup":"Tambaram", "drop":"Central", "fare":320},
   "UB003": {"trip_id": "UB003", "pickup":"T-Nagar", "drop":"Velachery", "fare":210}
}

print("UB001 Fare", trips["UB001"]["fare"])

for trip_id,details in trips.items():
    print(trip_id)
    print(details["pickup"],"-->",details["drop"])

