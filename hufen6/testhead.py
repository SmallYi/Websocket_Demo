#http://gifshow.3agzs.com/rest/n/user/profile/v2?user=707

# gifshowusercheck = True

url = "http://gifshow.3agzs.com/rest/n/user/profile/v2"
import requests
def GetProfile(self):
    global url
    try:
        r = requests.get(url,{"user":self.user.userid})
        data = r.json()
        self.username = data["userProfile"]["profile"]["user_name"]
        self.headurl = data["userProfile"]["profile"]["headurl"]
        print(self.username,self.headurl)
    except Exception as e:
        self.username = None
        self.headurl = None
        print("getprofile_error")

