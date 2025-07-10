from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `raw` (
    `id` CHAR(36) NOT NULL PRIMARY KEY,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `deleted_at` DATETIME(6),
    `html` LONGTEXT,
    `meta` JSON,
    `url_id` CHAR(36) NOT NULL,
    CONSTRAINT `fk_raw_url_f2b745ee` FOREIGN KEY (`url_id`) REFERENCES `url` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='Raw';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `raw`;"""
