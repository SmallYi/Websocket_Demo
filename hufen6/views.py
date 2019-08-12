from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ksuser.models import User
from hufen.models import HufenHistory,CancleHf,UserHeadProfile
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from django.core.paginator import Paginator  #后台分页
import base64

# Create your views here.
@csrf_exempt
@login_required(login_url="/kslogin?next=user/profile")
def getuser(request):
    if request.method == "POST":
        ##下面4行代码仅限调试使用

        # id = request.POST.get("id")
        # if id:
        #     user = User.objects.get(userid=id)
        #     auth.login(request, user)
        #     return JsonResponse({"sessionid": request.session._session_key})
        # else:
        sessionid = request.COOKIES["sessionid"]
        return JsonResponse({"sessionid":sessionid})


@login_required(login_url="/kslogin?next=user/profile")
def hall(request):
    return render(request,"hufen/hall2.html",)

@login_required(login_url="/kslogin?next=user/profile")
def list(request):
    sucobjs1 = HufenHistory.objects.filter(user1=request.user,state=1)
    sucobjs2 = HufenHistory.objects.filter(user2=request.user, state=1)
    canobjs = CancleHf.objects.filter(user=request.user,state=0)
    faiobjs1 = HufenHistory.objects.filter(user1=request.user).exclude(state=1)
    faiobjs2 = HufenHistory.objects.filter(user2=request.user).exclude(state=1)
    return render(request,"hufen/list.html",{"sucobjs1":sucobjs1,"sucobjs2":sucobjs2,"canobjs":canobjs,"faiobjs1":faiobjs1,"faiobjs2":faiobjs2})

@csrf_exempt
@login_required(login_url="/kslogin?next=user/profile")
def cancel(request):
    # 获取自身uid和被取关用户otherid
    print(request.POST)
    if request.method == "POST":
        otherid = int(request.POST.get("otherid", "0"))
        userid = request.user.userid
        user = request.user
        otheruser = User.objects.filter(userid=otherid).first()
        if userid < otherid:
            first = user
            second = otheruser
        else:
            first = otheruser
            second = user
    # first 是id 小的用户
    # 写入取关表
    HufenID = str(first.userid) + '_' + str(second.userid)
    CancleID = str(otheruser.userid) + "_" + str(user.userid)
    ClearID = str(user.userid) + "_" + str(otheruser.userid)
    if not CancleHf.objects.filter(CancelId=CancleID).first():
        CancleHf.objects.create(CancelId=CancleID, user=otheruser, cancle_user=user,state=0)
    if CancleHf.objects.filter(CancelId=ClearID).first():
        CancleHf.objects.filter(CancelId=CancleID).update(state=1)
        CancleHf.objects.filter(CancelId=ClearID).update(state=1)
    # 写入互粉历史 状态为5
    if HufenHistory.objects.filter(HufenId=HufenID).first():
        HufenHistory.objects.filter(HufenId=HufenID) \
            .update(user1=first, user2=second,state=5, bguser=otheruser)

    return JsonResponse({})

@csrf_exempt
@login_required(login_url="/kslogin?next=user/profile")
def suclist(request):
    if request.method == "POST":
        info = []
        state = request.POST.get('state',0)

        # suc
        if int(state) == 1:
            sucobjs1 = HufenHistory.objects.filter(user1=request.user,state=1)
            sucobjs2 = HufenHistory.objects.filter(user2=request.user, state=1)

            for obj in sucobjs1:
                otherobj = UserHeadProfile.objects.filter(user=obj.user2).first()
                if otherobj:
                    name = base64.b64decode(otherobj.name)
                    print(str(name,'utf-8'))
                    info.append({"userid":otherobj.user.userid,"username":str(name,'utf-8'),"headurl":otherobj.headurl})
            for obj in sucobjs2:
                otherobj = UserHeadProfile.objects.filter(user=obj.user1).first()
                if otherobj:
                    name = base64.b64decode(otherobj.name)
                    print(str(name,'utf-8'))
                    info.append({"userid": otherobj.user.userid, "username": str(name,'utf-8'), "headurl": otherobj.headurl})
        # cel
        elif int(state) == 2:
            canobjs = CancleHf.objects.filter(user=request.user, state=0)
            for obj in canobjs:
                otherobj = UserHeadProfile.objects.filter(user=obj.cancle_user).first()
                if otherobj:
                    name = base64.b64decode(otherobj.name.encode('utf-8'))
                    print(str(name,'utf-8'))
                    info.append({"userid": otherobj.user.userid, "username": str(name,'utf-8'), "headurl": otherobj.headurl})
        # fai
        elif int(state) == 3:
            faiobjs1 = HufenHistory.objects.filter(user1=request.user).exclude(state=1)
            faiobjs2 = HufenHistory.objects.filter(user2=request.user).exclude(state=1)
            for obj in faiobjs1:
                otherobj = UserHeadProfile.objects.filter(user=obj.user2).first()
                if otherobj:
                    name = base64.b64decode(otherobj.name.encode('utf-8'))
                    print(str(name,'utf-8'))
                    info.append({"userid":otherobj.user.userid,"username":str(name,'utf-8'),"headurl":otherobj.headurl})
            for obj in faiobjs2:
                otherobj = UserHeadProfile.objects.filter(user=obj.user1).first()
                if otherobj:
                    name = base64.b64decode(otherobj.name.encode('utf-8'))
                    print(str(name,'utf-8'))
                    info.append({"userid": otherobj.user.userid, "username": str(name,'utf-8'), "headurl": otherobj.headurl})
        else:
            print("state error")
            return JsonResponse({"pageinfo": [], "error": 1})
        info = sorted(info, key=lambda d: d["userid"],reverse=True)

        limit = 10

        if len(info):
            paginator = Paginator(info, limit)  # 每页两条数据 
            page = request.POST.get('page',1)  # QueryDict objects,如果没有对应的page键，就返回默认1。 
            if 0 < int(page) <= paginator.num_pages:
                error = 0
                pageinfo = paginator.page(page).object_list  # 根据索引page，返回该page数据，如果不存在，引起 InvalidPage异常 
                print(pageinfo)
            else:
                print("页码不符合要求")
                pageinfo = []
                error = 1
        else:
            print("没有数据")
            pageinfo = []
            error = 1
        return JsonResponse({"pageinfo": pageinfo,"error":error})

