from sqlalchemy.orm import Session

from db.models import User, UserSetting
from db.schemas import UserProfile
from utils import app_logger


class UserService:

    @staticmethod
    def get_user_by_id(user_id: int, db: Session):
        query = db.query(User)
        return query.filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_phone_number(phone_number: str, db: Session):
        user = db.query(User).filter(User.phone_number == phone_number).first()
        return user

    @staticmethod
    def create_user_setting(user: User, db: Session):
        user_settings = UserSetting(user_id=user.id, max_group_creation=3)  # Default settings
        db.add(user_settings)

    @staticmethod
    def get_or_create_user_setting(user: User, db: Session):
        user_setting = db.query(UserSetting).filter(UserSetting.user_id==user.id).first()
        if not user_setting:
            UserService.create_user_setting(user=user, db=db)
        else:
            user_setting.max_group_creation = 3
            db.add(user_setting)
            db.commit()

    @staticmethod
    def update_user_data(db: Session, user: User, user_profile_data: UserProfile):
        try:
            update_fields = user_profile_data.model_dump(exclude_unset=True)

            # Update fields dynamically
            for key, value in update_fields.items():
                setattr(user, key, value)

            db.commit()
            db.refresh(user)  # Refresh to get updated data
            return user
        except Exception as e:
            app_logger.exceptionlogs(f"Error in update_user_data {e}")
            return None

    @staticmethod
    def create_user_by_phone_number(phone_number: str, db: Session):
        try:
            user = UserService.get_user_by_phone_number(phone_number=phone_number, db=db)
            if not user:
                user = User(phone_number=phone_number, is_phone_verified=True, is_active=True)
                db.add(user)
                db.commit()
                db.refresh(user)
                UserService.get_or_create_user_setting(user=user, db=db)
            else:
                user.is_phone_verified = True
                user.is_active = True
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            app_logger.exceptionlogs(f"Error in get_or_create_user_by_phone_number, Error: {e}")
            return None

    @staticmethod
    def get_user_setting_by_user_id(user_id: int, db: Session):
        return db.query(UserSetting).filter(UserSetting.user_id == user_id).first()