"""add_entity_tracking_tables

Revision ID: 0ff98f1962bf
Revises: 336cf1f1c6c4
Create Date: 2026-01-26 14:45:15.585490

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ff98f1962bf'
down_revision = '336cf1f1c6c4'
branch_labels = None
depends_on = None


def upgrade():
    # Create tracked_actors table
    op.create_table(
        'tracked_actors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('actor_id', sa.String(length=100), nullable=False),
        sa.Column('tracked_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['actor_id'], ['actors.actor_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'actor_id', name='uq_user_actor')
    )
    
    # Create tracked_positions table
    op.create_table(
        'tracked_positions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('position_code', sa.String(length=100), nullable=False),
        sa.Column('tracked_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['position_code'], ['positions.position_code'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'position_code', name='uq_user_position')
    )
    
    # Create tracked_institutions table
    op.create_table(
        'tracked_institutions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('institution_code', sa.String(length=100), nullable=False),
        sa.Column('tracked_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['institution_code'], ['institutions.institution_code'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'institution_code', name='uq_user_institution')
    )


def downgrade():
    op.drop_table('tracked_institutions')
    op.drop_table('tracked_positions')
    op.drop_table('tracked_actors')