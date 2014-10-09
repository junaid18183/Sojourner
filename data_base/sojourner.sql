-- MySQL dump 10.13  Distrib 5.6.15, for Linux (x86_64)
--
-- Host: localhost    Database: sojourner
-- ------------------------------------------------------
-- Server version	5.6.15

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `sojourner`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `sojourner` /*!40100 DEFAULT CHARACTER SET latin1 */;

USE `sojourner`;

--
-- Table structure for table `facts`
--

DROP TABLE IF EXISTS `facts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `facts` (
  `Last_Update` varchar(50) DEFAULT NULL,
  `Hostname` varchar(25) NOT NULL,
  `Arch` varchar(25) DEFAULT NULL,
  `Distribution` varchar(25) DEFAULT NULL,
  `Version` varchar(25) DEFAULT NULL,
  `System` varchar(25) DEFAULT NULL,
  `Kernel` varchar(50) DEFAULT NULL,
  `Eth0_ip` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`Hostname`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `facts`
--

LOCK TABLES `facts` WRITE;
/*!40000 ALTER TABLE `facts` DISABLE KEYS */;
/*!40000 ALTER TABLE `facts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory`
--

DROP TABLE IF EXISTS `inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory` (
  `Hostname` varchar(25) NOT NULL,
  `Crid` int(11) NOT NULL,
  `Asset_ID` varchar(25) DEFAULT NULL,
  `Price` varchar(25) DEFAULT NULL,
  `Role` varchar(25) DEFAULT NULL,
  `Product` varchar(25) DEFAULT NULL,
  `Owner` varchar(25) DEFAULT NULL,
  `DC` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`Hostname`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

-- Dump completed on 2014-08-08 13:09:27
