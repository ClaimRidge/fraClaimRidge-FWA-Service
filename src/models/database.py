import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, Integer, Table, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import enum

class Base(DeclarativeBase):
    pass

class Severity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class CaseStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED_FRAUD = "RESOLVED_FRAUD"
    RESOLVED_LEGITIMATE = "RESOLVED_LEGITIMATE"
    CLOSED = "CLOSED"

# Many-to-many relationship between Cases and Flags
case_flags = Table(
    "case_flags",
    Base.metadata,
    Column("case_id", UUID(as_uuid=True), ForeignKey("fraud_cases.id"), primary_key=True),
    Column("flag_id", UUID(as_uuid=True), ForeignKey("fraud_flags.id"), primary_key=True),
)

class FraudScore(Base):
    __tablename__ = "fraud_scores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    claim_id: Mapped[str] = mapped_column(String, index=True)
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    
    # Layer scores
    l1_anomaly_score: Mapped[float] = mapped_column(Float, nullable=True)
    l2_drift_score: Mapped[float] = mapped_column(Float, nullable=True)
    l3_graph_score: Mapped[float] = mapped_column(Float, nullable=True)
    l4_timeseries_score: Mapped[float] = mapped_column(Float, nullable=True)
    
    composite_score: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class FraudFlag(Base):
    __tablename__ = "fraud_flags"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    
    layer: Mapped[str] = mapped_column(String)  # L1, L2, L3, L4
    severity: Mapped[Severity] = mapped_column(SQLEnum(Severity))
    confidence: Mapped[float] = mapped_column(Float)
    
    entity_type: Mapped[str] = mapped_column(String)  # CLAIM, PROVIDER, MEMBER
    entity_id: Mapped[str] = mapped_column(String, index=True)
    
    description: Mapped[str] = mapped_column(String)
    evidence: Mapped[Dict[str, Any]] = mapped_column(JSONB, default={})
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    cases: Mapped[List["FraudCase"]] = relationship(
        "FraudCase", secondary=case_flags, back_populates="flags"
    )

class FraudCase(Base):
    __tablename__ = "fraud_cases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    
    title: Mapped[str] = mapped_column(String)
    status: Mapped[CaseStatus] = mapped_column(SQLEnum(CaseStatus), default=CaseStatus.OPEN)
    severity: Mapped[Severity] = mapped_column(SQLEnum(Severity))
    
    investigator_id: Mapped[Optional[str]] = mapped_column(String, index=True, nullable=True)
    
    summary: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSONB, default={})
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    flags: Mapped[List["FraudFlag"]] = relationship(
        "FraudFlag", secondary=case_flags, back_populates="cases"
    )

class FraudAuditLog(Base):
    __tablename__ = "fraud_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    
    action: Mapped[str] = mapped_column(String)
    entity_type: Mapped[str] = mapped_column(String)
    entity_id: Mapped[str] = mapped_column(String)
    
    actor_id: Mapped[str] = mapped_column(String)
    details: Mapped[Dict[str, Any]] = mapped_column(JSONB, default={})
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
