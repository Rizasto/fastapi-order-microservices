from __future__ import annotations

import asyncio
import logging

from app.db.models.permission import Permission
from app.db.models.role import Role, RolePermission
from app.db.session import async_session_maker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROLES: list[dict] = [
    {
        "name": "user",
        "description": "Regular user",
    },
    {
        "name": "manager",
        "description": "Manager with access to catalog and all orders",
    },
    {
        "name": "admin",
        "description": "Administrator with full access",
    },
]

PERMISSIONS: list[dict] = [
    {"code": "catalog:view", "description": "View product catalog"},
    {"code": "catalog:create", "description": "Create product"},
    {"code": "catalog:update", "description": "Update product"},
    {"code": "catalog:delete", "description": "Delete product"},
    {"code": "orders:create", "description": "Create order"},
    {"code": "orders:view_own", "description": "View own orders"},
    {"code": "orders:view_all", "description": "View all orders"},
    {"code": "orders:cancel_own", "description": "Cancel own orders"},
    {"code": "orders:update_status", "description": "Update order status"},
    {"code": "users:view_self", "description": "View own profile"},
    {"code": "users:view_all", "description": "View all users"},
    {"code": "users:create", "description": "Create user"},
    {"code": "users:update", "description": "Update user"},
    {"code": "users:delete", "description": "Delete user"},
    {"code": "roles:view", "description": "View roles"},
    {"code": "roles:create", "description": "Create role"},
    {"code": "roles:update", "description": "Update role"},
    {"code": "roles:assign", "description": "Assign role to user"},
]

ROLE_PERMISSIONS: dict[str, list[str]] = {
    "user": [
        "catalog:view",
        "orders:create",
        "orders:view_own",
        "orders:cancel_own",
        "users:view_self",
    ],
    "manager": [
        "catalog:view",
        "catalog:create",
        "catalog:update",
        "orders:create",
        "orders:view_own",
        "orders:view_all",
        "orders:cancel_own",
        "orders:update_status",
        "users:view_self",
    ],
    "admin": [
        "catalog:view",
        "catalog:create",
        "catalog:update",
        "catalog:delete",
        "orders:create",
        "orders:view_own",
        "orders:view_all",
        "orders:cancel_own",
        "orders:update_status",
        "users:view_self",
        "users:view_all",
        "users:create",
        "users:update",
        "users:delete",
        "roles:view",
        "roles:create",
        "roles:update",
        "roles:assign",
    ],
}


async def get_role_by_name(session: AsyncSession, role_name: str) -> Role | None:
    stmt = select(Role).where(Role.name == role_name)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_permission_by_code(
    session: AsyncSession,
    permission_code: str,
) -> Permission | None:
    stmt = select(Permission).where(Permission.code == permission_code)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def role_permission_exists(
    session: AsyncSession,
    role_id: int,
    permission_id: int,
) -> bool:
    stmt = select(RolePermission).where(
        RolePermission.role_id == role_id,
        RolePermission.permission_id == permission_id,
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none() is not None


async def seed_roles(session: AsyncSession) -> None:
    for role_data in ROLES:
        existing_role = await get_role_by_name(session, role_data["name"])
        if existing_role:
            logger.info("Role already exists: %s", role_data["name"])
            continue

        session.add(
            Role(
                name=role_data["name"],
                description=role_data["description"],
            )
        )
        logger.info("Created role: %s", role_data["name"])

    await session.commit()


async def seed_permissions(session: AsyncSession) -> None:
    for permission_data in PERMISSIONS:
        existing_permission = await get_permission_by_code(
            session,
            permission_data["code"],
        )
        if existing_permission:
            logger.info("Permission already exists: %s", permission_data["code"])
            continue

        session.add(
            Permission(
                code=permission_data["code"],
                description=permission_data["description"],
            )
        )
        logger.info("Created permission: %s", permission_data["code"])

    await session.commit()


async def seed_role_permissions(session: AsyncSession) -> None:
    for role_name, permission_codes in ROLE_PERMISSIONS.items():
        role = await get_role_by_name(session, role_name)
        if not role:
            raise ValueError(f"Role '{role_name}' not found in database")

        for permission_code in permission_codes:
            permission = await get_permission_by_code(session, permission_code)
            if not permission:
                raise ValueError(f"Permission '{permission_code}' not found in database")

            exists = await role_permission_exists(session, role.id, permission.id)
            if exists:
                logger.info(
                    "RolePermission already exists: role=%s permission=%s",
                    role_name,
                    permission_code,
                )
                continue

            session.add(
                RolePermission(
                    role_id=role.id,
                    permission_id=permission.id,
                )
            )
            logger.info(
                "Created RolePermission: role=%s permission=%s",
                role_name,
                permission_code,
            )

    await session.commit()


async def seed_rbac() -> None:
    logger.info("Starting RBAC seeding...")

    async with async_session_maker() as session:
        await seed_roles(session)
        await seed_permissions(session)
        await seed_role_permissions(session)

    logger.info("RBAC seeding completed successfully")


if __name__ == "__main__":
    asyncio.run(seed_rbac())
