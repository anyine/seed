from flask import request, g

from sqlalchemy import and_, or_

from seed.schema.base import BaseSchema
from seed.api.endpoints._base import RestfulBaseView
from seed.models import Bussiness as BussinessModel
from seed.models import BUser
from seed.models import BManager as BManagerModel


class BussinessSchema(BaseSchema):
    class Meta:
        model = BussinessModel


class BManagerSchema(BaseSchema):
    class Meta:
        model = BManagerModel


class Bussiness(RestfulBaseView):
    """ bussiness
    """
    model_class = BussinessModel
    schema_class = BussinessSchema

    def get(self, bussiness_id=None):
        """ GET
        """
        if bussiness_id:
            data = self.session.query(
                self.model_class
            ).filter_by(bussiness_id=bussiness_id).first()
            data = data.row2dict() if data else {}
            return self.response_json(self.HttpErrorCode.SUCCESS, data=data)
        else:
            # 所有业务
            all_datas = self.session.query(self.model_class).all()
            all_datas = [data.row2dict() for data in all_datas]

            if g.user.role == 'super_admin':
                # 所有权限
                for data in all_datas:
                    data.update({'edit': True, 'delete': True})
                permission_datas = all_datas
                un_permission_datas = []

            else:
                # 管理的业务
                order_datas = self.session.query(self.model_class)\
                .join(BManagerModel, self.model_class.id==BManagerModel.bussiness_id)\
                .filter(BManagerModel.user_id==g.user.id)\
                .all()
                order_datas = [data.row2dict() for data in order_datas]
                for data in order_datas:
                    data.update({'edit': True, 'delete': False})

                # 有权限的业务
                permission_datas = self.session.query(self.model_class)\
                .join(BUser, self.model_class.id==BUser.bussiness_id)\
                .filter(BUser.user_id==g.user.id)\
                .all()
                permission_ids = [data.id for data in permission_datas]
                permission_datas = [data.row2dict() for data in permission_datas]
                for data in permission_datas:
                    data.update({'edit': False, 'delete': False})

                permission_datas = [data for data in order_datas if data['id'] not in permission_ids]
                permission_datas = order_datas + permission_datas
                permission_ids = [data['id'] for data in permission_datas]

                un_permission_datas = [data for data in all_datas if data['id'] not in permission_ids]

            datas = {'my_bussiness': permission_datas, 'other_bussiness': un_permission_datas}

            return self.response_json(self.HttpErrorCode.SUCCESS, data=datas)

    def post(self):
        """ POST
        """
        input_json = request.get_json()

        schema = self.schema_class()
        bussiness, errors = schema.load(input_json)

        if errors:
            return self.response_json(self.HttpErrorCode.PARAMS_VALID_ERROR, msg=errors)
        bussiness.save()

        # 管理员增改删
        managers = input_json.get('managers', [])
        for manager in managers:
            manager['bussiness_id'] = bussiness.id

        common_batch_crud(BManagerSchema, managers)

        return self.response_json(self.HttpErrorCode.SUCCESS, data={'bussiness_id': bussiness.id})

    put = post


def common_batch_crud(schema, datas):
    """ 批量做增改删操作
    """
    # 删除多余的数据
    schema_instance = schema()
    delete_datas = [data for data in datas if data.get('status') == -1]
    delete_datas, errors = schema_instance.load(delete_datas, many=True)
    if errors:
        raise Exception(errors)
    [delete_data.delete() for delete_data in delete_datas]

    # 新增和修改数据
    modify_datas = [data for data in datas if data.get('status') != -1]
    modify_datas, errors = schema_instance.load(modify_datas, many=True)
    if errors:
        raise Exception(errors)
    [modify_data.save() for modify_data in modify_datas]

    datas = [modify_data.row2dict() for modify_data in modify_datas]
    return datas
