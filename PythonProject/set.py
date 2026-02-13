uber_cities=["chennai","bangalore","chennai","delhi","bangalore"]

unique_cities=set(uber_cities)
print(unique_cities)

uber_cities1={"chennai","mumbai","bangalore"}
uber_cities2={"bangalore","delhi","hyderabad"}\

print(uber_cities1.union(uber_cities2))
print(uber_cities1.intersection(uber_cities2))

print(uber_cities2.difference(uber_cities1))
print(uber_cities1.difference(uber_cities2))

uber_cities1.add("karur")
print(uber_cities1)

uber_cities1.remove('chennai')
print(uber_cities1)

#print(uber_cities1[1]) --> index wont work

my_set={1,2,3}
print(my_set)
my_set.remove(2)
my_set.add(99)
print(my_set)
my_set.discard(8) # to remove safely without error// will delete 8 only if its avail
print(my_set)