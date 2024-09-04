import qrcode
 
# Data to be encoded
data = { "room_number": 2514, "building": "Foundry" }
 
# Encoding data using make() function
img = qrcode.make(data)
 
# Saving as an image file
img.save('2415.png')