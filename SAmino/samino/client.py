import json
import requests

import os
from uuid import UUID, uuid4
from binascii import hexlify

from .lib import headers
from .lib.objects import *
from .socket import Socket, Recall
from .lib.exception import CheckExceptions


class Client(Recall, Socket):
    def __init__(self, deviceId: str):
        self.api = 'https://service.narvii.com/api/v1'
        self.deviceId = deviceId
        self.uid = None
        self.sid = None
        self.userId = self.uid
        headers.deviceId = self.deviceId
        self.headers = headers.Headers().headers
        self.ad_headers = headers.AdHeaders().headers
        self.ad_data = headers.AdHeaders().data
        Recall.__init__(self)
        Socket.__init__(self, self)

    def handle(self, data):
        return self.solve(data)

    def login(self, email: str, password=str):
        data = json.dumps({
            "email": email,
            "secret": f"0 {password}",
            "deviceID": self.deviceId,
            "clientType": 100,
            "action": "normal"
        })
        req = requests.post(f"{self.api}/g/s/auth/login", headers=self.headers, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        sid = req.json()["sid"]
        self.uid = req.json()['auid']
        self.sid = f"sid={sid}"
        self.headers["NDCAUTH"] = self.sid
        headers.sid = self.sid
        headers.uid = self.uid
        return Login(req.json())

    def logout(self):
        data = json.dumps({
            "deviceID": self.deviceId,
            "clientType": 100})

        req = requests.post(f"{self.api}/g/s/auth/logout", headers=self.headers, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        self.sid = None
        self.uid = None
        return Json(req.json())

    def send_verify_code(self, email: str):
        data = json.dumps({
            "identity": email,
            "type": 1,
            "deviceID": headers.deviceId
        })
        req = requests.post(f"{self.api}/g/s/auth/request-security-validation", headers=self.headers, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def accept_host(self, requestId: str, chatId: str):
        req = requests.post(f"{self.api}/g/s/chat/thread/{chatId}/transfer-organizer/{requestId}/accept", headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def verify_account(self, email: str, code: str):
        data = json.dumps({
            "type": 1,
            "identity": email,
            "data": {"code": code},
            "deviceID": headers.deviceId
        })
        req = requests.post(f'{self.api}/g/s/auth/activate-email', data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def restore(self, email: str, password: str):
        data = json.dumps({
            "secret": f"0 {password}",
            "deviceID": self.deviceId,
            "email": email
        })
        req = requests.post(f"{self.api}/g/s/account/delete-request/cancel", headers=self.headers, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def delete_account(self, password: str = None):
        data = json.dumps({
            "deviceID": self.deviceId,
            "secret": f"0 {password}"
        })
        req = requests.post(f"{self.api}/g/s/account/delete-request", headers=self.headers, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_account_info(self):
        req = requests.get(f"{self.api}/g/s/account", headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return AccountInfo(req.json()['account'])

    def claim_coupon(self):
        req = requests.post(f"{self.api}/g/s/coupon/new-user-coupon/claim", headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def change_amino_id(self, aminoId: str = None):
        data = json.dumps({"aminoId": aminoId})
        req = requests.post(f'{self.api}/g/s/account/change-amino-id', data=data, headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_my_communitys(self, start: int = 0, size: int = 25):
        req = requests.get(f"{self.api}/g/s/community/joined?v=1&start={start}&size={size}", headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return MyCommunitys(req.json()['communityList'])

    def get_chat_threads(self, start: int = 0, size: int = 25):
        req = requests.get(f'{self.api}/g/s/chat/thread?type=joined-me&start={start}&size={size}', headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return MyChats(req.json()['threadList'])

    def leave_chat(self, chatId: str):
        req = requests.delete(f'{self.api}/g/s/chat/thread/{chatId}/member/{self.uid}', headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def join_chat(self, chatId: str):
        req = requests.post(f'{self.api}/g/s/chat/thread/{chatId}/member/{self.uid}', headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def start_chat(self, userId: str = None, title: str = None, message: str = None, content: str = None):
        if isinstance(userId, str): userIds = [userId]
        elif isinstance(userId, list): userIds = userId
        else: raise TypeError("")

        data = json.dumps({
            "title": title,
            "inviteeUids": userIds,
            "initialMessageContent": message,
            "content": content,
        })
        req = requests.post(f'{self.api}/g/s/chat/thread', headers=self.headers, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def invite_to_chat(self, chatId: str = None, userId: str = None):
        if isinstance(userId, str): userIds = [userId]
        elif isinstance(userId, list): userIds = userId
        else: raise TypeError("")

        data = json.dumps({"uids": userIds})
        req = requests.post(f'{self.api}/g/s/chat/thread/{chatId}/member/invite', data=data, headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_from_link(self, link: str):
        req = requests.get(f'{self.api}/g/s/link-resolution?q={link}', headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Link(req.json()['linkInfoV2']['extensions'])

    def edit_profile(self, nickname: str = None, content: str = None):
        data = {
            "latitude": 0,
            "longitude": 0,
            "eventSource": "UserProfileView"
        }

        if nickname: data["nickname"] = nickname
        if content: data["content"] = content

        data = json.dumps(data)
        req = requests.post(f'{self.api}/g/s/user-profile/{self.userId}', headers=self.headers, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
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
            "message": reason
        })
        req = requests.post(f"{self.api}/x{comId}/s/g-flag", headers=self.headers, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def leave_community(self, comId: str):
        req = requests.post(f'{self.api}/x{comId}/s/community/leave', headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def join_community(self, comId: str):
        req = requests.post(f'{self.api}/x{comId}/s/community/join', headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def unfollow(self, userId: str):
        req = requests.post(f"{self.api}/g/s/user-profile/{userId}/member/{self.userId}", headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def follow(self, userId: [str, list]):
        if isinstance(userId, str):
            api = f"{self.api}/g/s/user-profile/{userId}/member"
            data = {}
        if isinstance(userId, list):
            api = f'{self.api}/g/s/user-profile/{self.userId}/joined'
            data = json.dumps({"targetUidList": userId})

        req = requests.post(api, headers=self.headers, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_member_following(self, userId: str, start: int = 0, size: int = 25):
        req = requests.get(f'{self.api}/g/s/user-profile/{userId}/joined?start={start}&size={size}', headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return UserList(req.json()['userProfileList'])

    def get_member_followers(self, userId: str, start: int = 0, size: int = 25):
        req = requests.get(f'{self.api}/g/s/user-profile/{userId}/member?start={start}&size={size}', headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return UserList(req.json()['userProfileList'])

    def get_member_visitors(self, userId: str, start: int = 0, size: int = 25):
        req = requests.get(f'{self.api}/g/s/user-profile/{userId}/visitors?start={start}&size={size}', headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Visitors(req.json()['visitors'])

    def get_blocker_users(self, start: int = 0, size: int = 25):
        req = requests.get(f'{self.api}/g/s/block/full-list?start={start}&size={size}', headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return req.json()['blockerUidList']

    def get_blocked_users(self, start: int = 0, size: int = 25):
        req = requests.get(f'{self.api}/g/s/block/full-list?start={start}&size={size}', headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return req.json()['blockedUidList']

    def get_wall_comments(self, userId: str, sorting: str, start: int = 0, size: int = 25):
        sorting = sorting.lower()

        if sorting == "newest": sorting = "newest"
        elif sorting == "oldest": sorting = "oldest"
        elif sorting == "top": sorting = "vote"
        else: raise TypeError("حط تايب يا حمار")  # Not me typed this its (a7rf)

        req = requests.get(f"{self.api}/g/s/user-profile/{userId}/g-comment?sort={sorting}&start={start}&size={size}", headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
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
        }
        
        if replyTo: data["replyMessageId"] = replyTo
        
        data = json.dumps(data)
        req = requests.post(f"{self.api}/g/s/chat/thread/{chatId}/message/{message}", headers=self.headers, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_community_info(self, comId: str):
        req = requests.get(f"{self.api}/g/s-x{comId}/community/info?withInfluencerList=1&withTopicList=true&influencerListOrderStrategy=fansCount", headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Community(req.json()['community'])

    def mark_as_read(self, chatId: str):
        req = requests.post(f'{self.api}/g/s/chat/thread/{chatId}/mark-as-read', headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def delete_message(self, messageId: str, chatId: str):
        req = requests.delete(f"{self.api}/g/s/chat/thread/{chatId}/message/{messageId}", headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_chat_messages(self, chatId: str, start: int = 0, size: int = 25):
        req = requests.get(f'{self.api}/g/s/chat/thread/{chatId}/message?v=2&pagingType=t&size={size}', headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return ChatMessages(req.json()['messageList'])

    def get_message_info(self, messageId: str, chatId: str):
        req = requests.get(f'{self.api}/g/s/chat/thread/{chatId}/message/{messageId}', headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Message(req.json()['message'])

    def tip_coins(self, chatId: str = None, blogId: str = None, coins: int = 0, transactionId: str = str(UUID(hexlify(os.urandom(16)).decode('ascii')))):
        data = json.dumps({
            "coins": coins,
            "tippingContext": {
                "transactionId": transactionId
            }
        })

        if chatId is not None:api = f'{self.api}/g/s/blog/{chatId}/tipping'
        elif blogId is not None: api = f"{self.api}/g/s/blog/{blogId}/tipping"
        else:raise TypeError("")

        req = requests.post(api, headers=self.headers, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    # Not working if the account agent-leader to an community
    # Not working now (NOW)
    def change_password(self, email: str, password: str):
        data = json.dumps({
            "updateSecret": f"0 {password}",
            "emailValidationContext": {
                "identity": email,
                "deviceID": self.deviceId
            },
            "phoneNumberValidationContext": None,
            "deviceID": self.deviceId
        })
        print(data)
        req = requests.post(f"{self.api}/g/s/auth/reset-password", headers=self.headers, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_user_info(self, userId: str):
        req = requests.get(f"{self.api}/g/s/user-profile/{userId}",
                           headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return UserInfo(req.json()['userProfile'])

    def comment(self, comment: str, userId: str = None, replyTo: str = None):
        data = {
            "content": comment,
            "stickerId": None,
            "type": 0,
            'eventSource': 'UserProfileView'
        }

        if replyTo: data["respondTo"] = replyTo

        data = json.dumps(data)
        req = requests.post(f'{self.api}/g/s/user-profile/{userId}/g-comment', headers=self.headers, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def delete_comment(self, userId: str = None, commentId: str = None):
        req = requests.delete(f'{self.api}/g/s/user-profile/{userId}/g-comment/{commentId}', headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    # Function by Bovonos
    def invite_by_host(self, chatId: str, userId: [str, list]):
        data = json.dumps({"uidList": userId})
        req = requests.post(f"{self.api}/g/s/chat/thread/{chatId}/avchat-members", headers=self.headers, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def kick(self, chatId: str, userId: str, rejoin: bool = True):
        if rejoin: re = 1
        if not rejoin: re = 0
        req = requests.delete(f'{self.api}/g/s/chat/thread/{chatId}/member/{userId}?allowRejoin={re}', headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def block(self, userId: str):
        req = requests.post(f"{self.api}/g/s/block/{userId}", headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def unblock(self, userId: str):
        req = requests.delete(f"{self.api}/g/s/block/{userId}", headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def invite_to_voice_chat(self, userId: str = None, chatId: str = None):
        data = json.dumps({"uid": userId})
        req = requests.post(f'{self.api}/g/s/chat/thread/{chatId}/vvchat-presenter/invite', headers=self.headers, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def get_wallet_history(self, start: int = 0, size: int = 25):
        req = requests.get(f"{self.api}/g/s/wallet/coin/history?start={start}&size={size}", headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return CoinsHistory(req.json())

    def get_wallet_info(self):
        req = requests.get(f"{self.api}/g/s/wallet", headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return WalletInfo(req.json()['wallet'])

    def get_all_users(self, start: int = 0, size: int = 25):
        req = requests.get(f'{self.api}/g/s/user-profile?type=recent&start={start}&size={size}', headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return UserList(req.json()['userProfileList'])

    def get_chat_members(self, start: int = 0, size: int = 25, chatId: str = None):
        req = requests.get(f"{self.api}/g/s/chat/thread/{chatId}/member?start={start}&size={size}&type=default&cv=1.2", headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
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
            "objectType": objectType
        })

        if comId is None:
            url = f"{self.api}/g/s/link-resolution"
        elif comId is not None:
            url = f"{self.api}/g/s-x{comId}/link-resolution"

        req = requests.post(url, headers=self.headers, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return IdInfo(req.json()['linkInfoV2']['extensions']['linkInfo'])

    def chat_settings(self, chatId: str, viewOnly: bool = None, doNotDisturb: bool = None, canInvite: bool = False, canTip: bool = None, pin: bool = None):
        res = []

        if doNotDisturb is not None:
            if doNotDisturb: opt = 2
            if not doNotDisturb: opt = 1
            data = json.dumps({"alertOption": opt})
            req = requests.post(f"{self.api}/g/s/chat/thread/{chatId}/member/{self.uid}/alert", data=data,
                                headers=self.headers)
            if req.status_code != 200: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        if viewOnly is not None:
            if viewOnly: viewOnly = "enable"
            if not viewOnly: viewOnly = "disable"
            req = requests.post(f"{self.api}/g/s/chat/thread/{chatId}/view-only/{viewOnly}", headers=self.headers)
            if req.status_code != 200: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        if canInvite is not None:
            if canInvite: canInvite = "enable"
            if not canInvite: canInvite = "disable"
            req = requests.post(f"{self.api}/g/s/chat/thread/{chatId}/members-can-invite/{canInvite}",
                                headers=self.headers)
            if req.status_code != 200: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        if canTip is not None:
            if canTip: canTip = "enable"
            if not canTip: canTip = "disable"
            req = requests.post(f"{self.api}/g/s/chat/thread/{chatId}/tipping-perm-status/{canTip}",
                                headers=self.headers)
            if req.status_code != 200: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        if pin is not None:
            if pin: pin = "pin"
            if not pin: pin = "unpin"
            req = requests.post(f"{self.api}/g/s/chat/thread/{chatId}/{pin}", headers=self.headers)
            if req.status_code != 200: return CheckExceptions(req.json())
            res.append(Json(req.json()))

        return res

    def like_comment(self, commentId: str, userId: str = None, blogId: str = None):
        data = json.dumps({"value": 4})

        if userId: api = f"{self.api}/g/s/user-profile/{userId}/comment/{commentId}/g-vote?cv=1.2&value=1"
        if blogId: api = f"{self.api}/g/s/blog/{blogId}/comment/{commentId}/g-vote?cv=1.2&value=1"

        req = requests.post(api, data=data, headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def unlike_comment(self, commentId: str, blogId: str = None, userId: str = None):
        if userId: api = f"{self.api}/g/s/user-profile/{userId}/comment/{commentId}/g-vote?eventSource=UserProfileView"
        elif blogId: api = f"{self.api}/g/s/blog/{blogId}/comment/{commentId}/g-vote?eventSource=PostDetailView"
        req = requests.delete(api, headers=self.headers)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    def register(self, nickname: str, email: str, password: str, verifyCode: str = None, deviceId: str = None):
        if deviceId is None: deviceId = self.deviceId
        data = {
            "secret": f"0 {password}",
            "deviceID": deviceId,
            "email": email,
            "clientType": 100,
            "nickname": nickname,
            "latitude": 0,
            "longitude": 0,
            "address": None,
            "clientCallbackURL": "narviiapp://relogin",
            "validationContext": None,
            "type": 1,
            "identity": email
        }
        if verifyCode: data['validationContext'] = {"data": {"code": verifyCode}, "type": 1, "identity": email}
        req = requests.post(f"{self.api}/g/s/auth/register", headers=self.headers, data=data)
        if req.status_code != 200: return CheckExceptions(req.json())
        return Json(req.json())

    # By Marshall (Smile, Texaz)
    def watch_ad(self, uid: str = None):
        if uid: self.ad_data["reward"]["custom_json"]["hashed_user_id"] = uid
        if not uid: self.ad_data["reward"]["custom_json"]["hashed_user_id"] = self.uid
        self.ad_data["reward"]["event_id"] = str(uuid4())
        req = requests.post("https://ads.tapdaq.com/v4/analytics/reward", headers=self.ad_headers, json=self.ad_data)
        if req.status_code != 204: return CheckExceptions(req.text)
        else: return req.status_code
