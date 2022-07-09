import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("test-6d84c-firebase-adminsdk-qknug-c08468824e.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
data = {
    u'item': u'plastic food container',
    u'info': u'Plastic food containers can be recycled! Do note to empty and rinse it before recycling!',
    u'bluebin': True,
    u'keywords': [u'plastic', u'cup', 'container', 'food', 'takeaway']
}

# Add a new doc in collection 'cities' with ID 'LA'
db.collection(u'recycling-information').document(u'clothes hanger').set(data)