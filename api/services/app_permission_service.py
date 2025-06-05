from datetime import UTC
from typing import cast

from extensions.ext_database import db
from models.model import App, AppPermissionConfig
from tasks.remove_app_and_related_data_task import remove_app_and_related_data_task

from models.account import (
    TenantAccountJoin
)

class AppPermissionService:
    def get_app_permission(self, app_id: str) -> list:
            """
            Get App Permission Users + attach owner users (if not already in list)
            """
            app_permissions = db.session.query(AppPermissionConfig).filter(
                AppPermissionConfig.app_id == app_id
            ).all()
            owner_users = db.session.query(TenantAccountJoin).filter_by(role="owner").all()
            existing_account_ids = {perm.account_id for perm in app_permissions}
            for owner in owner_users:
                if owner.account_id not in existing_account_ids:
                    app_permissions.append(AppPermissionConfig(
                        app_id=app_id,
                        account_id=owner.account_id,
                    ))
            return app_permissions

    def create_app_permissions(self, app_id: str, account_ids: list[str]) -> list[AppPermissionConfig]:
        permissions = []
        db.session.query(AppPermissionConfig).filter(AppPermissionConfig.app_id == app_id).delete()
        for acc_id in account_ids:
            permission = AppPermissionConfig(
                app_id=app_id,
                account_id=acc_id,
            )
            db.session.add(permission)
            permissions.append(permission)

        db.session.commit()
        return permissions
    
    def get_user_permission(self, account_id: str) -> App:
        """
        Get App Permission Users
        """
        # return all app have permission with provided account Id
        
        app = db.session.query(AppPermissionConfig).filter(AppPermissionConfig.account_id == account_id).all()
        if not app:
            return None
        return app
      