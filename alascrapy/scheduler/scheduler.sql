
CREATE TABLE feed_in_conf.alascrapy_schedules (
	`id` INT(11) NOT NULL,
	`spider_name` VARCHAR(100) NOT NULL COLLATE 'utf8_unicode_ci',
	`hours` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`days_of_week` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`days_of_month` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`months` VARCHAR(50) NULL DEFAULT NULL COLLATE 'utf8_unicode_ci',
	`enabled` TINYINT(1) NOT NULL DEFAULT '0',
	PRIMARY KEY (`id`),
	INDEX `spider_name_idx` (`spider_name`)
);


CREATE TABLE feed_in_conf.alascrapy_run_params(
    schedule_id INT NOT NULL,
    parameter VARCHAR(100) NOT NULL,
    parameter_value VARCHAR(200) NOT NULL,
    PRIMARY KEY (schedule_id, parameter),
    CONSTRAINT `schedule_fk` FOREIGN KEY (schedule_id) REFERENCES
    feed_in_conf.alascrapy_schedules(id)
);

CREATE TABLE feed_in_conf.alascrapy_amazon_feeds(
    source_id INT(11) NOT NULL,
    feed_name VARCHAR(200) NOT NULL,
    last_feed_date TIMESTAMP,
    PRIMARY KEY (source_id, feed_name),
    CONSTRAINT `source_fk` FOREIGN KEY (source_id) REFERENCES review.sources(source_id)
);