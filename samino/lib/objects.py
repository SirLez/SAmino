# By A7rf - Rewrited again by SirLez - Rewrited again by Bovonos ._. - Rewrited again by SirLez ,_,
# SirLez: I know there is no property func

class Login:
    def __init__(self, data):
        self.json = data
        self.uid = data['auid']
        self.sid = data['sid']
        self.nickname = data['account']['nickname']
        self.aminoId = data['account']['aminoId']

class Jar():
    def __init__(self, fill_level: float = 0.0, data: dict = {}) -> None:
        if not data: self.fill_level: float = fill_level
        self.fill_level: float = len(data) / 10
    
class CumJar(Jar):
    def cum_in_jar(self, amount: float) -> None:
        self.fill_level += amount
        
    def clear_jar(self) -> bool:
        if self.fill_level > 0.50: raise NotImplementedError("Jar too dirty")
        self.fill_level = 0.0
        return True


class AccountInfo:
    def __init__(self, data):
        self.json = data
        self.time = data['modifiedTime']
        self.email = data['email']
        self.aminoId = data['aminoId']
        self.cumjar = CumJar()

class MyCommunitys:
    def __init__(self, data):
        self.json = data
        self.name = []
        self.comId = []

        for o in data:
            self.name.append(o['name'])
            self.comId.append(o['ndcId'])


class MyChats:
    def __init__(self, data):
        self.json = data
        self.chatId = []
        self.title = []

        for o in data:
            self.chatId.append(o['threadId'])
            self.title.append(o['title'])


class ChatInfo:
    def __init__(self, data):
        self.json = data
        self.chatId = data["chatId"]
        self.title = data["title"]


class Link:
    def __init__(self, data):
        self.json = data
        try: self.comId = data["linkInfo"]['ndcId']
        except (KeyError): self.comId = data["community"]["ndcId"]
        try: self.objectId = data["linkInfo"]['objectId']
        except (KeyError): self.objectId = None


class UserList:
    def __init__(self, data):
        self.json = data
        self.userId = []
        self.nickname = []
        self.icon = []

        for o in data:
            self.userId.append(o['uid'])
            self.nickname.append(o['nickname'])
            self.icon.append(o['icon'])


class Visitors:
    def __init__(self, data):
        _profile = []
        self.json = data

        for o in data: self.visitTime.append(o['visitTime'])
        for o in data:
            o = o["profile"]
            try: _profile.append(o)
            except: _profile.append(None)

        self.profile: UserList = UserList(_profile)
        self.aminoId = []
        self.nickname = []
        self.userId = []
        self.visitTime = []
        self.visitorsCount = data['visitorsCount']
        self.lastVisit = data['lastCheckTime']


class Comment:
    def __init__(self, data):
        _author = []
        self.json = data

        for o in data:
            try: _author.append(o["author"])
            except (KeyError, TypeError): _author.append(None)

        self.author: UserList = UserList(_author)
        self.commentId = []
        self.content = []

        for x in data:
            self.commentId.append(x['commentId'])
            self.content.append(x['content'])


class ChatMessages:
    def __init__(self, data):
        _author = []
        self.json = data

        for o in data:
            try: _author.append(o["author"])
            except (KeyError, TypeError): _author.append(None)

        self.author: UserList = UserList(_author)
        self.messageId = []
        self.content = []
        self.clientRefId = []
        self.userId = []

        for x in data:
            self.messageId.append(x['messageId'])
            self.content.append(x['content'])
            self.clientRefId.append(x['clientRefId'])


class UserInfo:
    def __init__(self, data):
        self.json = data
        try: self.createdTime = data['createdTime']
        except (KeyError): self.createdTime = None
        try: self.userId = data['uid']
        except (KeyError): self.userId = None
        try: self.icon = data['icon']
        except (KeyError): self.icon = None
        try: self.content = data['content']
        except: self.content = None
        try: self.nickname = data['nickname']
        except (KeyError): self.nickname = None


class Message:
    def __init__(self, data):
        self.json = data
        try: self.userId = data["uid"]
        except (KeyError): self.userId = None
        try: self.messageId = data['messageId']
        except (KeyError): self.messageId = None
        try: self.content = data['content']
        except (KeyError): self.content = None
        try:  self.clientRefId = data['clientRefId']
        except (KeyError): self.clientRefId = None
        try: self.author: UserInfo = UserInfo(data["author"])
        except (KeyError): self.author: UserInfo = UserInfo([])
        try: self.replyMessage: ReplyMessage = ReplyMessage(data["extensions"]["replyMessage"])
        except (KeyError): self.replyMessage: ReplyMessage = ReplyMessage({})
        try: self.chatId = data["threadId"]
        except (KeyError): self.chatId = None


class Community:
    def __init__(self, data):
        self.json = data
        self.content = data['content']
        self.themePack = data['themePack']


class CoinsHistory:
    def __init__(self, data):
        self.json = data
        self.uid = []
        self.title = []
        self.ip = []
        data = data['coinHistoryList']

        for x in data:
            try: self.uid.append(x['uid'])
            except: self.uid.append(None)
            try: self.ip.append(x['extData']['sourceIp'])
            except: self.ip.append(None)
            try: self.title.append(x['extData']['subtitle'])
            except: self.title.append(None)


class WalletInfo:
    def __init__(self, data):
        self.json = data
        self.coins = data['totalCoins']
        self.adsFlags = data['adsFlags']


class IdInfo:
    def __init__(self, data):
        self.json = data
        self.shortUrl = data['shareURLShortCode']


class Json:
    def __init__(self, data):
        self.json = data


class BlogInfo:
    def __init__(self, data):
      self.json = data
      self.title = data["title"]
      self.content = data["content"]

      self.author: UserInfo = UserInfo(data["author"])


class BlogList:
    def __init__(self, data):
      _author = []
      self.json = data

      for o in data:
        try: o = o["refObject"]
        except (KeyError): pass
        _author.append(o["author"])

      self.blogId = []
      self.title = []
      self.content = []

      for o in data:
        try: o = o["refObject"]
        except (KeyError): pass
        try: self.blogId.append(o["blogId"])
        except KeyError: self.blogId.append(o["itemId"])
        else: pass
        self.title.append(o["title"])
        self.content.append(o["content"])

      self.author: UserList = UserList(_author)


class BlogListAll:
    def __init__(self, data):
      _author = []
      self.json = data

      for o in data:
        try: o = o["refObject"]
        except (KeyError): pass
        _author.append(o["author"])

      self.blogId = []
      self.title = []
      self.content = []

      for o in data:
        try: o = o["refObject"]
        except (KeyError): pass
        try: self.blogId.append(o["blogId"])
        except KeyError: self.blogId.append(o["itemId"])
        else: pass
        try: self.title.append(o["title"])
        except KeyError: self.title.append(o["label"])
        else: pass
        try: self.content.append(o["content"])
        except KeyError: pass

      try: self.author: UserList = UserList(_author)
      except (KeyError): self.author: UserList = UserList({})


class ReplyMessage:
    def __init__(self, data):
        try: self.messageId = data['messageId']
        except (KeyError): self.messageId = None
        try: self.content = data['content']
        except (KeyError): self.content = None
        try:  self.clientRefId = data['clientRefId']
        except (KeyError): self.clientRefId = None
        try: self.author: UserInfo = UserInfo(data["author"])
        except (KeyError): self.author = None
        try: self.replyMessage: ReplyMessage = ReplyMessage(data["extensions"]["replyMessage"])
        except (KeyError): self.replyMessage = None


class Payload:
    def __init__(self, data):
        self.json = data
        self.ndcId = data["ndcId"]
        self.chatId = data["tid"]
        try: self.alert = data["aps"]["alert"]
        except (KeyError): self.alert = None


class Event:
    def __init__(self, data):
        self.json = data
        try: self.ndcId = data["ndcId"]
        except (KeyError): self.ndcId = None
        try: self.payload: Payload = Payload(data["payload"])
        except (KeyError): self.payload = None
        try: self.message: Message = Message(data["chatMessage"])
        except (KeyError): self.message: Message = Message(data)


class JoinRequests:
    def __init__(self, data):
        self.json = data
        try: self.requestsCount = self.json["communityMembershipRequestCount"]
        except (KeyError): self.requestsCount = None
        self.requestId = []
        self.comId = []
        self.userId = []
        self.nickname = []
        self.icon = []
        self.message = []
        self.role = []
        for x in self.json["communityMembershipRequestList"]:
            try: self.requestId.append(x["requestId"])
            except (KeyError): self.requestId.append(None)
            try: self.comId.append(x["ndcId"])
            except (KeyError): self.comId.append(None)
            try: self.userId.append(x["applicant"]["uid"])
            except (KeyError): self.userId.append(None)
            try: self.nickname.append(x["applicant"]["nickname"])
            except (KeyError): self.nickname.append(None)
            try: self.icon.append(x["applicant"]["icon"])
            except (KeyError): self.icon.append(None)
            try: self.message.append(x["message"])
            except (KeyError): self.message.append(None)
            try: self.role.append(x["applicant"]["role"])
            except (KeyError): self.role.append(None)


class CommunityStats:
    def __init__(self, data):
        self.json = data
        self.dailyActiveMembers = data["dailyActiveMembers"]
        self.monthlyActiveMembers = data["monthlyActiveMembers"]
        self.totalTimeSpent = data["totalTimeSpent"]
        self.totalPostsCreated = data["totalPostsCreated"]
        self.newMembersToday = data["newMembersToday"]
        self.totalMembers = data["totalMembers"]


configs = []
class BubbleConfig:
    def __init__(self, data):
        self.configs = configs
        self.json = data
        self.allowedSlots = []
        self.name = []
        self.color = []
        self.contentInsets = []
        self.version = []
        self.linkColor = []
        self.zoomPoint = []
        self.configs.append(data)
        for x in self.configs:
            try: self.allowedSlots.append(x["allowedSlots"])
            except (KeyError): self.allowedSlots.append(None)
            try: self.name.append(x["name"])
            except (KeyError): self.name.append(None)
            try: self.color.append(x["color"])
            except (KeyError): self.color.append(None)
            try: self.contentInsets.append(x["contentInsets"])
            except (KeyError): self.contentInsets.append(None)
            try: self.version.append(x["version"])
            except (KeyError): self.version.append(None)
            try: self.linkColor.append(x["linkColor"])
            except (KeyError): self.linkColor.append(None)
            try: self.zoomPoint.append(x["zoomPoint"])
            except (KeyError): self.zoomPoint.append(None)


class BubbleList:
    def __init__(self, data):
        self.json = data
        self.bubbleId = []
        self.bubbleName = []
        self.coverImage = []
        self.resourceUrl = []
        for o in data:
            try :self.bubbleId.append(o["bubbleId"])
            except (KeyError): pass
            try: self.bubbleName.append(o["config"]["name"])
            except (KeyError): pass
            try: self.coverImage.append(o["config"]["coverImage"])
            except (KeyError): pass
            try: self.resourceUrl.append(o['resourceUrl'])
            except (KeyError): pass
            try: self.config = BubbleConfig(o["config"])
            except (KeyError): self.config = BubbleConfig({})


class BubbleTemplates:
    def __init__(self, data):
        self.json = data
        self.templateId = []
        self.materialUrl = []
        self.name = []
        for x in data:
            try: self.templateId.append(x["templateId"])
            except (KeyError): self.templateId.append(None)
            try: self.materialUrl.append(x["materialUrl"])
            except (KeyError): self.materialUrl.append(None)
            try: self.name.append(x["name"])
            except (KeyError): self.name.append(None)
            try: self.config = BubbleConfig(x["config"])
            except (KeyError): self.config = BubbleConfig({})


class RepInfo:
    def __init__(self, data):
        self.json = data
        try: self.availableReputation = data["availableReputation"]
        except (KeyError): self.availableReputation = None
        try: self.reputation = data["reputation"]
        except (KeyError): self.reputation = None


class Rep:
    def __init__(self, data):
        self.json = data
        try: self.totalReputation = data["totalReputation"]
        except (KeyError): self.totalReputation = None
        try: self.participantCount = data["participantCount"]
        except (KeyError): self.participantCount = None


class Account:
    def __init__(self, data):
        self.json = data

        try: self.email = data["email"]
        except (KeyError): self.email = None
        try: self.icon = data["icon"]
        except (KeyError): self.icon = None
        try: self.nickname = data["nickname"]
        except (KeyError): self.nickname = None
        try: self.aminoId = data["aminoId"]
        except (KeyError): self.aminoId = None
        try: self.userId = data["uid"]
        except (KeyError): self.userId = None
