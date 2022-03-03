from ctypes import Union
import os
import requests
from uuid import UUID
from typing import BinaryIO
from binascii import hexlify
from time import time as timestamp
from aminos import Wss

from .lib import *
from .lib import api
from .lib import CheckExceptions


class Client:
    def __init__(self, deviceId: str = None):
        self.uid = None
        headers.deviceId = deviceId
        self.deviceId = headers.Headers().deviceId
        self.headers = headers.Headers().headers
        self.socket: Wss

    def get_video_rep_info(self, chatId: str):
        req = requests.get(api(f"/g/s/chat/thread/{chatId}/avchat-reputation"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        else: return RepInfo(req.json())

    def claim_video_rep(self, chatId: str):
        info = self.get_video_rep_info(chatId)
        reputation = info.json["reputation"]
        if int(reputation) < 1: return CheckExceptions(f"reputation should be more than 1 (Your rep Now {int(reputation)}")
        req = requests.post(api(f"/g/s/chat/thread/{chatId}/avchat-reputation"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        else: return Rep(req.json())

    def change_lang(self, lang: str = "ar-SY"):
        self.headers = headers.Headers(lang).headers

    def sid_login(self, sid: str):
        if "sid=" not in sid: return TypeError("SessionId should starts with 'sid='")

        headers.sid = sid
        req = requests.get(api(f"/g/s/account"), headers=self.headers)
        info = Account(req.json()["account"])
        
        headers.sid = sid
        headers.uid = info.userId
        
        self.uid = headers.uid
        self.sid = headers.uid
        self.socket = Wss(self.headers)
        
        if "OK" not in req.json()["api:message"]: return info
        else: return CheckExceptions(req.json())

    def login(self, email: str, password: str):
        data = json.dumps({
            "email": email,
            "secret": f"0 {password}",
            "deviceID": self.deviceId,
            "clientType": 100,
            "action": "normal",
            "timestamp": int(timestamp() * 1000)
        })

        req = requests.post(api(f"/g/s/auth/login"), headers=headers.Headers(data=data).headers, data=data)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        else:
            sid = req.json()["sid"]
            self.uid = req.json()['auid']
            self.sid = f"sid={sid}"
            self.headers["NDCAUTH"] = self.sid
            headers.sid = self.sid
            headers.uid = self.uid
            self.userId = self.uid
            self.headers = headers.Headers().headers
            self.web_headers = headers.Headers().web_headers
            self.socket = Wss(self.headers)
            self.socket.launch()
            self.event = self.socket.event
            self.socketClient = self.socket.getClient()
            return Login(req.json())

    def check_device(self, deviceId: str):
        head = self.headers
        head["NDCDEVICEID"] = deviceId
        req = requests.post(api(f"/g/s/device"), headers=head)
        if req.json()["api:statuscode"] != 0: return CheckExceptions(req.json())
        return Json(req.json())

    def upload_image(self, image: BinaryIO):
        data = image.read()

        self.headers["content-type"] = "image/jpg"
        self.headers["content-length"] = str(len(data))

        req = requests.post(api(f"/g/s/media/upload"), data=data, headers=self.headers)
        return req.json()["mediaValue"]

    def send_verify_code(self, email: str):
        data = json.dumps({
            "identity": email,
            "type": 1,
            "deviceID": headers.deviceId,
            "timestamp": int(timestamp() * 1000)
        })

        req = requests.post(api(f"/g/s/auth/request-security-validation"), headers=headers.Headers(data=data).headers, data=data)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def accept_host(self, requestId: str, chatId: str):
        req = requests.post(api(f"/g/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def verify_account(self, email: str, code: str):
        data = json.dumps({
            "type": 1,
            "identity": email,
            "data": {"code": code},
            "deviceID": headers.deviceId
        })
        req = requests.post(api(f"/g/s/auth/activate-email"), data=data)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def restore(self, email: str, password: str):
        data = json.dumps({
            "secret": f"0 {password}",
            "deviceID": self.deviceId,
            "email": email,
            "timestamp": int(timestamp() * 1000)
        })

        req = requests.post(api(f"/g/s/account/delete-request/cancel"), headers=headers.Headers(data=data).headers, data=data)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def delete_account(self, password: str = None):
        data = json.dumps({
            "deviceID": self.deviceId,
            "secret": f"0 {password}",
            "timestamp": int(timestamp() * 1000)
        })

        req = requests.post(api(f"/g/s/account/delete-request"), headers=headers.Headers(data=data).headers, data=data)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def get_account_info(self):
        req = requests.get(api(f"/g/s/account"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return AccountInfo(req.json()['account'])

    def claim_coupon(self):
        req = requests.post(api(f"/g/s/coupon/new-user-coupon/claim"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def change_amino_id(self, aminoId: str = None):
        data = json.dumps({"aminoId": aminoId, "timestamp": int(timestamp() * 1000)})

        req = requests.post(api(f"/g/s/account/change-amino-id"), data=data, headers=headers.Headers(data=data).headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def get_my_communitys(self, start: int = 0, size: int = 25):
        req = requests.get(api(f"/g/s/community/joined?v=1&start={start}&size={size}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return MyCommunitys(req.json()['communityList'])

    def get_chat_threads(self, start: int = 0, size: int = 25):
        req = requests.get(api(f"/g/s/chat/thread?type=joined-me&start={start}&size={size}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return MyChats(req.json()['threadList'])

    def get_chat_info(self, chatId: str):
        req = requests.get(api(f"/g/s/chat/thread/{chatId}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return ChatInfo(req.json()['thread'])

    def leave_chat(self, chatId: str):
        req = requests.delete(api(f"/g/s/chat/thread/{chatId}/member/{self.uid}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def join_chat(self, chatId: str):
        req = requests.post(api(f"/g/s/chat/thread/{chatId}/member/{self.uid}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def start_chat(self, userId: str = None, title: str = None, message: str = None, content: str = None):
        if isinstance(userId, str): userIds = [userId]
        elif isinstance(userId, list): userIds = userId
        else: raise TypeError("List or str only! ")

        data = json.dumps({
            "title": title,
            "inviteeUids": userIds,
            "initialMessageContent": message,
            "content": content,
            "timestamp": int(timestamp() * 1000)
        })

        req = requests.post(api(f"/g/s/chat/thread"), headers=headers.Headers(data=data).headers, data=data)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def invite_to_chat(self, chatId: str = None, userId: str = None):
        if isinstance(userId, str): userIds = [userId]
        elif isinstance(userId, list): userIds = userId
        else: raise TypeError("List or str only! ")

        data = json.dumps({"uids": userIds, "timestamp": int(timestamp() * 1000)})

        req = requests.post(api("/g/s/chat/thread/{chatId}/member/invite"), data=data, headers=headers.Headers(data=data).headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def get_from_link(self, link: str):
        req = requests.get(api(f"/g/s/link-resolution?q={link}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Link(req.json()['linkInfoV2']['extensions'])

    def edit_profile(self, nickname: str = None, content: str = None):
        data = {
            "latitude": 0,
            "longitude": 0,
            "eventSource": "UserProfileView",
            "timestamp": int(timestamp() * 1000)
        }

        if nickname: data["nickname"] = nickname
        if content: data["content"] = content

        data = json.dumps(data)

        req = requests.post(api(f"/g/s/user-profile/{self.userId}"), headers=headers.Headers(data=data).headers, data=data)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def flag_community(self, comId: str, reason: str, flagType: int):  # Changed by SirLez
        """
        Flag a Community.

        **Parameters**
            - **comId** : Id of the community.
            - **reason** : Reason of the flag.
            - **flagType** : Type of flag.

        **Returns**
            - **Success** : :meth:`Json Object <samino.lib.objects.Json>`

            - **Fail** : :meth:`Exceptions <samino.lib.exceptions>`
        """
        data = json.dumps({
            "objectId": comId,
            "objectType": 16,
            "flagType": flagType,
            "message": reason,
            "timestamp": int(timestamp() * 1000)
        })

        req = requests.post(api(f"/x{comId}/s/g-flag"), headers=headers.Headers(data=data).headers, data=data)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def leave_community(self, comId: str):
        req = requests.post(api(f"/x{comId}/s/community/leave"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def join_community(self, comId: str):
        req = requests.post(api(f"/x{comId}/s/community/join"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def unfollow(self, userId: str):
        req = requests.post(api(f"/g/s/user-profile/{userId}/member/{self.userId}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def follow(self, userId: Union[str, list]):
        if isinstance(userId, str):
            url = api(f"/g/s/user-profile/{userId}/member")
            data = {"timestamp": int(timestamp() * 1000)}
        if isinstance(userId, list):
            url = api(f"/g/s/user-profile/{self.userId}/joined")
            data = json.dumps({"targetUidList": userId, "timestamp": int(timestamp() * 1000)})
        else: raise TypeError("userId should be str or list of userIds")

        req = requests.post(url, headers=headers.Headers(data=data).headers, data=data)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def get_member_following(self, userId: str, start: int = 0, size: int = 25):
        req = requests.get(api(f"/g/s/user-profile/{userId}/joined?start={start}&size={size}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return UserList(req.json()['userProfileList'])

    def get_member_followers(self, userId: str, start: int = 0, size: int = 25):
        req = requests.get(api(f"/g/s/user-profile/{userId}/member?start={start}&size={size}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return UserList(req.json()['userProfileList'])

    def get_member_visitors(self, userId: str, start: int = 0, size: int = 25):
        req = requests.get(api(f"/g/s/user-profile/{userId}/visitors?start={start}&size={size}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Visitors(req.json()['visitors'])

    def get_blocker_users(self, start: int = 0, size: int = 25):
        req = requests.get(api(f"/g/s/block/full-list?start={start}&size={size}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return req.json()['blockerUidList']

    def get_blocked_users(self, start: int = 0, size: int = 25):
        req = requests.get(api(f"/g/s/block/full-list?start={start}&size={size}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return req.json()['blockedUidList']

    def get_wall_comments(self, userId: str, sorting: str, start: int = 0, size: int = 25):
        sorting = sorting.lower()

        if sorting == "newest":
            sorting = "newest"
        elif sorting == "oldest":
            sorting = "oldest"
        elif sorting == "top":
            sorting = "vote"
        else:
            raise TypeError("حط تايب يا حمار")  # Not me typed this its (a7rf)

        req = requests.get(api(f"/g/s/user-profile/{userId}/g-comment?sort={sorting}&start={start}&size={size}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Comment(req.json()['commentList'])

    def send_message(self, chatId: str, message: str = None, messageType: int = 0, replyTo: str = None, mentionUserIds: list = None, embedId: str = None, embedType: int = None, embedLink: str = None, embedTitle: str = None, embedContent: str = None):
        uids = []
        if mentionUserIds:
            for uid in mentionUserIds: uids.append({"uid": uid})
        data = {
            "type": messageType,
            "content": message,
            "attachedObject": {
                "objectId": embedId,
                "objectType": embedType,
                "link": embedLink,
                "title": embedTitle,
                "content": embedContent
            },
            "extensions": {
                "mentionedArray": uids
            },
            "timestamp": int(timestamp() * 1000)
        }

        if replyTo: data["replyMessageId"] = replyTo

        data = json.dumps(data)

        req = requests.post(api(f"/g/s/chat/thread/{chatId}/message/{message}"), headers=headers.Headers(data=data).headers, data=data)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def get_community_info(self, comId: str):
        req = requests.get(api(f"/g/s-x{comId}/community/info?withInfluencerList=1&withTopicList=true&influencerListOrderStrategy=fansCount"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Community(req.json()['community'])

    def mark_as_read(self, chatId: str):
        req = requests.post(api(f"/g/s/chat/thread/{chatId}/mark-as-read"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def delete_message(self, messageId: str, chatId: str):
        req = requests.delete(api(f"/g/s/chat/thread/{chatId}/message/{messageId}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def get_chat_messages(self, chatId: str, start: int = 0, size: int = 25):
        req = requests.get(api(f"/g/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return ChatMessages(req.json()['messageList'])

    def get_message_info(self, messageId: str, chatId: str):
        req = requests.get(api(f"/g/s/chat/thread/{chatId}/message/{messageId}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Message(req.json()['message'])

    def tip_coins(self, chatId: str = None, blogId: str = None, coins: int = 0, transactionId: str = str(UUID(hexlify(os.urandom(16)).decode('ascii')))):
        data = json.dumps({
            "coins": coins,
            "tippingContext": {
                "transactionId": transactionId
            },
            "timestamp": int(timestamp() * 1000)
        })

        if chatId is not None: url = api(f"/g/s/blog/{chatId}/tipping")
        elif blogId is not None: url = api(f"/g/s/blog/{blogId}/tipping")
        else: raise TypeError("please put chat or blog Id")

        req = requests.post(url, headers=headers.Headers(data=data).headers, data=data)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def change_password(self, email: str, password: str, code: str, deviceId: str = None):
        if deviceId is None: deviceId = self.deviceId

        data = json.dumps({
            "updateSecret": f"0 {password}",
            "emailValidationContext": {
                "data": {
                    "code": code
                },
                "type": 1,
                "identity": email,
                "level": 2,
                "deviceID": deviceId
            },
            "phoneNumberValidationContext": None,
            "deviceID": deviceId,
            "timestamp": int(timestamp() * 1000)
        })


        req = requests.post(api(f"/g/s/auth/reset-password"), headers=headers.Headers(data=data).headers, data=data)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def get_user_info(self, userId: str):
        req = requests.get(api(f"/g/s/user-profile/{userId}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return UserInfo(req.json()['userProfile'])

    def comment(self, comment: str, userId: str = None, replyTo: str = None):
        data = {
            "content": comment,
            "stickerId": None,
            "type": 0,
            'eventSource': 'UserProfileView',
            "timestamp": int(timestamp() * 1000)
        }

        if replyTo: data["respondTo"] = replyTo

        data = json.dumps(data)

        req = requests.post(api(f"/g/s/user-profile/{userId}/g-comment"), headers=headers.Headers(data=data).headers, data=data)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def delete_comment(self, userId: str = None, commentId: str = None):
        req = requests.delete(api(f"/g/s/user-profile/{userId}/g-comment/{commentId}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def invite_by_host(self, chatId: str, userId: Union[str, list]):
        data = json.dumps({"uidList": userId, "timestamp": int(timestamp() * 1000)})

        req = requests.post(api(f"/g/s/chat/thread/{chatId}/avchat-members"), headers=headers.Headers(data=data).headers, data=data)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def kick(self, chatId: str, userId: str, rejoin: bool = True):
        if rejoin: re = 1
        if not rejoin: re = 0
        else: raise TypeError("rejoin should be False or True")

        req = requests.delete(api(f"/g/s/chat/thread/{chatId}/member/{userId}?allowRejoin={re}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def block(self, userId: str):
        req = requests.post(api(f"/g/s/block/{userId}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def unblock(self, userId: str):
        req = requests.delete(api(f"/g/s/block/{userId}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def invite_to_voice_chat(self, userId: str = None, chatId: str = None):
        data = json.dumps({"uid": userId, "timestamp": int(timestamp() * 1000)})

        req = requests.post(api(f"/g/s/chat/thread/{chatId}/vvchat-presenter/invite"), headers=headers.Headers(data=data).headers, data=data)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def get_wallet_history(self, start: int = 0, size: int = 25):
        req = requests.get(api(f"/g/s/wallet/coin/history?start={start}&size={size}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return CoinsHistory(req.json())

    def get_wallet_info(self):
        req = requests.get(api(f"/g/s/wallet"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return WalletInfo(req.json()['wallet'])

    def get_all_users(self, type: str = "recent", start: int = 0, size: int = 25):
        if type == "recent": type = "recent"
        elif type == "banned": type = "banned"
        elif type == "featured": type = "featured"
        elif type == "leaders": type = "leaders"
        elif type == "curators": type = "curators"
        else: type = "recent"

        req = requests.get(api(f"/g/s/user-profile?type={type}&start={start}&size={size}"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return UserList(req.json()['userProfileList'])

    def get_chat_members(self, start: int = 0, size: int = 25, chatId: str = None):
        req = requests.get(api(f"/g/s/chat/thread/{chatId}/member?start={start}&size={size}&type=default&cv=1.2"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return UserList(req.json()['memberList'])

    def get_from_id(self, id: str, comId: str = None, objectType: int = 2):  # never tried
        """
        Get Link from Id.

        **Parameters**
            - **comId** : Id of the community.
            - **objectType** : Object type of the id.
            - **id** : The id.

        **Returns**
            - **Success** : :meth:`Json Object <samino.lib.objects.Json>`

            - **Fail** : :meth:`Exceptions <samino.lib.exceptions>`
        """
        data = json.dumps({
            "objectId": id,
            "targetCode": 1,
            "objectType": objectType,
            "timestamp": int(timestamp() * 1000)
        })

        if comId is None: url = api(f"/g/s/link-resolution")
        elif comId is not None: url = api(f"/g/s-x{comId}/link-resolution")
        else: raise TypeError("please put a comId")


        req = requests.post(url, headers=headers.Headers(data=data).headers, data=data)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return IdInfo(req.json()['linkInfoV2']['extensions']['linkInfo'])

    def chat_settings(self, chatId: str, viewOnly: bool = None, doNotDisturb: bool = None, canInvite: bool = False, canTip: bool = None, pin: bool = None):
        res = []

        if doNotDisturb is not None:
            if doNotDisturb: opt = 2
            if not doNotDisturb: opt = 1
            else: raise TypeError("Do not disturb should be True or False")
            
            data = json.dumps({"alertOption": opt, "timestamp": int(timestamp() * 1000)})
            req = requests.post(api(f"/g/s/chat/thread/{chatId}/member/{self.uid}/alert"), data=data, headers=headers.Headers(data=data).headers)
            if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        if viewOnly is not None:
            if viewOnly: viewOnly = "enable"
            if not viewOnly: viewOnly = "disable"
            else: raise TypeError("viewOnly should be True or False")
            
            req = requests.post(api(f"/g/s/chat/thread/{chatId}/view-only/{viewOnly}"), headers=self.headers)
            if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        if canInvite is not None:
            if canInvite: canInvite = "enable"
            if not canInvite: canInvite = "disable"
            else: raise TypeError("can invite should be True or False")
            
            req = requests.post(api(f"/g/s/chat/thread/{chatId}/members-can-invite/{canInvite}"), headers=self.headers)
            if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        if canTip is not None:
            if canTip: canTip = "enable"
            if not canTip: canTip = "disable"
            else: raise TypeError("can tip should be True or False")
            
            req = requests.post(api(f"/g/s/chat/thread/{chatId}/tipping-perm-status/{canTip}"), headers=self.headers)
            if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        if pin is not None:
            if pin: pin = "pin"
            if not pin: pin = "unpin"
            else: raise TypeError("pin should be True or False")
            
            req = requests.post(api(f"/g/s/chat/thread/{chatId}/{pin}"), headers=self.headers)
            if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        return res

    def like_comment(self, commentId: str, userId: str = None, blogId: str = None):
        data = json.dumps({"value": 4, "timestamp": int(timestamp() * 1000)})

        if userId: url = api(f"/g/s/user-profile/{userId}/comment/{commentId}/g-vote?cv=1.2&value=1")
        if blogId: url = api(f"/g/s/blog/{blogId}/comment/{commentId}/g-vote?cv=1.2&value=1")
        else: raise TypeError("Please put blogId or wikiId")

        req = requests.post(url, data=data, headers=headers.Headers(data=data).headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def unlike_comment(self, commentId: str, blogId: str = None, userId: str = None):
        if userId: url = api(f"/g/s/user-profile/{userId}/comment/{commentId}/g-vote?eventSource=UserProfileView")
        elif blogId: url = api(f"/g/s/blog/{blogId}/comment/{commentId}/g-vote?eventSource=PostDetailView")
        else: raise TypeError("Please put blog or user Id")

        req = requests.delete(url, headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def register(self, nickname: str, email: str, password: str, verificationCode: str, deviceId: str = None):
        if deviceId is None: deviceId = self.deviceId

        data = json.dumps({
            "secret": f"0 {password}",
            "deviceID": deviceId,
            "email": email,
            "clientType": 100,
            "nickname": nickname,
            "latitude": 0,
            "longitude": 0,
            "address": None,
            "clientCallbackURL": "narviiapp://relogin",
            "validationContext": {
                "data": {
                    "code": verificationCode
                },
                "type": 1,
                "identity": email
            },
            "type": 1,
            "identity": email,
            "timestamp": int(timestamp() * 1000)
        })

        req = requests.post(api(f"/g/s/auth/register"), data=data, headers=headers.Headers(data=data).headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

    def watch_ad(self):
        req = requests.post(api(f"/g/s/wallet/ads/video/start"), headers=self.headers)
        if "OK" not in req.json()["api:message"]: return CheckExceptions(req.json())
        return Json(req.json())

