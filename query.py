

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
    no_bins_message = 'We could not find any e-waste bins near you :('
    sector = postal_code[:2]
    e_waste_collection = db.collection(u'e-wasteLocations').document(sector).collection(sector)
    docs = e_waste_collection.stream()
    url = "https://www.google.com/maps/place/"
    count = 1
    messages = []
    messages.append(message)
    new_postalcode = ''

    for doc in docs:
        bin = E_waste.from_dict(doc.to_dict())
        full_url = url
        if len(str(bin.postal_code)) == 5:
            new_postalcode = "0" + str(bin.postal_code)
        location_placeholder = bin.location
        location_url = location_placeholder.split(",")
        full_url += "+" + location_url[0] + "+" + new_postalcode
        location_placeholder = location_placeholder + " " + new_postalcode
        full_url = full_url.replace(",", "")
        messages.insert(count, str(count) +". " + bin.collection_point + "\n\n Location: "  + f"<a href='{full_url}'>{location_placeholder}</a>" + "\n\n " + bin.information + "\n")
        count += 1
    if count == 1:
        messages = []
        messages.insert(0, no_bins_message)
    return messages


