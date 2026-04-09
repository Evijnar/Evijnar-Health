"""Initial migration: create all database tables

Revision ID: 20260408155133
Revises:
Create Date: 2026-04-08 15:51:33.927989

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260408155133"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types first
    user_role_enum = postgresql.ENUM('admin', 'hospital_staff', 'patient', 'physician', 'healthcare_provider', 'recovery_provider', name='userrole')
    user_role_enum.create(op.get_bind(), checkfirst=True)

    hospital_type_enum = postgresql.ENUM('SPECIALTY_CENTER', 'GENERAL_HOSPITAL', 'DIAGNOSTIC_CENTER', 'NURSING_HOME', name='hospitaltype')
    hospital_type_enum.create(op.get_bind(), checkfirst=True)

    rural_tier_enum = postgresql.ENUM('TIER1', 'TIER2', 'TIER3', name='ruraltier')
    rural_tier_enum.create(op.get_bind(), checkfirst=True)

    booking_status_enum = postgresql.ENUM('pending', 'confirmed', 'in_progress', 'completed', 'cancelled', name='bookingstatus')
    booking_status_enum.create(op.get_bind(), checkfirst=True)

    recovery_status_enum = postgresql.ENUM('pre_surgery', 'post_surgery', 'discharged', name='recoverystatus')
    recovery_status_enum.create(op.get_bind(), checkfirst=True)

    alert_severity_enum = postgresql.ENUM('info', 'warning', 'critical', name='alertseverity')
    alert_severity_enum.create(op.get_bind(), checkfirst=True)

    financing_type_enum = postgresql.ENUM('UPI_MANDATE', 'HEALTH_EMI', 'INSURANCE_CLAIM', 'DIRECT_PAYMENT', 'MICRO_LOAN', name='financingtype')
    financing_type_enum.create(op.get_bind(), checkfirst=True)

    financing_status_enum = postgresql.ENUM('pending', 'approved', 'rejected', 'disbursed', 'repayed', name='financingstatus')
    financing_status_enum.create(op.get_bind(), checkfirst=True)

    # Create user table
    op.create_table('user',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', user_role_enum, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Create audit_log table
    op.create_table('audit_log',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('resource_type', sa.String(), nullable=False),
        sa.Column('resource_id', sa.String(), nullable=False),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_audit_log_user_id', 'user_id'),
        sa.Index('ix_audit_log_resource_type_id', 'resource_type', 'resource_id'),
        sa.Index('ix_audit_log_created_at', 'created_at')
    )

    # Create price_normalizer table
    op.create_table('price_normalizer',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('cpt_code', sa.String(), nullable=False),
        sa.Column('cpt_description', sa.String(), nullable=False),
        sa.Column('icd10_code', sa.String(), nullable=False),
        sa.Column('icd10_description', sa.String(), nullable=False),
        sa.Column('uhi_code', sa.String(), nullable=True),
        sa.Column('ehds_identifier', sa.String(), nullable=True),
        sa.Column('clinical_category', sa.String(), nullable=False),
        sa.Column('complexity_score', sa.Integer(), nullable=False),
        sa.Column('us_median_cost_usd', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cpt_code')
    )

    # Create global_hospital table
    op.create_table('global_hospital',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('hospital_type', hospital_type_enum, nullable=False),
        sa.Column('country_code', sa.String(), nullable=False),
        sa.Column('state_province', sa.String(), nullable=False),
        sa.Column('city', sa.String(), nullable=False),
        sa.Column('postal_code', sa.String(), nullable=True),
        sa.Column('phone_primary', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('website_url', sa.String(), nullable=True),
        sa.Column('jci_accredited', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('jci_certificate_url', sa.String(), nullable=True),
        sa.Column('jci_expires_at', sa.DateTime(), nullable=True),
        sa.Column('nabh_accredited', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('nabh_certificate_url', sa.String(), nullable=True),
        sa.Column('nabh_expires_at', sa.DateTime(), nullable=True),
        sa.Column('avg_quality_score', sa.Float(), nullable=False, server_default='0'),
        sa.Column('complication_rate', sa.Float(), nullable=True),
        sa.Column('readmission_rate', sa.Float(), nullable=True),
        sa.Column('patient_reviews_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('price_data_source', sa.String(), nullable=False),
        sa.Column('price_data_verified_at', sa.DateTime(), nullable=False),
        sa.Column('source_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_id'),
        sa.Index('ix_global_hospital_name', 'name')
    )

    # Create procedure_price table
    op.create_table('procedure_price',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('hospital_id', sa.String(), nullable=False),
        sa.Column('normalizer_id', sa.String(), nullable=True),
        sa.Column('clinical_category', sa.String(), nullable=False),
        sa.Column('complexity_score', sa.Integer(), nullable=False),
        sa.Column('base_price', sa.Float(), nullable=False),
        sa.Column('facility_fee', sa.Float(), nullable=True),
        sa.Column('anesthesia_fee', sa.Float(), nullable=True),
        sa.Column('surgeon_fee', sa.Float(), nullable=True),
        sa.Column('currency_code', sa.String(), nullable=False, server_default='USD'),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('complication_rate', sa.Float(), nullable=True),
        sa.Column('data_source', sa.String(), nullable=False),
        sa.Column('verified_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['hospital_id'], ['global_hospital.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['normalizer_id'], ['price_normalizer.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_procedure_price_hospital_id', 'hospital_id'),
        sa.Index('ix_procedure_price_normalizer_id', 'normalizer_id')
    )

    # Create patient table
    op.create_table('patient',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('first_name_encrypted', sa.String(), nullable=False),
        sa.Column('last_name_encrypted', sa.String(), nullable=False),
        sa.Column('date_of_birth_encrypted', sa.String(), nullable=False),
        sa.Column('blood_type', sa.String(), nullable=True),
        sa.Column('allergies', sa.String(), nullable=True),
        sa.Column('chronic_conditions', sa.String(), nullable=True),
        sa.Column('current_medications', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_patient_user_id', 'user_id')
    )

    # Create medical_record table
    op.create_table('medical_record',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('patient_id', sa.String(), nullable=False),
        sa.Column('procedure_description', sa.String(), nullable=False),
        sa.Column('diagnosis_encrypted', sa.String(), nullable=False),
        sa.Column('procedure_encrypted', sa.String(), nullable=False),
        sa.Column('outcome', sa.String(), nullable=True),
        sa.Column('record_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_medical_record_patient_id', 'patient_id')
    )

    # Create department table
    op.create_table('department',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('hospital_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('specialization', sa.String(), nullable=False),
        sa.Column('head_physician_name', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['hospital_id'], ['global_hospital.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_department_hospital_id', 'hospital_id')
    )

    # Create surgeon table
    op.create_table('surgeon',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('hospital_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('specialization', sa.String(), nullable=False),
        sa.Column('experience_years', sa.Integer(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['hospital_id'], ['global_hospital.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_surgeon_hospital_id', 'hospital_id')
    )

    # Create healthcare_provider table
    op.create_table('healthcare_provider',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('hospital_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('provider_type', sa.String(), nullable=False),
        sa.Column('license_number', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['hospital_id'], ['global_hospital.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_healthcare_provider_hospital_id', 'hospital_id')
    )

    # Create hospital_booking table
    op.create_table('hospital_booking',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('patient_id', sa.String(), nullable=False),
        sa.Column('hospital_id', sa.String(), nullable=False),
        sa.Column('procedure_id', sa.String(), nullable=False),
        sa.Column('status', booking_status_enum, nullable=False),
        sa.Column('scheduled_date', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('estimated_cost', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['hospital_id'], ['global_hospital.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['procedure_id'], ['procedure_price.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_hospital_booking_patient_id', 'patient_id'),
        sa.Index('ix_hospital_booking_hospital_id', 'hospital_id'),
        sa.Index('ix_hospital_booking_status', 'status')
    )

    # Create recovery_session table
    op.create_table('recovery_session',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('patient_id', sa.String(), nullable=False),
        sa.Column('hospital_id', sa.String(), nullable=False),
        sa.Column('recovery_provider_id', sa.String(), nullable=True),
        sa.Column('status', recovery_status_enum, nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('care_protocol', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['hospital_id'], ['global_hospital.id'], ondelete='CASCADE'),
        sa.Column('recovery_provider_id', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_recovery_session_patient_id', 'patient_id'),
        sa.Index('ix_recovery_session_hospital_id', 'hospital_id'),
        sa.Index('ix_recovery_session_status', 'status')
    )

    # Create recovery_vital table
    op.create_table('recovery_vital',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('vital_type', sa.String(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('collected_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['recovery_session.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_recovery_vital_session_id', 'session_id'),
        sa.Index('ix_recovery_vital_collected_at', 'collected_at')
    )

    # Create recovery_alert table
    op.create_table('recovery_alert',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('severity', alert_severity_enum, nullable=False),
        sa.Column('alert_type', sa.String(), nullable=False),
        sa.Column('message', sa.String(), nullable=False),
        sa.Column('acknowledged', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('acknowledged_by', sa.String(), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['recovery_session.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_recovery_alert_session_id', 'session_id'),
        sa.Index('ix_recovery_alert_severity', 'severity')
    )

    # Create recovery_provider table
    op.create_table('recovery_provider',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('hospital_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('specialization', sa.String(), nullable=False),
        sa.Column('certification', sa.String(), nullable=True),
        sa.Column('experience_years', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['hospital_id'], ['global_hospital.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_recovery_provider_hospital_id', 'hospital_id')
    )

    # Create rural_financing table
    op.create_table('rural_financing',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('patient_id', sa.String(), nullable=False),
        sa.Column('hospital_id', sa.String(), nullable=False),
        sa.Column('tier', rural_tier_enum, nullable=False),
        sa.Column('financing_type', financing_type_enum, nullable=False),
        sa.Column('status', financing_status_enum, nullable=False),
        sa.Column('amount_requested', sa.Float(), nullable=False),
        sa.Column('amount_approved', sa.Float(), nullable=True),
        sa.Column('repayment_period_months', sa.Integer(), nullable=True),
        sa.Column('interest_rate_percent', sa.Float(), nullable=True),
        sa.Column('monthly_emi', sa.Float(), nullable=True),
        sa.Column('approval_date', sa.DateTime(), nullable=True),
        sa.Column('disbursement_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['patient_id'], ['patient.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['hospital_id'], ['global_hospital.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_rural_financing_patient_id', 'patient_id'),
        sa.Index('ix_rural_financing_hospital_id', 'hospital_id'),
        sa.Index('ix_rural_financing_status', 'status')
    )


def downgrade() -> None:
    # Drop tables in reverse order of creation
    op.drop_table('rural_financing')
    op.drop_table('recovery_provider')
    op.drop_table('recovery_alert')
    op.drop_table('recovery_vital')
    op.drop_table('recovery_session')
    op.drop_table('hospital_booking')
    op.drop_table('healthcare_provider')
    op.drop_table('surgeon')
    op.drop_table('department')
    op.drop_table('medical_record')
    op.drop_table('patient')
    op.drop_table('procedure_price')
    op.drop_table('global_hospital')
    op.drop_table('price_normalizer')
    op.drop_table('audit_log')
    op.drop_table('user')

    # Drop enums
    user_role_enum = postgresql.ENUM('admin', 'hospital_staff', 'patient', 'physician', 'healthcare_provider', 'recovery_provider', name='userrole')
    user_role_enum.drop(op.get_bind(), checkfirst=True)

    hospital_type_enum = postgresql.ENUM('SPECIALTY_CENTER', 'GENERAL_HOSPITAL', 'DIAGNOSTIC_CENTER', 'NURSING_HOME', name='hospitaltype')
    hospital_type_enum.drop(op.get_bind(), checkfirst=True)

    rural_tier_enum = postgresql.ENUM('TIER1', 'TIER2', 'TIER3', name='ruraltier')
    rural_tier_enum.drop(op.get_bind(), checkfirst=True)

    booking_status_enum = postgresql.ENUM('pending', 'confirmed', 'in_progress', 'completed', 'cancelled', name='bookingstatus')
    booking_status_enum.drop(op.get_bind(), checkfirst=True)

    recovery_status_enum = postgresql.ENUM('pre_surgery', 'post_surgery', 'discharged', name='recoverystatus')
    recovery_status_enum.drop(op.get_bind(), checkfirst=True)

    alert_severity_enum = postgresql.ENUM('info', 'warning', 'critical', name='alertseverity')
    alert_severity_enum.drop(op.get_bind(), checkfirst=True)

    financing_type_enum = postgresql.ENUM('UPI_MANDATE', 'HEALTH_EMI', 'INSURANCE_CLAIM', 'DIRECT_PAYMENT', 'MICRO_LOAN', name='financingtype')
    financing_type_enum.drop(op.get_bind(), checkfirst=True)

    financing_status_enum = postgresql.ENUM('pending', 'approved', 'rejected', 'disbursed', 'repayed', name='financingstatus')
    financing_status_enum.drop(op.get_bind(), checkfirst=True)
