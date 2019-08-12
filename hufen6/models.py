from django.db import models
import django.utils.timezone as timezone
from ksuser.models import User
# Create your models here.
#互粉列表
class HufenHistory(models.Model):
    HufenId = models.CharField("互粉编号",unique=True, default="0_0", max_length=128)
    # ID小的在前
    user1 = models.ForeignKey(User,related_name="User1") # user1_id db_index=True
    user2 = models.ForeignKey(User,related_name="User2") # user2_id
    state = models.IntegerField("匹配状态", default=0)
    #0-匹配超时 1-匹配成功 2-双方不一致 3-服务器故障 4-互粉中主动终止 5-成功后取关
    bguser = models.ForeignKey(User,related_name="Bguser")
    errinfo = models.CharField("异常信息", default="NoError", max_length=256)
    hftime = models.DateTimeField("记录时间",default = timezone.now)

#取关列表
class CancleHf(models.Model):
    CancelId = models.CharField("取关编号", unique=True, default="0_0", max_length=128)
    # 被取关的在前
    state = models.IntegerField("取关状态", default=0)
    # 0-被取关用户还未去取关对方 1-被取关用户已取关对方
    user = models.ForeignKey(User,related_name="UserDo") #被取关用户
    cancle_user = models.ForeignKey(User,related_name="UserCancel") #取关用户
    cancel_time = models.DateTimeField("取关时间",default = timezone.now)


class UserHeadProfile(models.Model):
    user = models.ForeignKey(User,related_name="UserHead") #被取关用户
    name = models.CharField("用户名",max_length=128)
    headurl = models.CharField("头像链接",max_length=256)
