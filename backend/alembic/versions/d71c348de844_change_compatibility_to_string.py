"""change_compatibility_to_string

Revision ID: d71c348de844
Revises: 9625f626fc4a
Create Date: 2026-09-02 19:19:22.306381

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd71c348de844'
down_revision: Union[str, Sequence[str], None] = '9625f626fc4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Change maintenance_compatibility.compatibility from BOOLEAN to VARCHAR(50).

    The dataset uses string values COMPATIBLE and CONDITIONAL which cannot be
    represented as a boolean without semantic loss. The table is empty at the
    time of this migration so no data conversion is required.
    """
    op.alter_column(
        'maintenance_compatibility',
        'compatibility',
        existing_type=sa.BOOLEAN(),
        type_=sa.String(length=50),
        existing_nullable=False,
        existing_server_default=sa.text('true'),
        server_default=None,
    )


def downgrade() -> None:
    """Revert maintenance_compatibility.compatibility from VARCHAR(50) to BOOLEAN."""
    op.alter_column(
        'maintenance_compatibility',
        'compatibility',
        existing_type=sa.String(length=50),
        type_=sa.BOOLEAN(),
        existing_nullable=False,
        postgresql_using='compatibility::boolean',
    )
