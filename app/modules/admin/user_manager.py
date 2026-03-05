from app.models.user import User


class UserManager:

    @staticmethod
    def list_users():

        return User.query.all()


    @staticmethod
    def get_user(user_id):

        return User.query.get_or_404(user_id)