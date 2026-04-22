"""Add policy and classification tables

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-04-17 21:45:00.000000

Adds four tables for Layer 2 (identity/access/policy) and document
classification:
- usage_policies: named policy bundles (limits + capabilities)
- user_policies: per-user attributes (department, clearance, geo) + policy link
- document_classifications: per-file sensitivity/entity/topic metadata
- policy_decisions: append-only audit log of policy evaluations

Note: user.id and file.id in this codebase are Text (varchar), not UUID.
FK columns referencing them use sa.Text() to match. Primary keys on the
new tables use native PostgreSQL UUID with gen_random_uuid() default.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from arkive.migrations.util import get_existing_tables

revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    existing_tables = set(get_existing_tables())

    if 'usage_policies' not in existing_tables:
        op.create_table(
            'usage_policies',
            sa.Column(
                'id',
                postgresql.UUID(as_uuid=True),
                nullable=False,
                primary_key=True,
                server_default=sa.text('gen_random_uuid()'),
            ),
            sa.Column('name', sa.Text(), nullable=False),
            sa.Column('max_messages_per_day', sa.Integer(), nullable=True),
            sa.Column('max_file_size_mb', sa.Integer(), nullable=True),
            sa.Column(
                'allowed_model_ids',
                postgresql.ARRAY(sa.Text()),
                nullable=False,
                server_default=sa.text("ARRAY[]::text[]"),
            ),
            sa.Column(
                'can_query_confidential',
                sa.Boolean(),
                nullable=False,
                server_default=sa.text('false'),
            ),
            sa.Column(
                'can_export',
                sa.Boolean(),
                nullable=False,
                server_default=sa.text('false'),
            ),
            sa.Column(
                'can_upload',
                sa.Boolean(),
                nullable=False,
                server_default=sa.text('true'),
            ),
            sa.Column(
                'requires_review_above_clearance',
                sa.Integer(),
                nullable=False,
                server_default=sa.text('2'),
            ),
            sa.Column('created_at', sa.BigInteger(), nullable=False),
            sa.Column('updated_at', sa.BigInteger(), nullable=False),
        )

    if 'user_policies' not in existing_tables:
        op.create_table(
            'user_policies',
            sa.Column('user_id', sa.Text(), nullable=False, primary_key=True),
            sa.Column('department', sa.Text(), nullable=True),
            sa.Column(
                'clearance_level',
                sa.Integer(),
                nullable=False,
                server_default=sa.text('0'),
            ),
            sa.Column('geo_zone', sa.Text(), nullable=True),
            sa.Column('usage_policy_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column(
                'allowed_collection_ids',
                postgresql.ARRAY(sa.Text()),
                nullable=False,
                server_default=sa.text("ARRAY[]::text[]"),
            ),
            sa.Column(
                'can_export',
                sa.Boolean(),
                nullable=False,
                server_default=sa.text('false'),
            ),
            sa.Column(
                'can_upload',
                sa.Boolean(),
                nullable=False,
                server_default=sa.text('true'),
            ),
            sa.Column('updated_at', sa.BigInteger(), nullable=False),
            sa.ForeignKeyConstraint(
                ['user_id'],
                ['user.id'],
                name='fk_user_policies_user_id',
                ondelete='CASCADE',
            ),
            sa.ForeignKeyConstraint(
                ['usage_policy_id'],
                ['usage_policies.id'],
                name='fk_user_policies_usage_policy_id',
                ondelete='SET NULL',
            ),
        )
        op.create_index(
            'idx_user_policies_usage_policy_id',
            'user_policies',
            ['usage_policy_id'],
        )

    if 'document_classifications' not in existing_tables:
        op.create_table(
            'document_classifications',
            sa.Column(
                'id',
                postgresql.UUID(as_uuid=True),
                nullable=False,
                primary_key=True,
                server_default=sa.text('gen_random_uuid()'),
            ),
            sa.Column('file_id', sa.Text(), nullable=False, unique=True),
            sa.Column(
                'sensitivity_level',
                sa.Integer(),
                nullable=False,
                server_default=sa.text('0'),
            ),
            sa.Column(
                'detected_entities',
                sa.JSON(),
                nullable=False,
                server_default=sa.text("'[]'::json"),
            ),
            sa.Column(
                'topic_labels',
                postgresql.ARRAY(sa.Text()),
                nullable=False,
                server_default=sa.text("ARRAY[]::text[]"),
            ),
            sa.Column(
                'classification_source',
                sa.Text(),
                nullable=False,
                server_default=sa.text("'auto'"),
            ),
            sa.Column('classified_at', sa.BigInteger(), nullable=False),
            sa.Column('updated_at', sa.BigInteger(), nullable=False),
            sa.ForeignKeyConstraint(
                ['file_id'],
                ['file.id'],
                name='fk_document_classifications_file_id',
                ondelete='CASCADE',
            ),
        )
        op.create_index(
            'idx_document_classifications_sensitivity',
            'document_classifications',
            ['sensitivity_level'],
        )

    if 'policy_decisions' not in existing_tables:
        op.create_table(
            'policy_decisions',
            sa.Column(
                'id',
                postgresql.UUID(as_uuid=True),
                nullable=False,
                primary_key=True,
                server_default=sa.text('gen_random_uuid()'),
            ),
            sa.Column('user_id', sa.Text(), nullable=True),
            sa.Column('team_id', sa.Text(), nullable=True),
            sa.Column('query_hash', sa.Text(), nullable=False),
            sa.Column(
                'detected_entities',
                sa.JSON(),
                nullable=False,
                server_default=sa.text("'[]'::json"),
            ),
            sa.Column('sensitivity_level', sa.Integer(), nullable=True),
            sa.Column('decision', sa.Text(), nullable=False),
            sa.Column('reason', sa.Text(), nullable=True),
            sa.Column('created_at', sa.BigInteger(), nullable=False),
            sa.ForeignKeyConstraint(
                ['user_id'],
                ['user.id'],
                name='fk_policy_decisions_user_id',
                ondelete='SET NULL',
            ),
        )
        op.create_index(
            'idx_policy_decisions_user_id',
            'policy_decisions',
            ['user_id'],
        )
        op.create_index(
            'idx_policy_decisions_created_at',
            'policy_decisions',
            ['created_at'],
        )
        op.create_index(
            'idx_policy_decisions_decision',
            'policy_decisions',
            ['decision'],
        )

        # Append-only: block UPDATE and DELETE at the database level.
        op.execute(
            'CREATE RULE no_update_policy_decisions AS '
            'ON UPDATE TO policy_decisions DO INSTEAD NOTHING'
        )
        op.execute(
            'CREATE RULE no_delete_policy_decisions AS '
            'ON DELETE TO policy_decisions DO INSTEAD NOTHING'
        )


def downgrade() -> None:
    op.execute('DROP RULE IF EXISTS no_delete_policy_decisions ON policy_decisions')
    op.execute('DROP RULE IF EXISTS no_update_policy_decisions ON policy_decisions')

    op.drop_index('idx_policy_decisions_decision', table_name='policy_decisions')
    op.drop_index('idx_policy_decisions_created_at', table_name='policy_decisions')
    op.drop_index('idx_policy_decisions_user_id', table_name='policy_decisions')
    op.drop_table('policy_decisions')

    op.drop_index(
        'idx_document_classifications_sensitivity',
        table_name='document_classifications',
    )
    op.drop_table('document_classifications')

    op.drop_index('idx_user_policies_usage_policy_id', table_name='user_policies')
    op.drop_table('user_policies')

    op.drop_table('usage_policies')
