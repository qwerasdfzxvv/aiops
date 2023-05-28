from datetime import datetime
import json
import pickle
from markupsafe import escape, Markup
from flask_appbuilder import Model
from flask_appbuilder.models.decorators import renders
from sqlalchemy import Column, Float, BLOB, Date, ForeignKey, Integer, String, Table, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from . import db, appbuilder, app
from typing import List


class DeployRecord(Model):
    id = Column(Integer, primary_key=True)
    order_id = Column(String(50), ForeignKey('deploy.order_id'), nullable=False)
    deploy = relationship("Deploy")
    executor = Column(String(50), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    result = Column(Text, nullable=True)

    def __repr__(self):
        return f'{self.id}-{self.order_id}'


class Deploy(Model):
    id = Column(Integer, primary_key=True)
    order_id = Column(String(50), unique=True, nullable=False)
    executor = Column(String(50), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    # def __repr__(self):
    #     return self.order_id


class ApschedulerJobs(Model):
    __tablename__ = "apscheduler_jobs"
    id = Column(String(191), primary_key=True, nullable=False)
    next_run_time = Column(Float, nullable=True)
    job_state = Column(BLOB, nullable=False)

    def __repr__(self):
        return self.id

    @renders('next_run_time')
    def render_next_run_time(self):
        return datetime.fromtimestamp(float(str(self.next_run_time)))

    @renders('job_state')
    def render_job_state(self, ):
        return pickle.loads(self.job_state)


class JobEvent(Model):
    __tablename__ = "jobs_event"
    id = Column(Integer, primary_key=True, nullable=False)
    event_type = Column(String(50), nullable=True)
    event_msg = Column(Text, nullable=False)

    def __repr__(self):
        return self.id
