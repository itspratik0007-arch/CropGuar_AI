"""upgrade_database_schema_plant_assistant

Revision ID: c84920e51fa2
Revises: 0650b38296c8
Create Date: 2026-10-26 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c84920e51fa2'
down_revision: Union[str, None] = '0650b38296c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update users table with preferences
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('preferences', sa.Text(), nullable=True, server_default='{}'))

    # 2. Update plants table with botanical agronomic attributes
    with op.batch_alter_table('plants', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category', sa.String(length=100), nullable=True, server_default='Crop'))
        batch_op.add_column(sa.Column('temperature_range', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('fertilizer', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('season', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('common_diseases', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('common_pests', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('prevention_treatment', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('data_source', sa.String(length=255), nullable=True, server_default='Curated Botanical Knowledgebase'))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
        batch_op.create_index('ix_plants_family', ['family'], unique=False)
        batch_op.create_index('ix_plants_category', ['category'], unique=False)

    # 3. Create plant_conversations table
    op.create_table(
        'plant_conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('plant_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False, server_default='Plant Inquiry'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['plant_id'], ['plants.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_plant_conversations_id'), 'plant_conversations', ['id'], unique=False)
    op.create_index(op.f('ix_plant_conversations_user_id'), 'plant_conversations', ['user_id'], unique=False)
    op.create_index(op.f('ix_plant_conversations_plant_id'), 'plant_conversations', ['plant_id'], unique=False)
    op.create_index(op.f('ix_plant_conversations_created_at'), 'plant_conversations', ['created_at'], unique=False)
    op.create_index(op.f('ix_plant_conversations_updated_at'), 'plant_conversations', ['updated_at'], unique=False)
    op.create_index('ix_conversations_user_updated', 'plant_conversations', ['user_id', 'updated_at'], unique=False)

    # 4. Create conversation_messages table
    op.create_table(
        'conversation_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('model_metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['plant_conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_messages_id'), 'conversation_messages', ['id'], unique=False)
    op.create_index(op.f('ix_conversation_messages_conversation_id'), 'conversation_messages', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_conversation_messages_created_at'), 'conversation_messages', ['created_at'], unique=False)
    op.create_index('ix_messages_conv_created', 'conversation_messages', ['conversation_id', 'created_at'], unique=False)

    # 5. Update disease_detections with plant_id foreign key reference & indexes
    with op.batch_alter_table('disease_detections', schema=None) as batch_op:
        batch_op.add_column(sa.Column('plant_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_disease_detections_plant_id', 'plants', ['plant_id'], ['id'], ondelete='SET NULL')
        batch_op.create_index(op.f('ix_disease_detections_plant_id'), ['plant_id'], unique=False)
        batch_op.create_index(op.f('ix_disease_detections_created_at'), ['created_at'], unique=False)

    # 6. Add composite index to bookmarks
    with op.batch_alter_table('bookmarks', schema=None) as batch_op:
        batch_op.create_index('ix_bookmarks_user_plant', ['user_id', 'plant_id'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('bookmarks', schema=None) as batch_op:
        batch_op.drop_index('ix_bookmarks_user_plant')

    with op.batch_alter_table('disease_detections', schema=None) as batch_op:
        batch_op.drop_index(op.f('ix_disease_detections_created_at'))
        batch_op.drop_index(op.f('ix_disease_detections_plant_id'))
        batch_op.drop_constraint('fk_disease_detections_plant_id', type_='foreignkey')
        batch_op.drop_column('plant_id')

    op.drop_table('conversation_messages')
    op.drop_table('plant_conversations')

    with op.batch_alter_table('plants', schema=None) as batch_op:
        batch_op.drop_index('ix_plants_category')
        batch_op.drop_index('ix_plants_family')
        batch_op.drop_column('updated_at')
        batch_op.drop_column('data_source')
        batch_op.drop_column('prevention_treatment')
        batch_op.drop_column('common_pests')
        batch_op.drop_column('common_diseases')
        batch_op.drop_column('season')
        batch_op.drop_column('fertilizer')
        batch_op.drop_column('temperature_range')
        batch_op.drop_column('category')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('preferences')
