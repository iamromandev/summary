from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `task` (
    `id` CHAR(36) NOT NULL PRIMARY KEY,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `deleted_at` DATETIME(6),
    `ref` CHAR(36) NOT NULL,
    `ref_type` VARCHAR(32) NOT NULL,
    `action` VARCHAR(9) NOT NULL COMMENT 'CREATE: create\nREAD: read\nUPDATE: update\nDELETE: delete\nFETCH: fetch\nCRAWL: crawl\nPARSE: parse\nEXTRACT: extract\nTRANSFORM: transform\nLOAD: load\nTRAIN: train\nEVALUATE: evaluate\nINFER: infer\nPREDICT: predict\nVALIDATE: validate\nSTART: start\nSTOP: stop\nRESTART: restart\nRETRY: retry\nCANCEL: cancel\nSCHEDULE: schedule\nEXPORT: export\nIMPORT: import\nBACKUP: backup\nRESTORE: restore\nNOTIFY: notify\nLOG: log\nMONITOR: monitor\nARCHIVE: archive\nCLEANUP: cleanup\nUNKNOWN: unknown' DEFAULT 'unknown',
    `state` VARCHAR(12) NOT NULL COMMENT 'NEW: new\nPENDING: pending\nQUEUED: queued\nSCHEDULED: scheduled\nINITIALIZING: initializing\nRUNNING: running\nPROCESSING: processing\nVALIDATING: validating\nCOMPLETED: completed\nSUCCESS: success\nFAILED: failed\nRETRY: retry\nTIMEOUT: timeout\nSKIPPED: skipped\nCANCELED: canceled\nDEFERRED: deferred\nBLOCKED: blocked\nINTERRUPTED: interrupted\nSTALE: stale\nARCHIVED: archived\nEXPIRED: expired\nUNKNOWN: unknown' DEFAULT 'unknown',
    `meta` JSON,
    UNIQUE KEY `uid_task_ref_c1e65a` (`ref`, `ref_type`)
) CHARACTER SET utf8mb4 COMMENT='Task';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `task`;"""
