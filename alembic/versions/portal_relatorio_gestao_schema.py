"""portal relatorio gestao schema

Revision ID: portal_relatorio_gestao
Revises: df72b10ec0f3
Create Date: 2026-10-26 16:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from src.resources.database import Base
import src.models

revision: str = 'portal_relatorio_gestao'
down_revision: Union[str, Sequence[str], None] = 'df72b10ec0f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind)

def downgrade() -> None:
    pass
