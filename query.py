
class E_waste:
    def __init__(self, collection_point, type, location, postal_code,
                 information):
        self.collection_point = collection_point
        self.type = type
        self.location = location
        self.postal_code = postal_code
        self.information = information

    @staticmethod
    def from_dict(source):
        e_waste = E_waste(source[u'collection_point'], source[u'type'],
                          source[u'location'], source[u'postal_code'],
                          source[u'information'])

        if u'collection_point' in source:
            e_waste.collection_point = source[u'collection_point']
        if u'type' in source:
            e_waste.type = source[u'type']
        if u'location' in source:
            e_waste.location = source[u'location']
        if u'postal_code' in source:
            e_waste.postal_code = source[u'postal_code']
        if u'information' in source:
            e_waste.information = source[u'information']
        return e_waste

    def to_dict(self):
        obj = {
            u'collection_point': self.collection_point,
            u'type': self.type,
            u'location': self.location,
            u'postal_code': self.postal_code,
            u'information': self.information
        }

        if self.collection_point:
            obj[u'collection_point'] = self.collection_point
        if self.type:
            obj[u'type'] = self.type
        if self.location:
            obj[u'location'] = self.location
        if self.postal_code:
            obj[u'postal_code'] = self.postal_code
        if self.information:
            obj[u'information'] = self.information

        return obj

    def __repr__(self):
        return(
            f'e_waste(\
                collection_point={self.collection_point}, \
                type ={self.type}, \
                location={self.location}, \
                postal_code={self.postal_code}, \
                information={self.information}\
            )'
        )


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
        messages.insert(count, str(count) +". " + bin.collection_point + "\n\n Location: "  + bin.location + " " + str(bin.postal_code) +"\n\n " + bin.information + "\n")
        count += 1
    return messages


