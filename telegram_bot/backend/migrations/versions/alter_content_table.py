"""alter_content_table — Remove text/cefr_level/order_index, restrict content_type."""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "alter_content_table"
down_revision = "init"  # Eski migration nomi; kerak bo'lsa yangilang
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Eski ustunlarni olib tashlash
    op.drop_column("content_items", "text", if_exists=True)
    op.drop_column("content_items", "cefr_level", if_exists=True)
    op.drop_column("content_items", "order_index", if_exists=True)

    # content_type ni NOT NULL cheklovi (faqat video/file)
    # Avval joriy qiymatlarni tekshirish
    conn = op.get_bind()
    res = conn.execute(sa.text("SELECT id, content_type FROM content_items WHERE content_type NOT IN ('video', 'file')"))
    rows = res.fetchall()
    if rows:
        raise RuntimeError(
            f"Noto'g'ri content_type qiymatlari topildi: {[r[1] for r in rows]}. Iltimos, avval ularni tuzating."
        )

    # Agar ustun hali NOT NULL bo'lmasa, o'zgartirish
    op.alter_column("content_items", "content_type", existing_type=sa.String(20), nullable=False)


def downgrade() -> None:
    # Eski ustunlarni qayta tiklash (nullable)
    op.add_column("content_items", sa.Column("text", sa.Text, nullable=True))
    op.add_column("content_items", sa.Column("cefr_level", sa.String(10), nullable=True))
    op.add_column("content_items", sa.Column("order_index", sa.Integer, nullable=True, server_default="0"))

    # content_type ni qayta nullable qilish
    op.alter_column("content_items", "content_type", existing_type=sa.String(20), nullable=True)