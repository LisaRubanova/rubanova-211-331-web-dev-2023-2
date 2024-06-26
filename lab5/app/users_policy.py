
from flask_login import current_user

class UsersPolicy:
    def __init__(self, record):
        self.record = record

    def create(self):
        return current_user.is_admin()

    def delete(self):
        return current_user.is_admin()

    def show(self):
        return True
    
    def edit(self):
        if current_user.id == self.record.id:
            return True
        return current_user.is_admin()


    # возможность просматривать статистику админу
    def show_statistics(self):
        return current_user.is_admin()
    
	# возможность изменить свою роль может только администратор
    def change_role(self):
        return current_user.is_admin()
