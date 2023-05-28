import json
import logging

from flask import render_template, flash, abort, redirect
from flask_appbuilder import ModelView, MasterDetailView
from flask_appbuilder.fields import QuerySelectField

from flask_appbuilder.fieldwidgets import Select2Widget, Select2AJAXWidget
from flask_appbuilder.widgets import ListWidget
from flask_appbuilder.models.sqla.interface import SQLAInterface
import requests
import uuid
from wtforms import SelectField, validators
from datetime import datetime, timedelta

from flask_appbuilder.widgets import ListLinkWidget
import loguru

from . import db, appbuilder, app
from .models import Deploy, ApschedulerJobs, DeployRecord, JobEvent
from .validateor import StartTimeValidator, OrderIDValidtor
import random
import requests


def order_query():
    data = [{'queue_id': 'd173C5Bf-3d3c-eDBf-CB6c-7dcfEAFe6CD1', 'deploy_status': '0',
             'id': 'd173C5Bf-3d3c-eDBf-CB6c-7dcfEAFe6CD1a'},
            {'queue_id': '9eE9FDaC-bBc3-C7C9-711c-BDABdAe699Bc', 'deploy_status': '0',
             'id': '9eE9FDaC-bBc3-C7C9-711c-BDABdAe699Bca'},
            {'queue_id': 'a6fFB8a8-9F4D-32F4-7b6D-4CB0f2C43cBa', 'deploy_status': '0',
             'id': 'a6fFB8a8-9F4D-32F4-7b6D-4CB0f2C43cBaa'},
            {'queue_id': 'd40D8d2e-b66b-2D84-4f61-24CA3e5fBDFb', 'deploy_status': '0',
             'id': 'd40D8d2e-b66b-2D84-4f61-24CA3e5fBDFba'},
            {'queue_id': 'be8DCFCA-9Eb0-7Db4-dA2b-BcD7BA8ddb5f', 'deploy_status': '0',
             'id': 'be8DCFCA-9Eb0-7Db4-dA2b-BcD7BA8ddb5fa'}]

    data = [i['queue_id'] for i in data]

    return data


def request_mock(*args, **kwargs):
    response = requests.get('http://127.0.0.1:4523/m1/2415682-0-default/pet/{0}'.format(kwargs.get('order_id'))).json()
    print(args, response)
    print(app.scheduler.print_jobs())


class JobEventView(ModelView):
    # base_permissions = ['can_list', 'can_show']
    datamodel = SQLAInterface(JobEvent)
    list_columns = ["id", "event_type", 'event_msg']


class DeployRecordView(ModelView):
    base_permissions = ['can_list', 'can_show']
    datamodel = SQLAInterface(DeployRecord)

    list_columns = ["id", "order_id", 'executor', "start_time", 'end_time', 'result']
    list_title = '布署记录'
    show_title = 'Y'


class DeployView(ModelView):
    datamodel = SQLAInterface(Deploy)
    related_views = [DeployRecordView]
    # show_template = "appbuilder/general/model/show_cascade.html"
    # edit_template = "appbuilder/general/model/edit_cascade.html"

    # base_permissions = ['can_add', 'can_show']
    list_columns = ["id", "order_id", 'executor', "start_time", 'end_time']
    validators_columns = {
        "start_time": [validators.DataRequired(), StartTimeValidator()],
        'end_time': [validators.DataRequired()],
        'order_id': [validators.DataRequired(), OrderIDValidtor()]
    }

    add_form_extra_fields = {
        'order_id': QuerySelectField(
            'order_id',
            query_func=order_query,
            get_pk_func=lambda x: x,
            get_label=lambda x: x,
            allow_blank=True,
            widget=Select2Widget(extra_classes='readonly'),
        )
    }
    edit_form_extra_fields = add_form_extra_fields

    def post_add(self, item: "Deploy"):
        self._post_add_update(item=item)

    def post_update(self, item: "Deploy"):
        self._post_add_update(item=item)

    @staticmethod
    def _post_add_update(item: "Deploy"):
        try:
            app.scheduler.add_job(
                func=request_mock,
                trigger='date',
                run_date=item.start_time,
                kwargs={'order_id': item.order_id},
                id=str(item.order_id),
                replace_existing=True
            )
            loguru.logger.info('添加任务成功')
        except Exception as ex:
            logging.exception(f'添加任务失败：order_id{item.order_id},异常信息：{ex}')
            flash(f'添加任务失败：order_id{item.order_id},异常信息：{ex}', 'error')

    def post_delete(self, item: Deploy):
        try:
            app.scheduler.remove_job(job_id=str(item.order_id))
        except Exception as ex:
            logging.exception(f'删除任务异常：{ex}')
            flash(f'调度任务删除异常', "danger")


class ApschedulerJobsView(ModelView):
    datamodel = SQLAInterface(ApschedulerJobs)
    list_columns = ['render_next_run_time', 'render_job_state']
    show_columns = list_columns


#
# from flask import session, flash
# from flask import abort, current_app, flash, g, redirect, request, session, url_for
#
@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return redirect("/")


#
# @appbuilder.app.errorhandler(500)
# def page_not_foundx(e):
#     flash("An error occurred", "danger")
#     print(e)
#     return redirect("/")


# db.create_all()

appbuilder.add_view(DeployView, "EmployeeHistoryView")
appbuilder.add_view(ApschedulerJobsView, "ApschedulerJobsView")
appbuilder.add_view(DeployRecordView, "DeployRecordView")
appbuilder.add_view(JobEventView, "JobEventView")

from .utils import json_iso_dttm_ser


def my_listener(event):
    print(event.__dict__)
    print(type(event))
    job_event = JobEvent()
    job_event.event_type = event.__class__.__name__
    job_event.event_msg = json.dumps(event.__dict__, default=json_iso_dttm_ser)
    try:
        db.session.add(job_event)
        db.session.commit()
    except Exception as ex:
        loguru.logger.exception(ex)
    # if event.exception:
    #     print('The job crashed :(')
    # else:
    #     print('The job worked :)')
