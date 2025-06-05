from flask import request
from flask_login import current_user
from flask_restful import Resource, marshal_with
from werkzeug.exceptions import BadRequest, Forbidden

from controllers.console import api
from controllers.console.app.wraps import get_app_model
from controllers.console.wraps import (
    account_initialization_required,
    cloud_edition_billing_resource_check,
    enterprise_license_required,
    setup_required,
)
from fields.app_permission_fields import app_permission_fields
from libs.login import login_required
from services.app_permission_service import AppPermissionService

ALLOW_CREATE_APP_MODES = ["chat", "agent-chat", "advanced-chat", "workflow", "completion"]


class AppPermissionApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @enterprise_license_required
    @get_app_model
    @marshal_with(app_permission_fields)
    def get(self, app_model):
        """Get app permission users"""
        print("current_user.is_admin_or_owner", current_user.is_admin_or_owner)
        if not current_user.is_admin_or_owner:
            raise Forbidden()
        
        app_permission_service = AppPermissionService()
        permissions = app_permission_service.get_app_permission(app_model.id)
        return permissions
    
    @setup_required
    @login_required
    @account_initialization_required
    @marshal_with(app_permission_fields)
    @cloud_edition_billing_resource_check("apps")
    def post(self, app_id):
        data = request.get_json()

        account_ids = data.get("account_id", [])
        if not isinstance(account_ids, list):
            raise BadRequest("account_id must be a list")

        if not current_user.is_admin_or_owner:
            raise Forbidden()

        app_permission_service = AppPermissionService()
        permissions = app_permission_service.create_app_permissions(app_id, account_ids)
        
        return permissions, 201
     
api.add_resource(AppPermissionApi, "/apps-permission/<uuid:app_id>")