from pymilvus import connections, db, utility

HOST="127.0.0.1"   # 先按你服务配置改
PORT="19530"
ALIAS="t"
DB="default"

connections.connect(alias=ALIAS, host=HOST, port=PORT)
db.using_database(DB, using=ALIAS)

print("DBs:", db.list_database(using=ALIAS))
print("Collections:", utility.list_collections(using=ALIAS))
print("Has nrs2002_collection_v2:", utility.has_collection("nrs2002_collection_v2", using=ALIAS))
