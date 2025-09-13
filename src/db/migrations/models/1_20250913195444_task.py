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
    `action` VARCHAR(16) NOT NULL COMMENT 'CREATE: create\nREAD: read\nUPDATE: update\nDELETE: delete\nFETCH: fetch\nCRAWL: crawl\nPARSE: parse\nEXTRACT: extract\nTRANSFORM: transform\nLOAD: load\nVALIDATE: validate\nCLEAN: clean\nNORMALIZE: normalize\nENRICH: enrich\nAGGREGATE: aggregate\nJOIN: join\nFILTER: filter\nSORT: sort\nDEDUPLICATE: deduplicate\nMERGE: merge\nSPLIT: split\nTRAIN: train\nEVALUATE: evaluate\nINFER: infer\nPREDICT: predict\nTEST: test\nDEPLOY: deploy\nRETRAIN: retrain\nTUNE: tune\nSCORE: score\nFEATURE_ENGINEER: feature_engineer\nSTART: start\nSTOP: stop\nRESTART: restart\nRETRY: retry\nCANCEL: cancel\nSCHEDULE: schedule\nPAUSE: pause\nRESUME: resume\nABORT: abort\nWAIT: wait\nEXPORT: export\nIMPORT: import\nBACKUP: backup\nRESTORE: restore\nSNAPSHOT: snapshot\nARCHIVE: archive\nCLEANUP: cleanup\nNOTIFY: notify\nLOG: log\nMONITOR: monitor\nALERT: alert\nREPORT: report\nTRACK: track\nAUDIT: audit\nOBSERVE: observe\nSEND: send\nRECEIVE: receive\nPUBLISH: publish\nSUBSCRIBE: subscribe\nBROADCAST: broadcast\nQUEUE: queue\nDEQUEUE: dequeue\nOTHER: other' DEFAULT 'other',
    `state` VARCHAR(15) NOT NULL COMMENT 'NEW: new\nPENDING: pending\nQUEUED: queued\nSCHEDULED: scheduled\nINITIALIZING: initializing\nSTARTING: starting\nRUNNING: running\nPROCESSING: processing\nVALIDATING: validating\nCHECKING: checking\nTRANSFORMING: transforming\nWAITING: waiting\nBLOCKED: blocked\nDEFERRED: deferred\nSKIPPED: skipped\nINTERRUPTED: interrupted\nRETRY: retry\nTIMEOUT: timeout\nFAILED: failed\nERROR: error\nABORTED: aborted\nCANCELED: canceled\nCOMPLETED: completed\nSUCCESS: success\nPARTIAL_SUCCESS: partial_success\nSTALE: stale\nARCHIVED: archived\nEXPIRED: expired\nSUSPENDED: suspended\nRESUMED: resumed\nOTHER: other' DEFAULT 'other',
    `meta` JSON,
    UNIQUE KEY `uid_task_ref_c1e65a` (`ref`, `ref_type`)
) CHARACTER SET utf8mb4 COMMENT='Task';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `task`;"""
