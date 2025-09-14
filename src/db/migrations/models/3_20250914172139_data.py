from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `data` (
    `id` CHAR(36) NOT NULL PRIMARY KEY,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `deleted_at` DATETIME(6),
    `source` VARCHAR(16) COMMENT 'API: api\nUSER: user\nCRAWLER: crawler\nSYSTEM: system\nDATABASE: database\nFILE_UPLOAD: file_upload\nSENSOR: sensor\nSTREAM: stream\nMANUAL: manual\nEXTERNAL_SERVICE: external_service\nMOBILE_APP: mobile_app\nDESKTOP_APP: desktop_app\nEMAIL: email\nMESSAGE_QUEUE: message_queue\nLOG: log\nBACKUP: backup\nTEST: test',
    `type` VARCHAR(13) COMMENT 'DOCUMENT: document\nIMAGE: image\nVIDEO: video\nAUDIO: audio\nSENSOR: sensor\nLOG: log\nTRANSACTION: transaction\nWEBPAGE: webpage\nEMAIL: email\nSCRIPT: script\nAPI: api\nDATABASE: database\nBACKUP: backup\nCONFIGURATION: configuration\nARCHIVE: archive\nMODEL: model\nNOTE: note\nSTREAM: stream',
    `subtype` VARCHAR(13) COMMENT 'INVOICE: invoice\nREPORT: report\nARTICLE: article\nMANUAL: manual\nCONTRACT: contract\nMEMO: memo\nPRESENTATION: presentation\nSPREADSHEET: spreadsheet\nPHOTO: photo\nDIAGRAM: diagram\nSCREENSHOT: screenshot\nICON: icon\nLOGO: logo\nMAP: map\nTUTORIAL: tutorial\nADVERTISEMENT: advertisement\nCLIP: clip\nMOVIE: movie\nANIMATION: animation\nMUSIC: music\nPODCAST: podcast\nRECORDING: recording\nSOUND_EFFECT: sound_effect\nTEMPERATURE: temperature\nHUMIDITY: humidity\nGPS: gps\nACCELERATION: acceleration\nPRESSURE: pressure\nLIGHT: light\nPROXIMITY: proximity\nERROR_LOG: error_log\nACCESS_LOG: access_log\nEVENT_LOG: event_log\nPAYMENT: payment\nORDER: order\nREFUND: refund\nINVOICE_ITEM: invoice_item\nHTML_PAGE: html_page\nJSON_RESPONSE: json_response\nXML_RESPONSE: xml_response\nPYTHON: python\nSHELL: shell\nJAVASCRIPT: javascript\nSQL: sql\nMODEL_FILE: model_file\nTRAINING_DATA: training_data\nMARKDOWN: markdown\nNOTE: note',
    `owner_id` CHAR(36),
    `organization` VARCHAR(256),
    `status` VARCHAR(10) COMMENT 'ACTIVE: active\nINACTIVE: inactive\nARCHIVED: archived\nDELETED: deleted\nPENDING: pending\nPROCESSING: processing\nFAILED: failed\nCOMPLETED: completed\nDRAFT: draft\nREVIEW: review\nAPPROVED: approved\nREJECTED: rejected\nEXPIRED: expired\nLOCKED: locked\nSCHEDULED: scheduled',
    `visibility` VARCHAR(15) COMMENT 'PUBLIC: public\nPRIVATE: private\nINTERNAL: internal\nRESTRICTED: restricted\nCONFIDENTIAL: confidential\nSECRET: secret\nANONYMOUS: anonymous\nENCRYPTED: encrypted\nTOKEN_PROTECTED: token_protected\nPAID: paid\nTEMPORARY: temporary',
    `version` INT NOT NULL DEFAULT 1,
    `content` JSON,
    `checksum` VARCHAR(64),
    `score` DOUBLE,
    `is_encrypted` BOOL NOT NULL DEFAULT 0,
    `tags` JSON,
    `permissions` JSON,
    `expires_at` DATETIME(6),
    `meta` JSON,
    `parent_id` CHAR(36),
    CONSTRAINT `fk_data_data_b16099d7` FOREIGN KEY (`parent_id`) REFERENCES `data` (`id`) ON DELETE SET NULL,
    KEY `idx_data_owner_i_204d74` (`owner_id`),
    KEY `idx_data_checksu_3037b5` (`checksum`)
) CHARACTER SET utf8mb4 COMMENT='Data';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `data`;"""
