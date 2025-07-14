from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `state` (
    `id` CHAR(36) NOT NULL PRIMARY KEY,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `deleted_at` DATETIME(6),
    `ref` CHAR(36) NOT NULL,
    `ref_type` VARCHAR(32) NOT NULL,
    `state` VARCHAR(32) NOT NULL,
    `extra` JSON,
    UNIQUE KEY `uid_state_ref_79d2d8` (`ref`, `ref_type`)
) CHARACTER SET utf8mb4 COMMENT='State';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `state`;"""
