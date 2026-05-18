"""initial_schema

Revision ID: 7b403fb1c503
Revises:
Create Date: 2026-05-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7b403fb1c503'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── usuarios ──────────────────────────────────────────────────────────────
    op.create_table(
        'usuarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('nombre', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='customer'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_usuarios_email', 'usuarios', ['email'])

    # ── categorias ────────────────────────────────────────────────────────────
    op.create_table(
        'categorias',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=255), nullable=False),
        sa.Column('descripcion', sa.String(length=1000), nullable=False, server_default=''),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre'),
    )
    op.create_index('ix_categorias_nombre', 'categorias', ['nombre'])

    # ── ingredientes ──────────────────────────────────────────────────────────
    op.create_table(
        'ingredientes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=255), nullable=False),
        sa.Column('descripcion', sa.String(length=1000), nullable=False, server_default=''),
        sa.Column('unidad_medida', sa.String(length=50), nullable=False),
        sa.Column('cantidad_stock', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cantidad_minima', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cantidad_reservada', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('categoria_id', sa.Integer(), nullable=True),
        sa.Column('es_alergeno', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['categoria_id'], ['categorias.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre'),
    )
    op.create_index('ix_ingredientes_nombre', 'ingredientes', ['nombre'])

    # ── productos ─────────────────────────────────────────────────────────────
    op.create_table(
        'productos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=255), nullable=False),
        sa.Column('descripcion', sa.String(length=1000), nullable=False, server_default=''),
        sa.Column('base_price', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='active'),
        sa.Column('stock', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre'),
    )
    op.create_index('ix_productos_nombre', 'productos', ['nombre'])

    # ── producto_categoria (M2M) ──────────────────────────────────────────────
    op.create_table(
        'producto_categoria',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('producto_id', sa.Integer(), nullable=False),
        sa.Column('categoria_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['categoria_id'], ['categorias.id']),
        sa.ForeignKeyConstraint(['producto_id'], ['productos.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_producto_categoria_producto_id', 'producto_categoria', ['producto_id'])
    op.create_index('ix_producto_categoria_categoria_id', 'producto_categoria', ['categoria_id'])

    # ── producto_ingrediente (M2M) ────────────────────────────────────────────
    op.create_table(
        'producto_ingrediente',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('ingredient_id', sa.Integer(), nullable=False),
        sa.Column('quantity_required', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredientes.id']),
        sa.ForeignKeyConstraint(['product_id'], ['productos.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_producto_ingrediente_product_id', 'producto_ingrediente', ['product_id'])
    op.create_index('ix_producto_ingrediente_ingredient_id', 'producto_ingrediente', ['ingredient_id'])

    # ── clientes ──────────────────────────────────────────────────────────────
    op.create_table(
        'clientes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('telefono', sa.String(length=50), nullable=True),
        sa.Column('direccion', sa.String(length=500), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_clientes_email', 'clientes', ['email'])
    op.create_index('ix_clientes_user_id', 'clientes', ['user_id'])

    # ── direcciones_entrega ───────────────────────────────────────────────────
    op.create_table(
        'direcciones_entrega',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('calle', sa.String(length=255), nullable=False),
        sa.Column('numero', sa.String(length=50), nullable=False),
        sa.Column('ciudad', sa.String(length=100), nullable=False),
        sa.Column('provincia', sa.String(length=100), nullable=False),
        sa.Column('codigo_postal', sa.String(length=20), nullable=False),
        sa.Column('piso', sa.String(length=20), nullable=True),
        sa.Column('departamento', sa.String(length=20), nullable=True),
        sa.Column('referencia', sa.String(length=500), nullable=True),
        sa.Column('es_predeterminada', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_direcciones_entrega_cliente_id', 'direcciones_entrega', ['cliente_id'])

    # ── pedidos ───────────────────────────────────────────────────────────────
    op.create_table(
        'pedidos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('estado', sa.String(length=50), nullable=False, server_default='PENDIENTE'),
        sa.Column('direccion_snapshot', sa.String(length=2000), nullable=False, server_default=''),
        sa.Column('total', sa.Float(), nullable=False, server_default='0'),
        sa.Column('costo_envio', sa.Float(), nullable=False, server_default='0'),
        sa.Column('creado_en', sa.DateTime(), nullable=False),
        sa.Column('actualizado_en', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_pedidos_cliente_id', 'pedidos', ['cliente_id'])
    op.create_index('ix_pedidos_estado', 'pedidos', ['estado'])

    # ── detalle_pedido ────────────────────────────────────────────────────────
    op.create_table(
        'detalle_pedido',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pedido_id', sa.Integer(), nullable=False),
        sa.Column('producto_id', sa.Integer(), nullable=False),
        sa.Column('nombre_snapshot', sa.String(length=255), nullable=False),
        sa.Column('cantidad', sa.Integer(), nullable=False),
        sa.Column('precio_snapshot', sa.Float(), nullable=False),
        sa.Column('personalizacion', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('creado_en', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['pedido_id'], ['pedidos.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_detalle_pedido_pedido_id', 'detalle_pedido', ['pedido_id'])
    op.create_index('ix_detalle_pedido_producto_id', 'detalle_pedido', ['producto_id'])

    # ── historial_estado_pedido ───────────────────────────────────────────────
    op.create_table(
        'historial_estado_pedido',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pedido_id', sa.Integer(), nullable=False),
        sa.Column('estado_anterior', sa.String(length=50), nullable=True),
        sa.Column('estado_nuevo', sa.String(length=50), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('observacion', sa.String(length=1000), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['pedido_id'], ['pedidos.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_historial_estado_pedido_pedido_id', 'historial_estado_pedido', ['pedido_id'])
    op.create_index('ix_historial_estado_pedido_timestamp', 'historial_estado_pedido', ['timestamp'])

    # ── pagos ─────────────────────────────────────────────────────────────────
    op.create_table(
        'pagos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pedido_id', sa.Integer(), nullable=False),
        sa.Column('mp_payment_id', sa.String(length=100), nullable=True),
        sa.Column('mp_status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('external_reference', sa.String(length=100), nullable=False),
        sa.Column('idempotency_key', sa.String(length=100), nullable=False),
        sa.Column('creado_en', sa.DateTime(), nullable=False),
        sa.Column('actualizado_en', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['pedido_id'], ['pedidos.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('external_reference'),
        sa.UniqueConstraint('idempotency_key'),
    )
    op.create_index('ix_pagos_pedido_id', 'pagos', ['pedido_id'])
    op.create_index('ix_pagos_mp_payment_id', 'pagos', ['mp_payment_id'])


def downgrade() -> None:
    op.drop_table('pagos')
    op.drop_table('historial_estado_pedido')
    op.drop_table('detalle_pedido')
    op.drop_table('pedidos')
    op.drop_table('direcciones_entrega')
    op.drop_table('clientes')
    op.drop_table('producto_ingrediente')
    op.drop_table('producto_categoria')
    op.drop_table('productos')
    op.drop_table('ingredientes')
    op.drop_table('categorias')
    op.drop_table('usuarios')
