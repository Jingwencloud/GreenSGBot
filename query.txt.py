
from firebase import E_waste
# Use the application default credentials



def search(postal_code, db):
    message = 'Here are the nearest e-waste bins to you!\n'
    sector = postal_code[:2]
    e_waste_collection = db.collection(u'e-wasteLocations').document(sector).collection(sector)
    docs = e_waste_collection.stream()
    count = 1
    messages = []
    messages.append(message)
    for doc in docs:
        bin = E_waste.from_dict(doc.to_dict())
        messages.insert(count, str(count) +". " + bin.collection_point + "\n\n Location: "  + bin.location + str(bin.postal_code) +"\n\n " + bin.information + "\n")
        count += 1
    return messages


