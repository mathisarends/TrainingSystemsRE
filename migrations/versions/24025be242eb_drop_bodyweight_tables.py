"""drop bodyweight tables

Revision ID: 24025be242eb
Revises: b03758e3333d
Create Date: 2026-08-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '24025be242eb'
down_revision: Union[str, Sequence[str], None] = 'b03758e3333d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(op.f('ix_body_weight_goals_user_id'), table_name='body_weight_goals')
    op.drop_table('body_weight_goals')
    op.drop_index(op.f('ix_body_weight_entries_user_id'), table_name='body_weight_entries')
    op.drop_table('body_weight_entries')


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table('body_weight_entries',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('weight', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'date')
    )
    op.create_index(op.f('ix_body_weight_entries_user_id'), 'body_weight_entries', ['user_id'], unique=False)
    op.create_table('body_weight_goals',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('direction', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
    sa.Column('rate', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_body_weight_goals_user_id'), 'body_weight_goals', ['user_id'], unique=True)
