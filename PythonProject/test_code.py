delivery_partner='Swiggy'

def hotel():
    item='Pizza'

    def order_now():
        quantity =2
        print (f"ordering {quantity} {item} using {delivery_partner}")
        print ("Ordering ", quantity, item, "using" , delivery_partner)

    order_now()

hotel()

print (delivery_partner)

print (__file__)