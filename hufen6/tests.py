from django.test import TestCase

# Create your tests here.
import sys,os
sys.path.append("/home/ksht/") #windows环境不用管 linux是应用的路径
os.environ['DJANGO_SETTINGS_MODULE'] = 'ksht.settings'  # 项目的settings
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
from hufen.models import HufenHistory
from ksuser.models import User

Users = []

def makeuser(start,end):
    for i in range(start,end):
        if not User.objects.filter(userid=i).first():
            User.objects.create(userid=i,integral=i,credit=i,username=str(i))
        user = User.objects.filter(userid=i).first()
        if user not in Users:
            Users.append(user)

def main():

    HufenList = []
    for user1 in Users:
        for user2 in Users:
            if user1.userid < user2.userid:
                first = user1
                seconf = user2
            elif user1.userid > user2.userid:
                first = user2
                second = user1
            else:
                break
            ID = str(first.userid) + '_' + str(second.userid)

            hufen = HufenHistory(HufenId=ID,user1=first,user2=second,state=0,bguser=first)
            HufenList.append(hufen)
            if len(HufenList) > 10000:
                HufenHistory.objects.bulk_create(HufenList)
                HufenList.clear()
                print("write 10000")

def HufenRate(user):
    # 匹配总次数
    totaltime = HufenHistory.objects.filter(user1=user).count() + \
                     HufenHistory.objects.filter(user2=user).count()
    # 互粉成功次数
    suctime = len(HufenHistory.objects.filter(user1=user, state=1)) + \
              len(HufenHistory.objects.filter(user2=user, state=1))
    if totaltime:
        sucrate = float(suctime / totaltime)
    else:
        sucrate = 0
    print("user:" + str(user.userid) + "totaltime:" + str(totaltime))
    # HufenHistory.objects.bulk_create(HufenList)


# if __name__ == "__main__":
#     makeuser(1415,1570)
#     main()
#     print('Done!')
# obj = HufenHistory.objects.get(id=500000)
# first =obj.user1
# second = obj.user2
# User.objects.create(userid=int(4582),integral=200,credit=100,username=str(4567))
# User.objects.create(userid=int(123),integral=200,credit=100,username=str(4568))
first = User.objects.filter(userid=4567).first()
second = User.objects.filter(userid=4568).first()
from django.utils import timezone



start = timezone.now()
# for i in range(1,101):
#     for i in range(1,100):
HufenRate(first)
HufenRate(second)
ID = str(first.userid) + '_' + str(second.userid)
HufenHistory.objects.filter(HufenId=ID).exists()
# HufenHistory.objects.filter(user1=first,user2=second).exists()
print("time:" + str((timezone.now() - start).total_seconds()))


