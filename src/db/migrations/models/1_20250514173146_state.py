from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `state` (
    `id` CHAR(36) NOT NULL PRIMARY KEY,
    `ref` CHAR(36) NOT NULL,
    `state` VARCHAR(32) NOT NULL,
    `extra` VARCHAR(32),
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `deleted_at` DATETIME(6),
    UNIQUE KEY `uid_state_ref_7c8a8b` (`ref`, `state`)
) CHARACTER SET utf8mb4 COMMENT='State';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `state`;"""
