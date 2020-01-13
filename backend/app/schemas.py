from app import db, ma
from sqlalchemy import func
from .models import User, Group
from marshmallow import fields, validates, ValidationError

class GroupSchema(ma.ModelSchema):
    permissions = fields.Function(lambda obj: obj.get_permissions())

    class Meta:
        fields = ('id', 'name', 'permissions', 'users')
        ordered = True

class UserSchema(ma.ModelSchema):
    group = ma.Nested(GroupSchema, exclude=('users',))

    class Meta:
        fields = ('id', 'firstname', 'surname', 'group')
        ordered = True

    @validates('email')
    def validate_email(self, email):
        user = User.query.filter(func.lower(User.email) == email.data.lower()).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')