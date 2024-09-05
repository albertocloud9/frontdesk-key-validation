import qrcode
 
rooms = [ 1714, 1814, 2315, 2414 , 2512]
# Data to be encoded
for room in rooms:
    data = { "room_number": room, "building": "Foundry" }
    
    # Encoding data using make() function
    img = qrcode.make(data)
    
    # Saving as an image file
    img.save(f'{room}.png')