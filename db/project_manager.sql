-- MariaDB dump 10.19  Distrib 10.5.10-MariaDB, for Win64 (AMD64)
--
-- Host: 127.0.0.1    Database: project_manager
-- ------------------------------------------------------
-- Server version	10.5.10-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `project_lanes`
--

DROP TABLE IF EXISTS `project_lanes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_lanes` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL,
  `accent_hex` varchar(10) DEFAULT NULL,
  `project_id` int(10) unsigned NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `task_order` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT '[]' CHECK (json_valid(`task_order`)),
  PRIMARY KEY (`id`),
  KEY `project_lanes_projects_id_FK` (`project_id`),
  CONSTRAINT `project_lanes_projects_id_FK` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=79 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_lanes`
--

LOCK TABLES `project_lanes` WRITE;
/*!40000 ALTER TABLE `project_lanes` DISABLE KEYS */;
INSERT INTO `project_lanes` VALUES (44,'this is a new lane yayyy live',NULL,36,'2021-07-28 00:21:13','[118,119,121]'),(48,'title',NULL,36,'2021-07-28 05:12:37','[120, 122]'),(67,'Title',NULL,35,'2021-07-29 08:47:51','[166, 165, 179]'),(77,'1',NULL,35,'2021-07-29 13:13:41','[172, 176]');
/*!40000 ALTER TABLE `project_lanes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_roles`
--

DROP TABLE IF EXISTS `project_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_roles` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `project_id` int(10) unsigned NOT NULL,
  `user_id` int(10) unsigned NOT NULL,
  `role_id` int(10) unsigned NOT NULL,
  `accepted` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_roles_project_id_user_id_UN` (`project_id`,`user_id`),
  KEY `project_roles_users_id_FK` (`user_id`),
  KEY `project_roles_user_roles_id_FK` (`role_id`),
  CONSTRAINT `project_roles_projects_id_FK` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `project_roles_user_roles_id_FK` FOREIGN KEY (`role_id`) REFERENCES `user_roles` (`id`),
  CONSTRAINT `project_roles_users_id_FK` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=71 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_roles`
--

LOCK TABLES `project_roles` WRITE;
/*!40000 ALTER TABLE `project_roles` DISABLE KEYS */;
INSERT INTO `project_roles` VALUES (64,35,22,3,1,'2021-07-27 22:19:29'),(65,36,9,3,1,'2021-07-28 00:04:34'),(66,37,22,3,1,'2021-07-28 00:36:02'),(67,38,22,3,1,'2021-07-28 00:43:23'),(68,39,22,3,1,'2021-07-28 00:45:32'),(69,36,22,1,1,'2021-07-28 05:11:52'),(70,35,9,1,0,'2021-07-29 14:03:05');
/*!40000 ALTER TABLE `project_roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_tasks`
--

DROP TABLE IF EXISTS `project_tasks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_tasks` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `accent_hex` varchar(8) DEFAULT 'FFFFFF',
  `lane_id` int(10) unsigned NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `project_tasks_project_lanes_id_FK` (`lane_id`),
  CONSTRAINT `project_tasks_project_lanes_id_FK` FOREIGN KEY (`lane_id`) REFERENCES `project_lanes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=185 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_tasks`
--

LOCK TABLES `project_tasks` WRITE;
/*!40000 ALTER TABLE `project_tasks` DISABLE KEYS */;
INSERT INTO `project_tasks` VALUES (118,'1','desc1','FFFFFF',44,'2021-07-28 05:38:32'),(119,'2','desc2','FFFFFF',44,'2021-07-28 05:38:32'),(120,'3','desc3','FFFFFF',48,'2021-07-28 05:38:32'),(121,'4','desc4','FFFFFF',44,'2021-07-28 05:38:32'),(122,'5','desc5','FFFFFF',48,'2021-07-28 05:38:32'),(165,'1','1','FFFFFF',67,'2021-07-29 08:47:56'),(166,'1','1','FFFFFF',67,'2021-07-29 08:48:07'),(172,'6','6','FFFFFF',77,'2021-07-29 08:56:00'),(176,'1','1','FFFFFF',77,'2021-07-29 08:57:46'),(179,'4','4','FFFFFF',67,'2021-07-29 09:05:40');
/*!40000 ALTER TABLE `project_tasks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `projects`
--

DROP TABLE IF EXISTS `projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `projects` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL,
  `owner_id` int(10) unsigned NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `lane_order` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT '[]' CHECK (json_valid(`lane_order`)),
  PRIMARY KEY (`id`),
  KEY `projects_users_id_FK` (`owner_id`),
  CONSTRAINT `projects_users_id_FK` FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `projects`
--

LOCK TABLES `projects` WRITE;
/*!40000 ALTER TABLE `projects` DISABLE KEYS */;
INSERT INTO `projects` VALUES (35,'hi2234',22,'2021-07-27 22:19:29','[67, 77]'),(36,'1111',9,'2021-07-28 00:04:34','[44,48]'),(37,'not live',22,'2021-07-28 00:36:02','[]'),(38,'111',22,'2021-07-28 00:43:23','[]'),(39,'222',22,'2021-07-28 00:45:32','[]');
/*!40000 ALTER TABLE `projects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sessions`
--

DROP TABLE IF EXISTS `sessions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sessions` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `token` varchar(65) NOT NULL,
  `user_id` int(10) unsigned NOT NULL,
  `session_start` datetime NOT NULL DEFAULT current_timestamp(),
  `session_end` datetime DEFAULT NULL,
  `is_acitve` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `session_users_id_FK` (`user_id`),
  CONSTRAINT `session_users_id_FK` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sessions`
--

LOCK TABLES `sessions` WRITE;
/*!40000 ALTER TABLE `sessions` DISABLE KEYS */;
INSERT INTO `sessions` VALUES (6,'zDyYE5SWdUVCS7uh41orKXoXBdd3UuyuLWAMsjj8MZ5oXxGrrrpPp9sY5bJL',9,'2021-07-14 00:27:02',NULL,1),(7,'a-T7NwzP6RNVULd4AN4i9RWemyscT-aO3mDF6otfs_MM-sLSkhibfrdqfQlT',10,'2021-07-14 00:27:07',NULL,1),(8,'xaMxH4Izn99gTr22LZTaavKkS4yAicIEMIzzd0RzBTyMZTDYdB53ongQw8fl',9,'2021-07-14 22:54:14',NULL,1),(9,'gCMK5sGpEykOwTJVOlzzXzfEcCnXbuDfZVmW-_mw6461KytJZLxVzHgtnU-5',9,'2021-07-14 22:55:06',NULL,1),(10,'eDpVlQDERFXX_4jqpUt0FCxR7Yq6KC0Jo8uFOcLW6foBNTcHyGM-dLy5yeVK',9,'2021-07-14 22:55:14',NULL,1),(11,'Zv2KD02JY4xj7wZu0NpRJ46OSi6rBphCTY33osSO22M5bF3LUnKggom_61BR',9,'2021-07-14 22:55:18',NULL,1),(12,'UwLuAuklS-nPYMlvfQ3wT4htyRdeACbP1FI3mxAKR-NRj1RswcBrKzTHY9vc',9,'2021-07-14 23:17:13',NULL,1),(13,'qIM7vEVdjj4ZFwAhOUxgntIBJ7qN2wkY3wsONX0NVCIMiQcF2H8TFa2cuzS3',9,'2021-07-14 23:17:20',NULL,1),(14,'WQAwu40RRbii2FbbSqxVA8IkeYsDQwuH2RvHaizhWyunbBjQ52jnacXVpVnl',12,'2021-07-15 18:00:16',NULL,1),(15,'gy3RY8LIV8pOVqvLBuPvccJ1JQtBLbti_yr8MTLiV56ifKCzgYQerEZGJ8Vu',13,'2021-07-15 18:00:23',NULL,1),(16,'S-d_xvAA-hIHPWooqCWSwbhXCgYVuu413V0Vt4nhgA2MOmwWAiWkxPGNl3vo',14,'2021-07-15 19:48:05',NULL,1),(17,'yq5mON8xeJse5SKYPFwFsqnKjO0oYBKsGyfRjh27KSRSyOXLJzlzSH1Hqhk2',15,'2021-07-15 19:48:12',NULL,1),(18,'5bjabbIqMwsK3-5FNS_uKnGqe0d0EsxZJs7TddfwqK4JXSM0w0eY-XpIWLu-',16,'2021-07-15 19:48:17',NULL,1),(19,'VcMY7T6iPIvgfw-b2WfUBFmFRtVxKTKEYiIukZPntWcZtaJzdgKGv975GoJQ',9,'2021-07-20 16:53:05',NULL,1),(20,'kppuNUNkSStUfKYE_O11K-0z8FXq9OpEDfB6u2RWQXlAmyrkuiJNvcFCm2eu',9,'2021-07-20 16:56:22',NULL,1),(21,'fAoHXiE-6NNoB3hRJjS7Nbpkq4lsxVkBidQKKrBFRqAfK7Zj1hY-dIHPQDqe',9,'2021-07-20 17:04:03',NULL,1),(22,'VPJXmhtCsuzN_Yjp-cGiPye8A-32EQSEKOBRczww5dJXnkkY0SLzzeQcoU5o',9,'2021-07-20 17:05:10',NULL,1),(23,'ICc6Ot1BTVwaZbYo4t6gGMqt8z0xkpv39nFp6QEm9F9yd8PfuHzDWqDT01h_',9,'2021-07-20 17:07:42',NULL,1),(24,'ZgvQOIkXHE8SWHCX58BD1EF8q2NPQIn0Zq8lA46IVmb7PIogtNaeBi-aC8Lw',9,'2021-07-20 17:11:21',NULL,1),(25,'GxpixuoGbgspW6FEIcUpe8RJS2fLbrX9EIONx2sYGncm3WDyKQMttqleh9Gu',9,'2021-07-20 17:11:25',NULL,1),(26,'0f8jRjqFPWXqqoPyoFBuOsaGlczk9wSk-L_byKl9sPm7VrbReJRdFiIsjHzU',9,'2021-07-20 17:35:52',NULL,1),(27,'Uchr7pezB4FPf7_3LgAOALnfMArkzlK1ivTK-qf-6rguFzSFSU6ZcIs4cQNQ',9,'2021-07-20 17:39:19',NULL,1),(28,'MufVG0Gh4_LNGtNqKCcqA-Xr28xXarLC2jU_gkjBSmcibB3xOTfqgEFNOj5R',17,'2021-07-20 19:05:39',NULL,1),(29,'MaGg2wHqkAnDqHfx52sdYz8kOpt_hl7LRr2DT6-mtU77Ah1HqMq6nk2eyhH4',18,'2021-07-20 19:09:24',NULL,1),(30,'EDHtdbcPcswuB2wl6K2JKKWNN_MWWfbqpZ4O1YDNW_no3_TZk4MUoM5VAoQo',9,'2021-07-20 19:54:36',NULL,1),(31,'f7cPh4ns8SYKYfcPCnQvfncbJwIRdiDHAUEVByg4UfsygRNf36o8wTzPPqgq',9,'2021-07-20 20:48:48',NULL,1),(32,'Omuk6rftm727drgDLQj-lvpT6ddn59UF-nn5ARjmvaaDzSlegOFlaoUnIulz',9,'2021-07-22 01:47:09',NULL,1),(33,'WAVD-8pcqYQJtT8-W9woeLirprSDYQ1OHv_CK9OEu30hjFyzO74Omy_hwoyV',9,'2021-07-23 01:50:40',NULL,1),(34,'eaCsIM6PmrbfotB2lkSgdKosc1bd4ogx3GlX7CVFWF23qdvGt9eC8svpzg6A',9,'2021-07-24 07:50:15',NULL,1),(35,'m9Et8BdMB0abN0LXhDeGy9NK_wcZgM5nWLO6-ZbENALOKv1zeh9SR-apcq-7',9,'2021-07-25 17:50:44',NULL,1),(36,'3sPYT8vXGXh7tM-7q10GsvEyDKU99tNs9Of6qIz4lWttiVa1KnQV13JN_XMA',9,'2021-07-25 18:20:04',NULL,1),(37,'onncwJ3yO5RtL6Gzlj0XF7M6B6MQMAI5jk36XHxqMqNkYalTY6Jz8edYKNGo',9,'2021-07-27 05:50:35',NULL,1),(38,'vcgXGdEgxT9PPOppZUWiLhPadC5Qr2kBVVromz9K3CYeh3Qw59_ePexThkg7',19,'2021-07-27 13:35:49',NULL,1),(39,'VLlRAzjk1167jyjlQAD9SmrihtIp-MWE_IRZBlrGX0vRusOawZuHjtWIyAOa',19,'2021-07-27 13:38:42',NULL,1),(40,'rPu-_VdRji8KjXBUbkxQqqDoza2Gov8Tj4w3ayWWuThGlisRmcvaSZYXbLl6',20,'2021-07-27 13:41:39',NULL,1),(41,'1bFPa1v-XuEks9_KJRbR9e9kkm80hPMl1mS5ojhwTDiJdBi-exmwacHkglOO',9,'2021-07-27 13:50:59',NULL,1),(42,'anZqYd9NmodduMi4Gk91OVZHQclgd6bLXZIEPvTM_aX2hvsVuXlvFpYfS11r',21,'2021-07-27 14:56:50',NULL,1),(43,'7OmhoXNobuI1wk8FBOE3iv5I1ltJ0EJdKOKLeUBBem1ZUvx1es3Wl2SDS_xP',22,'2021-07-27 16:43:44',NULL,1),(44,'gAd3aWW_ilM34XDI_t7D0NyIYMT-QwDjK9BHjWpb_hfvv9o8oaqshXH6LE7t',9,'2021-07-28 00:04:11',NULL,1),(45,'cmxkk-1Z7icQuuTSj9_uymuPXQmLrwR2cuPSkroe47HYToMyqS4fsyf_E674',9,'2021-07-29 05:36:44',NULL,1),(46,'U8QQNbRmiSoEh2uw_AUklvlOA1l-f4Kws8SCmYC720-pId4llKYzQTm3pAA_',22,'2021-07-29 05:37:03',NULL,1),(49,'7nOGiZjZQSeeDQaXF0W8WyF0-tOAePicOzCPCgsbMTRSvUUa7KQgGcaNeOo7',22,'2021-07-29 14:50:24',NULL,1),(51,'bjt1sY2r_Cl9sqUB2zybmsycPjMvCkvHoW8FOhxAT9eMjxqHAUMBetzf1A10',22,'2021-07-30 10:10:15',NULL,1);
/*!40000 ALTER TABLE `sessions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_roles`
--

DROP TABLE IF EXISTS `user_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_roles` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `can_edit` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_roles`
--

LOCK TABLES `user_roles` WRITE;
/*!40000 ALTER TABLE `user_roles` DISABLE KEYS */;
INSERT INTO `user_roles` VALUES (1,'view',0),(2,'edit',1),(3,'owner',1);
/*!40000 ALTER TABLE `user_roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `salt` varchar(10) NOT NULL,
  `avatar` varchar(255) NOT NULL DEFAULT 'https://cdn.discordapp.com/attachments/841266201657344010/841266288486907914/ABSRlIpzcqh_JEyZP1CW1_RaZDO34zgsV3wfGtpwfn_D3IB6XFnQjvFl5nkymDIEJ58dpJoA1-t8agaWloWXJhVz9WWaXYVIbkkj.png',
  `status` varchar(120) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `username` varchar(30) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_email_UN` (`email`),
  UNIQUE KEY `users_username_UN` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (9,'user2@none.com','780c02504666c405eeca85be5b2c622182e55451e7f4a367202f08e4e598df37c9447539a3c920be2abff903f2a489dd903ce5d781e0d5ac36221b4cc9ab6a5e','CFifT0Kmvt','https://cdn.discordapp.com/attachments/841266201657344010/841266288486907914/ABSRlIpzcqh_JEyZP1CW1_RaZDO34zgsV3wfGtpwfn_D3IB6XFnQjvFl5nkymDIEJ58dpJoA1-t8agaWloWXJhVz9WWaXYVIbkkj.png',NULL,'2021-07-14 00:27:02','user2'),(10,'user3@none.com','1a176ff81970a1cc5084e2d89a587dbda30ad64c1a90799b7a73d87526bc57c4b2a07ff82b9c1d5890ce21ad31f4d39d25df9e2c82421ac058ec1ab8b5c31477','9qNHf66VxZ','https://cdn.discordapp.com/attachments/841266201657344010/841266288486907914/ABSRlIpzcqh_JEyZP1CW1_RaZDO34zgsV3wfGtpwfn_D3IB6XFnQjvFl5nkymDIEJ58dpJoA1-t8agaWloWXJhVz9WWaXYVIbkkj.png',NULL,'2021-07-14 00:27:07','user3'),(12,'user4@none.com','f04bc0ff3e6171627c1a448fa27b1338d866c0cbb38ca68b36e26ccc1d555efb4f58726637773c533a2bf81538809948ecc9252b990bcb08a36ad8046bd71327','kCSzCrccos','https://cdn.discordapp.com/attachments/841266201657344010/841266288486907914/ABSRlIpzcqh_JEyZP1CW1_RaZDO34zgsV3wfGtpwfn_D3IB6XFnQjvFl5nkymDIEJ58dpJoA1-t8agaWloWXJhVz9WWaXYVIbkkj.png',NULL,'2021-07-15 18:00:16','user4'),(13,'user5@none.com','8b077fa65b768d7eae51d1d737f6a924717825ac13e4364c984357b930932133548b9218c4c234c613e2249310ba25df19044b51c4fefcd1c905509e8c4555e8','tuG6QDZah4','https://cdn.discordapp.com/attachments/841266201657344010/841266288486907914/ABSRlIpzcqh_JEyZP1CW1_RaZDO34zgsV3wfGtpwfn_D3IB6XFnQjvFl5nkymDIEJ58dpJoA1-t8agaWloWXJhVz9WWaXYVIbkkj.png',NULL,'2021-07-15 18:00:23','user5'),(14,'user6@none.com','2817e8b3b910a74178fd31bcf1070c9ff030aa349f9a97468f232c247cbd980e6b9fb2b5640fbf2fc27c79a90a52891e3af0061c59aeb03883889bd8f69e539f','hYTEltRWUY','https://cdn.discordapp.com/attachments/841266201657344010/841266288486907914/ABSRlIpzcqh_JEyZP1CW1_RaZDO34zgsV3wfGtpwfn_D3IB6XFnQjvFl5nkymDIEJ58dpJoA1-t8agaWloWXJhVz9WWaXYVIbkkj.png',NULL,'2021-07-15 19:48:05','user6'),(15,'user7@none.com','de2f4a82d3b8ea72bc157929212aaa5208bcf6f3915be8dfd463ad15e0b8c96d8df32eb5e194cc3295ea67fc61fa644e9a21b799209f63b739378951b297d6c0','htoxoCaPLe','https://cdn.discordapp.com/attachments/841266201657344010/841266288486907914/ABSRlIpzcqh_JEyZP1CW1_RaZDO34zgsV3wfGtpwfn_D3IB6XFnQjvFl5nkymDIEJ58dpJoA1-t8agaWloWXJhVz9WWaXYVIbkkj.png',NULL,'2021-07-15 19:48:12','user7'),(16,'user8@none.com','cd81894fa53d6aea40475c74f09fbe7111129400ee128454362896574bfc2accae79d6f779c59c9bcca772fdafce80b85680aae366dbf96724e674705ce35429','PGlAx60bpm','https://cdn.discordapp.com/attachments/841266201657344010/841266288486907914/ABSRlIpzcqh_JEyZP1CW1_RaZDO34zgsV3wfGtpwfn_D3IB6XFnQjvFl5nkymDIEJ58dpJoA1-t8agaWloWXJhVz9WWaXYVIbkkj.png',NULL,'2021-07-15 19:48:17','user8'),(17,'test@test.com','7dc2b8e2f78c62655bf9f3b00682c380775ed84cff9ace5370f1338940ff489df9914c799aad853f4cd6e3705668ac75f9ca396eecd46311e0bbf2d6b6bfdc23','NzeM1EoW3Q','https://cdn.discordapp.com/attachments/841266201657344010/841266288486907914/ABSRlIpzcqh_JEyZP1CW1_RaZDO34zgsV3wfGtpwfn_D3IB6XFnQjvFl5nkymDIEJ58dpJoA1-t8agaWloWXJhVz9WWaXYVIbkkj.png',NULL,'2021-07-20 19:05:39','test1'),(18,'test2@test.com','3b55033057b5a28bd82a02e20bce1bde03af8af9ab2547a29fd592c8d4eeccd2cb6e4f113b06d606a3611b79fa2fcacb6cb28a7b091fe9491c93f7c711219e4c','CvmplVe2As','https://cdn.discordapp.com/attachments/841266201657344010/841266288486907914/ABSRlIpzcqh_JEyZP1CW1_RaZDO34zgsV3wfGtpwfn_D3IB6XFnQjvFl5nkymDIEJ58dpJoA1-t8agaWloWXJhVz9WWaXYVIbkkj.png',NULL,'2021-07-20 19:09:24','test2'),(19,'newEmail@none.com','3121a7422f5e0114ed2a7c8a554f302856f4feedf2031481d76154f3be3049ddfb297e8acee8c3e839d7a679c9310b2fd6a27ffc9539b1f13379c3f3ed3a5cc1','jfn8FGBp1l','https://cdn.discordapp.com/attachments/841266201657344010/841266288486907914/ABSRlIpzcqh_JEyZP1CW1_RaZDO34zgsV3wfGtpwfn_D3IB6XFnQjvFl5nkymDIEJ58dpJoA1-t8agaWloWXJhVz9WWaXYVIbkkj.png',NULL,'2021-07-27 13:35:49','newUser12'),(20,'newuser1@email.com','f2027a1f9291fd7d77a81c7fce3213e75dfcf679c00d936ef91e52347cee2d755c2b0286de4f00b2ddf63b5baa094235974696562a1ea6d4a2fe98b9afb4996b','7hWfqo6WoR','https://cdn.discordapp.com/attachments/841266201657344010/841266288486907914/ABSRlIpzcqh_JEyZP1CW1_RaZDO34zgsV3wfGtpwfn_D3IB6XFnQjvFl5nkymDIEJ58dpJoA1-t8agaWloWXJhVz9WWaXYVIbkkj.png',NULL,'2021-07-27 13:41:39','newuser1'),(21,'newuser@gmail.com','2182b49bbf2833ea744ad47f3d63c553931acf34de7499c4d86b9b59e1f67088edb55dee571be33559bda937e993771e4e3810b7716f466a014c723a4bd768a8','RSFzAtIMsS','https://cdn.discordapp.com/attachments/841266201657344010/841266288486907914/ABSRlIpzcqh_JEyZP1CW1_RaZDO34zgsV3wfGtpwfn_D3IB6XFnQjvFl5nkymDIEJ58dpJoA1-t8agaWloWXJhVz9WWaXYVIbkkj.png',NULL,'2021-07-27 14:56:50','neweruser'),(22,'shawn@none.com','9e718c0e2c56830b793bbffadeffc15c37a56752517dab687977b39c0024e51b561dc24c85523f8fde04ef2f809dcb5e82a336754f65fb4c4ba6e7f7845ebcb0','zW0olkzGDR','https://cdn.discordapp.com/attachments/841266201657344010/841266288486907914/ABSRlIpzcqh_JEyZP1CW1_RaZDO34zgsV3wfGtpwfn_D3IB6XFnQjvFl5nkymDIEJ58dpJoA1-t8agaWloWXJhVz9WWaXYVIbkkj.png','yo','2021-07-27 16:43:44','shawn');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-07-30 10:48:38
