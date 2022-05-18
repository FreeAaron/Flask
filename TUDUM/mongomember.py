#from asyncio.windows_events import NULL
from asyncio.windows_events import NULL
import random, string
from importlib_metadata import NullFinder
from matplotlib import collections
from matplotlib.collections import Collection
from numpy import sort
import pymongo
from urllib.parse import quote_plus
from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId
from flask import render_template
#----------------基礎設置--------------#
account = __password = client = memberdb = usercollection =cscollection= 0
#連線到資料庫
def init():
    global account,__password,client,memberdb,usercollection,cscollection
    account= quote_plus("peach")
    __password=  quote_plus("Ss123456")
    client = pymongo.MongoClient("mongodb+srv://"+ account + ":" + __password + "@mycluster.5y8sq.mongodb.net/MembersData?retryWrites=true&w=majority")
    # client = pymongo.MongoClient("mongodb://localhost:27017")
    
    #選擇資料庫memberdb
    memberdb = client.members
    #選擇集合users
    usercollection = memberdb.users
    #選擇集合 csdb (comments and stars)
    cscollection = memberdb.cs
    print("已連線資料庫")
init()
print(usercollection)
#資料放入集合中
#----------------單一方法--------------#
#找一筆會員資料
def getadatabyid(id):
    objid = id
    userdata = usercollection.find_one(ObjectId(objid))
    print("username:",userdata["username"])

def getaexistbyusername(username):
    result = usercollection.find_one({"username":username})
    if result!= None:
        print("user帳號存在")
        return True #帳號已存在
    else: return False
#回傳一些會員東西
def getadatabyusername(uname):
    result = usercollection.find_one({"username":uname})
    return result
#新增一筆會員
def newamember(username,password,nick,useremail,age,gender,level):
    if not getaexistbyusername(username):
        if gender==0:
            gender ="male"
        elif gender==1:
            gender ="female"
        elif gender=="male" or gender=="female":pass
        else:print("性別不正確")
        if level==None:
            level=1
        result = usercollection.insert_one({
            "username":username,
            "password":password,
            "nickname":nick,
            "useremail":useremail,
            "age":age,
            "gender":gender,
            "level":level
        })
        print("資料新增成功")
        #print(result.inserted_id)
        return True
    else:
        return False

#newamember("admin02","super","芒果","test@mail","25",1,100)

#所有會員資料
def getalldata():
    cursor = usercollection.find()
    for data in cursor:
        print("%s等級是%s"%(data["nickname"], data["level"]))

#更新單筆會員資料
def setupdatedata(username,num,newdata):
    if num==1: #更password
        result = usercollection.update_one({"username":username},
        {"$set":{"password":newdata}
        })
    elif num==2: #更暱稱
        result = usercollection.update_one({"username":username},
        {"$set":{"nickname":newdata}
        })
        #說明
        #"$set" = 直接覆蓋 "$inc" = 加值"level":2 "$mul" = 乘值 "$unset":{"name"} 清除欄位 "$and":[]/ "$or":[] 多重條件篩選
        print("有%d筆資料符合需求"%result.matched_count)
        print("已完成%d筆資料的更新"%result.modified_count)
    else:
        print("需求不正確")
def setlevelup(username):
    lvup = usercollection.update_one({"username":username},
    {
        "$inc":{
            "level":1
        }
    })
    lv = usercollection.find_one({"username":username})
    print("%s已經升級,%d筆資料異動,目前等級是:"%(username,lvup.modified_count),lv["level"])

def setdelete_onedata(username):
    result = usercollection.delete_one({"username":username})
    print("刪了:",result.deleted_count,"筆")
#異動多筆會員資料
def setdelete_manydatas(level):
    lv = int(level)
    result = usercollection.delete_many({"level":lv})
    print("刪了:",result.deleted_count,"筆")

#getadata("6264159f953e381ee6b88f2e")
#getalldata()
#setupdatedata("admin",2,"可愛的管理員")
#setlevelup("peach")
#setdelete_onedata("hi")
#setdelete_manydatas(3)
#----------------------------------------#
#隨便製造一些會員用戶#隨機
def randomamenber():
    for i in range(1,11):
        raneng = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        ranch =random.randint(0x4e00, 0x9FA5)
        ranlv =random.randint(1,10)
        ranage=random.randint(18,30)
        rangen = random.randint(0,1)
        newamember(raneng,"super",chr(ranch),"",ranage,rangen,ranlv)
#randomamenber()

#排序篩選會員
def setlistallsort():
    cursor = usercollection.find({},sort=[ ("level", pymongo.ASCENDING) ] )
    for i in cursor:print(i["nickname"],"level",i["level"])
#setlistallsort()

#複合篩選 
#會員可否登入
def login(username,password):
    if usercollection.find_one({
        "$and":[
            {"username":username},
            {"password":password},
        ]}):
            return True
    else:
        return False
#login("peach","super")

#篩選會員結果
def setresult():
    cursor = usercollection.find({
        "$or":[{"level":2},{"username":"admin"}]
    } , sort=[("level",pymongo.ASCENDING)])
    for c in cursor:
        print(c)
#setresult()

#------------------------評論與喜好--------------------------#
#添加編號至會員的收藏清單
def setUsercollectList(username, movieid,cancel=False):
    if not getaexistbyusername(username):  #先確認的確有此會員
        return 0
    #userdb = cscollection.find_one({"username":username}) 

    #此會員收藏東西(但不能重複收藏)
    if cscollection.find_one({
        "$and":[
            {"username":username},
            {"collect":movieid},
        ]}):
            if(cancel == True):
                #懶得做
                return 0 #取消收藏
            return 1 #早就收藏過拉
    else:
        cscollection.insert_one({
            "username":username,
            "collect":movieid
        })#增加id到收藏清單
        return 2 #加入收藏

# setUsercollectList("test","1345")
# setUsercollectList("test","4576")
# setUsercollectList("test","4567")

#印出會員所收藏的
def getUserStar(username):
    if not getaexistbyusername(username):  #先確認的確有此會員
        return 0
    cursor = cscollection.find()
    collect =[]
    for data in cursor:
        if data["username"] == username:
            print("您所收藏的東西有%s" %(data["collect"]))
            collect.append(data["collect"])
    return collect
#getUserStar("test")

#會員按星星
def setUserStar(username, movieid, star):
    if not getaexistbyusername(username):  #先確認的確有此會員
        return 0
 
    # cscollection.insert_one({
    #     "username":username,
    #     "collect":movieid,
    #     "star":star
    # })
       #找
    filter = { "$and":[
            {"username":username},
            {"collect":movieid},
        ] }
    # Values to be updated.
    newvalues = { "$set" : { "star" : star } }
    p =cscollection.find_one(filter)
    if p:
        print(p)
        print("評分有被更動")
        cscollection.update_one(filter, newvalues)
    else:
        print("user並沒有收藏該電影")
   
    
setUserStar("test",2000,5)

#找所有符合該條件的 蒐集該內容
# find = "note1"

# curs = collection.find({"name":find}, {"content":True, "_id":False})

# for item in curs:
#   print(item)


#查看會員的收藏編號清單
def getUsercollectdList(username):
    data = cscollection.find_one({"username":username})
    print(data["collect"])
    return data["collect"] #回傳收藏清單