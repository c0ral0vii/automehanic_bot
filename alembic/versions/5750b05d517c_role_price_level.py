"""role & price level

Revision ID: 5750b05d517c
Revises: a29f1a194eff
Create Date: 2024-10-21 00:53:38.873664

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5750b05d517c'
down_revision: Union[str, None] = 'a29f1a194eff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

role_enum = sa.Enum('ADMIN', 'USER', 'UNDEFINED', 'CANCELLED', name='role')
price_level_enum = sa.Enum('DEFAULT', 'FIRST', 'SECOND', 'THIRD', 'FOURTH', name='price_level')

def upgrade() -> None:
    role_enum.create(op.get_bind(), checkfirst=True)
    price_level_enum.create(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    pass
