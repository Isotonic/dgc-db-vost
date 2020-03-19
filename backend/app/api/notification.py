from ..api import api
from .utils.resource import Resource
from .utils.namespace import Namespace
from ..models import User, Notifications
from .utils.models import notification_model
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..utils.delete import delete_notification, delete_all_notifications

ns_notification = Namespace('Notification', description='Used to carry out actions related to notifications.', path='/notifications', decorators=[jwt_required])

@ns_notification.route('')
class NotificationsEndpoint(Resource):
    @ns_notification.doc(security='access_token')
    @ns_notification.response(200, 'Success', [notification_model])
    @ns_notification.response(401, 'Incorrect credentials')
    @api.marshal_with(notification_model)
    def get(self):
        """
                Returns all notifications.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()

        return current_user.notifications, 200


    @ns_notification.doc(security='access_token')
    @ns_notification.response(200, 'Success')
    @ns_notification.response(401, 'Incorrect credentials')
    def delete(self):
        """
                Deletes all notification.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()
        delete_all_notifications(current_user)

        return 'Success', 200


@ns_notification.route('/<int:id>')
@ns_notification.doc(params={'id': 'Notification ID.'})
@ns_notification.resolve_object('notification', lambda kwargs: Notifications.query.get_or_error(kwargs.pop('id')))
class NotificationEndpoint(Resource):
    @ns_notification.doc(security='access_token')
    @ns_notification.response(200, 'Success', notification_model)
    @ns_notification.response(401, 'Incorrect credentials')
    @ns_notification.response(404, 'Notification doesn\'t exist')
    @api.marshal_with(notification_model)
    def get(self, notification):
        """
                Returns notification info.
        """
        return notification, 200


    @ns_notification.doc(security='access_token')
    @ns_notification.response(200, 'Success')
    @ns_notification.response(401, 'Incorrect credentials')
    @ns_notification.response(402, 'Notification doesn\'t belong to you')
    @ns_notification.response(404, 'Notification doesn\'t exist')
    def delete(self, notification):
        """
                Deletes a notification.
        """
        current_user = User.query.filter_by(id=get_jwt_identity()).first()

        if current_user.id != notification.user.id:
            ns_notification.abort(401, 'Notification doesn\'t belong to you')

        delete_notification(notification)
        return 'Success', 200
