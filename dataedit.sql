-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Apr 22, 2026 at 10:40 AM
-- Server version: 9.1.0
-- PHP Version: 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `databreach`
--

-- --------------------------------------------------------

--
-- Table structure for table `downloads`
--

DROP TABLE IF EXISTS `downloads`;
CREATE TABLE IF NOT EXISTS `downloads` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ownerid` int NOT NULL,
  `uid` int NOT NULL,
  `uname` varchar(50) NOT NULL,
  `filename` varchar(50) NOT NULL,
  `date` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `downloads`
--

INSERT INTO `downloads` (`id`, `ownerid`, `uid`, `uname`, `filename`, `date`) VALUES
(1, 8, 8, 'chandru', 'image1.jpg', '2026-04-22'),
(2, 8, 9, 'gokul', 'image1.jpg', '2026-04-22'),
(3, 8, 9, 'gokul', 'image1.jpg', '2026-04-22');

-- --------------------------------------------------------

--
-- Table structure for table `files`
--

DROP TABLE IF EXISTS `files`;
CREATE TABLE IF NOT EXISTS `files` (
  `fid` int NOT NULL AUTO_INCREMENT,
  `uid` int NOT NULL,
  `filename` varchar(10) NOT NULL,
  `filepath` varchar(255) NOT NULL,
  `skey` varchar(5) NOT NULL,
  PRIMARY KEY (`fid`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `files`
--

INSERT INTO `files` (`fid`, `uid`, `filename`, `filepath`, `skey`) VALUES
(12, 6, 'Python Min', 'static/uploads\\Python Mini Task  (1).pdf', '123'),
(13, 7, 'finale pra', 'static/uploads\\finale prasanna doc.pdf', '809'),
(14, 8, 'image1.jpg', 'static/uploads\\image1.jpg', '2003');

-- --------------------------------------------------------

--
-- Table structure for table `intrusion`
--

DROP TABLE IF EXISTS `intrusion`;
CREATE TABLE IF NOT EXISTS `intrusion` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ownerid` int NOT NULL,
  `uid` int NOT NULL,
  `uname` varchar(50) NOT NULL,
  `ipaddress` varchar(255) NOT NULL,
  `filename` varchar(100) NOT NULL,
  `date` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `intrusion`
--

INSERT INTO `intrusion` (`id`, `ownerid`, `uid`, `uname`, `ipaddress`, `filename`, `date`) VALUES
(4, 7, 6, 'Devadharshini', '192.168.1.4', 'finale pra', '2026-02-26'),
(5, 0, 8, 'chandru', '192.168.56.2', 'LOGIN_ATTEMPT', '2026-04-22'),
(6, 8, 9, 'gokul', '192.168.56.2', 'image1.jpg', '2026-04-22');

-- --------------------------------------------------------

--
-- Table structure for table `requests`
--

DROP TABLE IF EXISTS `requests`;
CREATE TABLE IF NOT EXISTS `requests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `rid` int NOT NULL,
  `rname` varchar(50) NOT NULL,
  `fileid` int NOT NULL,
  `ownerid` int NOT NULL,
  `status` varchar(50) NOT NULL,
  `skey` varchar(5) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `requests`
--

INSERT INTO `requests` (`id`, `rid`, `rname`, `fileid`, `ownerid`, `status`, `skey`) VALUES
(4, 6, 'Devadharshini', 13, 7, 'allowed', '809'),
(5, 9, 'gokul', 14, 8, 'allowed', '2003');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
CREATE TABLE IF NOT EXISTS `user` (
  `uid` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `password` varchar(15) NOT NULL,
  `status` varchar(15) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `pattern_id` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`uid`, `name`, `password`, `status`, `email`, `pattern_id`) VALUES
(6, 'Devadharshini', '2002', 'allowed', 'devawrk0@gmail.com', '8'),
(7, 'kani', '2468', 'allowed', 'kani@gmail.com', '6'),
(8, 'chandru', '123456', 'allowed', 'chandrupnd2@gmail.com', NULL),
(9, 'gokul', '123456', 'allowed', 'ascentztechpro@gmail.com', NULL);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
