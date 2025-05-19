-- phpMyAdmin SQL Dump
-- version 5.0.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 20, 2025 at 07:31 AM
-- Server version: 10.4.14-MariaDB
-- PHP Version: 7.4.11

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `royal`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin_login`
--

CREATE TABLE `admin_login` (
  `adminnm` varchar(20) NOT NULL,
  `password` varchar(8) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `admin_login`
--

INSERT INTO `admin_login` (`adminnm`, `password`) VALUES
('drashti', 'd@123'),
('jinsha', '7410.'),
('hetu', '8520');

-- --------------------------------------------------------

--
-- Table structure for table `bill`
--

CREATE TABLE `bill` (
  `bill_id` int(11) NOT NULL,
  `o_id` int(11) NOT NULL,
  `total` decimal(10,2) NOT NULL,
  `gst` decimal(10,2) NOT NULL,
  `net_amt` decimal(10,2) NOT NULL,
  `bill_date` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `bill`
--

INSERT INTO `bill` (`bill_id`, `o_id`, `total`, `gst`, `net_amt`, `bill_date`) VALUES
(31, 92, '100000.00', '28000.00', '128000.00', '2025-02-20 04:59:52'),
(32, 93, '225000.00', '63000.00', '288000.00', '2025-02-20 05:21:05'),
(33, 94, '60000.00', '16800.00', '76800.00', '2025-02-20 05:22:06'),
(34, 95, '100000.00', '28000.00', '128000.00', '2025-02-20 05:40:46'),
(35, 96, '150000.00', '42000.00', '192000.00', '2025-02-20 05:55:50'),
(36, 97, '300000.00', '84000.00', '384000.00', '2025-02-20 06:08:31');

-- --------------------------------------------------------

--
-- Table structure for table `cart`
--

CREATE TABLE `cart` (
  `cart_id` int(11) NOT NULL,
  `userid` int(11) NOT NULL,
  `id` int(11) NOT NULL,
  `quantity` int(11) NOT NULL DEFAULT 1,
  `total` decimal(10,2) NOT NULL,
  `date` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `cart`
--

INSERT INTO `cart` (`cart_id`, `userid`, `id`, `quantity`, `total`, `date`) VALUES
(39, 15, 20, 1, '100000.00', '2025-02-20 04:59:21'),
(40, 18, 16, 1, '225000.00', '2025-02-20 05:20:46'),
(41, 17, 19, 1, '60000.00', '2025-02-20 05:21:54'),
(42, 19, 18, 1, '200000.00', '2025-02-20 06:08:05');

-- --------------------------------------------------------

--
-- Table structure for table `feedback`
--

CREATE TABLE `feedback` (
  `id` int(11) NOT NULL,
  `usernm` varchar(20) NOT NULL,
  `email` varchar(40) NOT NULL,
  `phonno` varchar(10) NOT NULL,
  `message` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `feedback`
--

INSERT INTO `feedback` (`id`, `usernm`, `email`, `phonno`, `message`) VALUES
(5, 'hetu', 'hetu@gmail.com', '9558976904', 'very good :)'),
(6, 'jinu', 'jinshagodhani@gmail.com', '9316058810', 'very good!!!!!!!!!!!!!'),
(7, 'mira', 'miralimem@gmail.com', '7412365890', 'good');

-- --------------------------------------------------------

--
-- Table structure for table `login`
--

CREATE TABLE `login` (
  `usernm` varchar(20) NOT NULL,
  `password` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `login`
--

INSERT INTO `login` (`usernm`, `password`) VALUES
('jinsha', '123456');

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `o_id` int(11) NOT NULL,
  `cart_id` int(11) NOT NULL,
  `o_date` date NOT NULL,
  `price` int(11) NOT NULL,
  `qty` int(11) NOT NULL,
  `total` int(11) NOT NULL,
  `status` varchar(30) NOT NULL,
  `qrcode` varchar(10) NOT NULL,
  `usernm` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `orders`
--

INSERT INTO `orders` (`o_id`, `cart_id`, `o_date`, `price`, `qty`, `total`, `status`, `qrcode`, `usernm`) VALUES
(92, 39, '2025-02-20', 100000, 1, 100000, 'Shipped', 'EVHCVQSZPH', ''),
(93, 40, '2025-02-20', 225000, 1, 225000, 'Delivered', 'HKM3VW7KD9', ''),
(94, 41, '2025-02-20', 60000, 1, 60000, 'Shipped', 'WMCZNWBPP5', ''),
(95, 40, '2025-02-20', 100000, 1, 100000, 'Delivered', 'OY3FHTTHBB', ''),
(96, 39, '2025-02-20', 150000, 1, 150000, 'Pending', 'V90J4ZT931', 'hetu'),
(97, 42, '2025-02-20', 200000, 1, 200000, 'Pending', '4XWJ3JZ61P', 'mira'),
(98, 42, '2025-02-20', 100000, 1, 100000, 'Delivered', '4XWJ3JZ61P', 'mira');

-- --------------------------------------------------------

--
-- Table structure for table `product`
--

CREATE TABLE `product` (
  `id` int(11) NOT NULL,
  `name` varchar(20) NOT NULL,
  `price` int(10) NOT NULL,
  `description` varchar(100) NOT NULL,
  `image` varchar(255) NOT NULL,
  `stock` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `product`
--

INSERT INTO `product` (`id`, `name`, `price`, `description`, `image`, `stock`) VALUES
(16, 'himalayan', 225000, 'The **Royal Enfield himalayan** is a legendary motorcycle known for its iconic thump and timeless de', 'uploads/himalayan.avif', 4),
(18, 'classic 350', 200000, 'The Royal Enfield Classic 350 is powered by a 349.34 cc air-cooled engine which produces 20.21 PS @ ', 'uploads/classic350.webp', 3),
(19, 'bullet 450', 60000, 'The Royal Enfield Bullet 450 is a motorcycle with a 452 cc air-cooled engine that produces 40.02 PS ', 'uploads/bullet350.avif', 4),
(20, 'scram 440', 100000, 'The Scram 440 a refined Long Stroke 443 cc Engine (LS 440) paired with a Six Speed Gearbox.', 'uploads/scram440.avif', 4),
(21, 'Guerrilla 450', 150000, 'The Royal Enfield Guerrilla 450 is a modern-retro street naked motorcycle.', 'uploads/guerrilla_450_motorcycle.avif', 5),
(22, 'hunter 350', 200000, 'The **Royal Enfield Hunter 350** is a modern, agile motorcycle designed for urban commuting.', 'uploads/hunter350.avif', 6);

-- --------------------------------------------------------

--
-- Table structure for table `registration`
--

CREATE TABLE `registration` (
  `userid` int(11) NOT NULL,
  `firstnm` varchar(20) NOT NULL,
  `lastnm` varchar(20) NOT NULL,
  `usernm` varchar(20) NOT NULL,
  `password` varchar(6) NOT NULL,
  `email` varchar(40) NOT NULL,
  `phonno` varchar(10) NOT NULL,
  `address` varchar(100) NOT NULL,
  `country` varchar(20) NOT NULL,
  `state` varchar(20) NOT NULL,
  `date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `registration`
--

INSERT INTO `registration` (`userid`, `firstnm`, `lastnm`, `usernm`, `password`, `email`, `phonno`, `address`, `country`, `state`, `date`) VALUES
(15, 'hetvi', 'bhanderi', 'hetu', '123', 'hetu@gmail.com', '9558976904', 'mandasan', 'India', 'gujarat', '2025-01-05 18:30:00'),
(16, 'jinsha', 'godhani', 'jinu', '456', 'jinshagodhani@gmail.com', '9316058810', 'Navi Haliyad', 'India', 'gujarat', '2025-02-13 15:21:08'),
(17, 'drashti', 'gajera', 'datu', '123', 'rudra@gmail.com', '0985746321', 'mandasan', 'India', 'gujarat', '0000-00-00 00:00:00'),
(18, 'harshita', 'kakadiya', 'harshita', '789', 'harshita@gmail.com', '9265050876', 'Jarakhiya', 'gujarat', 'india', '2025-02-18 18:30:00'),
(19, 'mirali', 'gorakhiya', 'mira', '753', 'miralimem@gmail.com', '7412365890', 'Amreli', 'india', 'gujarat', '2025-02-19 18:30:00');

-- --------------------------------------------------------

--
-- Table structure for table `services`
--

CREATE TABLE `services` (
  `service_id` int(11) NOT NULL,
  `usernm` varchar(255) DEFAULT NULL,
  `vehicle_id` varchar(255) DEFAULT NULL,
  `service_type` varchar(255) DEFAULT NULL,
  `date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `services`
--

INSERT INTO `services` (`service_id`, `usernm`, `vehicle_id`, `service_type`, `date`) VALUES
(47, 'jinu', 'GJ141949', 'washing', '2025-02-13'),
(48, 'mira', 'GJ145893', 'washing', '2025-02-20');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `bill`
--
ALTER TABLE `bill`
  ADD PRIMARY KEY (`bill_id`),
  ADD KEY `o_id` (`o_id`);

--
-- Indexes for table `cart`
--
ALTER TABLE `cart`
  ADD PRIMARY KEY (`cart_id`),
  ADD KEY `id` (`id`),
  ADD KEY `userid` (`userid`);

--
-- Indexes for table `feedback`
--
ALTER TABLE `feedback`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`o_id`);

--
-- Indexes for table `product`
--
ALTER TABLE `product`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `registration`
--
ALTER TABLE `registration`
  ADD PRIMARY KEY (`userid`) USING BTREE;

--
-- Indexes for table `services`
--
ALTER TABLE `services`
  ADD PRIMARY KEY (`service_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bill`
--
ALTER TABLE `bill`
  MODIFY `bill_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- AUTO_INCREMENT for table `cart`
--
ALTER TABLE `cart`
  MODIFY `cart_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=43;

--
-- AUTO_INCREMENT for table `feedback`
--
ALTER TABLE `feedback`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `o_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=99;

--
-- AUTO_INCREMENT for table `product`
--
ALTER TABLE `product`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT for table `registration`
--
ALTER TABLE `registration`
  MODIFY `userid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT for table `services`
--
ALTER TABLE `services`
  MODIFY `service_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=49;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `bill`
--
ALTER TABLE `bill`
  ADD CONSTRAINT `bill_ibfk_1` FOREIGN KEY (`o_id`) REFERENCES `orders` (`o_id`);

--
-- Constraints for table `cart`
--
ALTER TABLE `cart`
  ADD CONSTRAINT `cart_ibfk_1` FOREIGN KEY (`id`) REFERENCES `product` (`id`),
  ADD CONSTRAINT `cart_ibfk_2` FOREIGN KEY (`userid`) REFERENCES `registration` (`userid`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
