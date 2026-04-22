import logging
import time
from typing import Optional
import uuid

from sqlalchemy.orm import Session
from arkive.internal.db import Base, get_db_context

from pydantic import BaseModel, ConfigDict
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Integer,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID

log = logging.getLogger(__name__)

####################
# UsagePolicy DB Schema
####################


class UsagePolicy(Base):
    __tablename__ = 'usage_policies'

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(Text, nullable=False)
    max_messages_per_day = Column(Integer, nullable=True)
    max_file_size_mb = Column(Integer, nullable=True)
    allowed_model_ids = Column(ARRAY(Text), nullable=False, default=list)
    can_query_confidential = Column(Boolean, nullable=False, default=False)
    can_export = Column(Boolean, nullable=False, default=False)
    can_upload = Column(Boolean, nullable=False, default=True)
    requires_review_above_clearance = Column(Integer, nullable=False, default=2)
    created_at = Column(BigInteger, nullable=False)
    updated_at = Column(BigInteger, nullable=False)


class UsagePolicyModel(BaseModel):
    id: uuid.UUID
    name: str
    max_messages_per_day: Optional[int] = None
    max_file_size_mb: Optional[int] = None
    allowed_model_ids: list[str] = []
    can_query_confidential: bool = False
    can_export: bool = False
    can_upload: bool = True
    requires_review_above_clearance: int = 2
    created_at: int  # timestamp in epoch
    updated_at: int  # timestamp in epoch

    model_config = ConfigDict(from_attributes=True)


####################
# Forms
####################


class UsagePolicyForm(BaseModel):
    name: str
    max_messages_per_day: Optional[int] = None
    max_file_size_mb: Optional[int] = None
    allowed_model_ids: list[str] = []
    can_query_confidential: bool = False
    can_export: bool = False
    can_upload: bool = True
    requires_review_above_clearance: int = 2


class UsagePoliciesTable:
    def insert_new_usage_policy(
        self, form_data: UsagePolicyForm, db: Optional[Session] = None
    ) -> Optional[UsagePolicyModel]:
        with get_db_context(db) as db:
            try:
                now = int(time.time())
                policy = UsagePolicy(
                    id=uuid.uuid4(),
                    **form_data.model_dump(),
                    created_at=now,
                    updated_at=now,
                )
                db.add(policy)
                db.commit()
                db.refresh(policy)
                return UsagePolicyModel.model_validate(policy)
            except Exception as e:
                log.exception(f'Error creating usage policy: {e}')
                return None

    def get_usage_policy_by_id(
        self, id: uuid.UUID, db: Optional[Session] = None
    ) -> Optional[UsagePolicyModel]:
        try:
            with get_db_context(db) as db:
                policy = db.query(UsagePolicy).filter_by(id=id).first()
                return UsagePolicyModel.model_validate(policy) if policy else None
        except Exception:
            return None

    def get_all_usage_policies(
        self, db: Optional[Session] = None
    ) -> list[UsagePolicyModel]:
        with get_db_context(db) as db:
            policies = (
                db.query(UsagePolicy)
                .order_by(UsagePolicy.updated_at.desc())
                .all()
            )
            return [UsagePolicyModel.model_validate(p) for p in policies]

    def update_usage_policy_by_id(
        self,
        id: uuid.UUID,
        form_data: UsagePolicyForm,
        db: Optional[Session] = None,
    ) -> Optional[UsagePolicyModel]:
        try:
            with get_db_context(db) as db:
                db.query(UsagePolicy).filter_by(id=id).update(
                    {
                        **form_data.model_dump(),
                        'updated_at': int(time.time()),
                    }
                )
                db.commit()
                return self.get_usage_policy_by_id(id=id, db=db)
        except Exception as e:
            log.exception(f'Error updating usage policy: {e}')
            return None

    def delete_usage_policy_by_id(
        self, id: uuid.UUID, db: Optional[Session] = None
    ) -> bool:
        try:
            with get_db_context(db) as db:
                db.query(UsagePolicy).filter_by(id=id).delete()
                db.commit()
                return True
        except Exception:
            return False


UsagePolicies = UsagePoliciesTable()
