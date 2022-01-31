import os
import re

from pvpc_bot.ree.utils import store_data, load_data
from pvpc_bot.config import SETTINGS_DIR


class SettingsManager:
    def __init__(self, restore_backup=True):
        self.users = {}
        if restore_backup:
            self.load_settings(system=True)
    

    def register_user(self, user_id: int):
        if user_id not in self.users:
            self.users[user_id] = {
                "subscribed": True,
                "timezone": "Península",
                "colors": "percentiles"
            }
            self.backup_settings(user_id=user_id)
    
    def set_config(self, user_id: int, property_name: str, property_value: 'Any') -> None:
        if user_id not in self.users:
            self.register_user(user_id)
        self.users[user_id][property_name] = property_value
        self.backup_settings(user_id=user_id)
    
    def backup_settings(self, user_id: int=None, system: bool=False, backup_path: str=None):
        def save_user_data(user_id, data):
            backup_file = backup_path or os.path.join(SETTINGS_DIR, f"{user_id}_settings.json")
            store_data(json_data=data, file_path=backup_file)
        
        if not system and all(param is None for param in (user_id, backup_path)):
            raise Exception("Either user_id must be provided or backup_path must be enabled when not backing up the whole system.")
        
        if system:
            if backup_path:
                # If admin request all data, we have to wait D:
                store_data(json_data=self.users, file_path=backup_path, wait=True)
            else:
                for user_id, data in self.users.items():
                    save_user_data(user_id, data)
        else:
            save_user_data(user_id, self.users[user_id])

    def load_settings(self, user_id:int=None, system: bool=False, backup_path: str=None):
        if not system and all(param is None for param in (user_id, backup_path)):
            raise Exception("Either user_id must be provided or backup_path must be enabled when not restoring the whole system.")
        
        backup_file = backup_path or os.path.join(SETTINGS_DIR, "system_settings.json" if system else f"{user_id}_settings.json")
        data = load_data(backup_file)
        if system:
            if backup_path:
                self.users = {int(key): value for key, value in data.items()}
            else:
                for backup_file in os.listdir(SETTINGS_DIR):
                    match = re.search(r"(\d+)_settings.json", backup_file)
                    if match:
                        user_id = int(match.group(1))
                        data = load_data(os.path.join(SETTINGS_DIR, backup_file))
                        self.users[user_id] = data
        else:
            self.users[user_id] = data
