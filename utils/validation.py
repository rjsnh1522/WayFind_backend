from sqlalchemy.orm import Session

from db.models import Group
from services.group_service import GroupService
from services.user_service import UserService
from utils import app_logger

logger = app_logger.createLogger("app")


class Validator:

    @staticmethod
    @app_logger.functionlogs(log="log")
    def validate_group_creation(db: Session, user_id:int):
        try:
            user_setting = UserService.get_user_setting_by_user_id(user_id=user_id, db=db)
            if not user_setting:
                logger.warning(f"user {user_id} has no user settings. denying group creation.")
                return False
            max_group_creation = user_setting.max_group_creation
            user_groups = GroupService.fetch_user_groups(user_id=user_id, db=db)
            owned_groups = len(user_groups)
            if owned_groups >= max_group_creation:
                return False
            return True
        except Exception as e:
            app_logger.exceptionlogs(f"Error in validate_group_creation Error: {e} for user {user_id}")
            return False

    @staticmethod
    def user_already_in_group(db: Session, user_id, group_id):
        try:
            return GroupService.user_already_member_of_group(db=db, user_id=user_id, group_id=group_id)
        except Exception as e:
            app_logger.exceptionlogs(f"User already member of group {e}")
            return True
