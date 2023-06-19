import os

from flask import Blueprint, request, abort

from webapp import find_user_with_email, find_user_with_id
from webapp.db import notifications as db

notifications_api = Blueprint("notifications_api", __name__)


SECRET_API_KEY = os.getenv("SECRET_API_KEY")


@notifications_api.before_request
def check_secret_key():
    values = request.values
    if "secret-key" not in values or values["secret-key"] != SECRET_API_KEY:
        abort(403)


@notifications_api.errorhandler(403)
def handle_forbidden(e):
    return {
        "success": False,
        "message": "missing-secret-key"
    }, 403


@notifications_api.route("/telegram-account/<int:id_>")
def get_account_status(id_: int):
    account = db.find_telegram_with_id(id_)
    if account is None:
        return {
            "success": True,
            "connected": False,
            "user_id": None
        }
    return {
        "success": True,
        "connected": True,
        "user_id": account.user.id
    }


@notifications_api.route("/telegram-account/<int:id_>", methods=("POST",))
def connect_account(id_: int):
    account_id = id_
    user = find_user_with_email(request.json["user-email"])
    account_username = request.json["account-username"]
    verification_code = request.json["verification-code"]
    if user is None:
        return {
            "success": False,
            "message": "no-user-with-email"
        }
    if not user.is_verification_code_valid(verification_code):
        return {
            "success": False,
            "message": "wrong-verification-code"
        }
    try:
        db.connect_telegram(user, account_id, account_username)
    except db.UserAlreadyConnectedToTelegram:
        return {
            "success": False,
            "message": "user-already-connected"
        }
    except db.TelegramAlreadyConnectedToAnotherUser:
        return {
            "success": False,
            "message": "telegram-already-connected"
        }
    return {
        "success": True
    }


@notifications_api.route("/pending-notifications")
def get_pending_notifications():
    result = []
    notifications = db.get_pending_notifications()
    for notification in notifications:
        account = db.find_telegram_for(notification.user)
        if account is None:
            continue
        result.append({
            "notification": notification.to_json(),
            "account": account.to_json()
        })
    return {
        "success": True,
        "notifications": result
    }


@notifications_api.route("/pending-notifications/<int:id_>/delivered", methods=("POST",))
def mark_notification_delivered(id_: int):
    notification = db.find_notification_with_id(id_)
    if notification is None:
        return {
            "success": False,
            "message": "no-notification-with-id"
        }
    db.mark_delivered(notification)
    return {
        "success": True
    }
