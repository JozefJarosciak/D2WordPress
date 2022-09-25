// Required download database - MySQL Code

CREATE TABLE `urls` (
	`id` INT(10) NOT NULL AUTO_INCREMENT,
	`timestamp_orig` TIMESTAMP NULL DEFAULT NULL,
	`image_orig` VARCHAR(255) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`keywords` TEXT NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`image_new` VARCHAR(255) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`thumbnail_new_id` INT(10) NULL DEFAULT NULL,
	`thumbnail_new` VARCHAR(255) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`timestamp` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
	`size_image_orig` INT(10) NULL DEFAULT NULL,
	`size_thumb_new` INT(10) NULL DEFAULT NULL,
	`author` VARCHAR(255) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	PRIMARY KEY (`id`) USING BTREE,
	UNIQUE INDEX `index` (`timestamp_orig`, `image_orig`) USING BTREE
)
COLLATE='utf8mb4_0900_ai_ci'
ENGINE=InnoDB
AUTO_INCREMENT=20521
;
