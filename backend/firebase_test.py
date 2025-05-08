import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase-config.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# Test write
doc_ref = db.collection("test").document("testdoc")
doc_ref.set({"test": "success"})

# Test read
doc = doc_ref.get()
print(f"Test result: {doc.to_dict()}")