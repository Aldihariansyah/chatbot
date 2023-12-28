-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 29 Nov 2023 pada 03.51
-- Versi server: 10.4.28-MariaDB
-- Versi PHP: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `madani`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `admin`
--

CREATE TABLE `admin` (
  `nama` varchar(25) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `username` varchar(30) NOT NULL,
  `password` varchar(30) NOT NULL,
  `id` int(11) NOT NULL
) 

--
-- Dumping data untuk tabel `admin`
--

INSERT INTO `admin` (`nama`, `phone`, `username`, `password`, `id`) VALUES
('imam', '0834567812', 'uki', 'kamiuu', 5),
('imam', '09876543', 'aldi', 'admin', 7),
('kami', '9876545678', 'axii', '12345', 8);

-- --------------------------------------------------------

--
-- Struktur dari tabel `doctor_schedule`
--

CREATE TABLE `doctor_schedule` (
  `id` int(11) NOT NULL,
  `id_spesialis` int(11) NOT NULL,
  `nama_dokter` varchar(255) NOT NULL,
  `specialization` varchar(255) DEFAULT NULL,
  `day` varchar(255) DEFAULT NULL,
  `jam_awal` time DEFAULT NULL,
  `jam_akhir` time DEFAULT NULL
) 

--
-- Dumping data untuk tabel `doctor_schedule`
--

INSERT INTO `doctor_schedule` (`id`, `id_spesialis`, `nama_dokter`, `specialization`, `day`, `jam_awal`, `jam_akhir`) VALUES
(12, 1, 'dr. EKA PERMATA SARI. Sp.A', 'SPESIALIS ANAK', 'SENIN', '07:30:00', '14:00:00'),
(13, 1, 'dr. RITA MEY RINA. Sp.A', 'SPESIALIS ANAK', 'SELASA', '07:30:00', '14:00:00'),
(14, 1, 'dr. NOFARENI. Sp.A', 'SPESIALIS ANAK', 'RABU', '07:30:00', '14:00:00'),
(15, 1, 'dr. YURMA. Sp. A', 'SPESIALIS ANAK', 'KAMIS', '07:30:00', '14:00:00'),
(16, 1, 'dr. EKA PERMATA SARI. Sp.A', 'SPESIALIS ANAK', 'JUMAT', '07:30:00', '14:00:00'),
(17, 1, 'dr. RITA MEY RINA. Sp.A', 'SPESIALIS ANAK', 'SABTU', '07:30:00', '14:00:00'),
(18, 2, 'dr. TAUFIQURRAHMAN. Sp. THT-KL. MARS', 'SPESIALIS THT-KL', 'SENIN', '07:30:00', '14:00:00'),
(19, 2, 'dr. RISDAWATI. Sp.THT-KL', 'SPESIALIS THT-KL', 'SELASA', '07:30:00', '14:00:00'),
(20, 2, 'dr. TAUFIQURRAHMAN. Sp. THT-KL. MARS', 'SPESIALIS THT-KL', 'RABU', '07:30:00', '14:00:00'),
(21, 2, 'dr. RISDAWATI. Sp.THT-KL', 'SPESIALIS THT-KL', 'KAMIS', '07:30:00', '14:00:00'),
(22, 2, 'dr. TAUFIQURRAHMAN. Sp. THT-KL. MARS', 'SPESIALIS THT-KL', 'JUMAT', '07:30:00', '14:00:00'),
(23, 2, 'dr. RISDAWATI. Sp.THT-KL', 'SPESIALIS THT-KL', 'SABTU', '07:30:00', '14:00:00'),
(24, 3, 'dr. T. AFRINA. Sp.M', 'SPESIALIS MATA', 'SENIN', '07:30:00', '14:00:00'),
(25, 3, 'dr. SHERLY MUCHLIS. Sp.M', 'SPESIALIS MATA', 'SELASA', '07:30:00', '14:00:00'),
(26, 3, 'dr. FEBY HELWINA. Sp.M', 'SPESIALIS MATA', 'RABU', '07:30:00', '14:00:00'),
(27, 3, 'dr. FEBY HELWINA. Sp.M', 'SPESIALIS MATA', 'KAMIS', '07:30:00', '14:00:00'),
(28, 3, 'dr. T. AFRINA. Sp.M', 'SPESIALIS MATA', 'JUMAT', '07:30:00', '14:00:00'),
(29, 3, 'dr. SHERLY MUCHLIS. Sp.M', 'SPESIALIS MATA', 'SABTU', '07:30:00', '14:00:00'),
(30, 4, 'dr. FITRI ANDRIYANI. Sp. Rad', 'SPESIALIS RADIOLOGI', 'SENIN', '07:30:00', '14:00:00'),
(31, 4, 'dr. FITRI ANDRIYANI. Sp. Rad', 'SPESIALIS RADIOLOGI', 'SELASA', '07:30:00', '14:00:00'),
(32, 4, 'dr. FITRI ANDRIYANI. Sp. Rad', 'SPESIALIS RADIOLOGI', 'RABU', '07:30:00', '14:00:00'),
(33, 4, 'dr. FITRI ANDRIYANI. Sp. Rad', 'SPESIALIS RADIOLOGI', 'KAMIS', '07:30:00', '14:00:00'),
(34, 4, 'dr. FITRI ANDRIYANI. Sp. Rad', 'SPESIALIS RADIOLOGI', 'JUMAT', '07:30:00', '14:00:00'),
(35, 4, 'dr. FITRI ANDRIYANI. Sp. Rad', 'SPESIALIS RADIOLOGI', 'SABTU', '07:30:00', '14:00:00'),
(38, 5, 'dr. MAGDI AYUZA. Sp.B', 'SPESIALIS BEDAH UMUM', 'RABU', '07:30:00', '14:00:00'),
(39, 5, 'dr. MAGDI AYUZA. Sp.B', 'SPESIALIS BEDAH UMUM', 'KAMIS', '07:30:00', '14:00:00'),
(40, 5, 'dr. MAHENDRA. Sp.B', 'SPESIALIS BEDAH UMUM', 'JUMAT', '07:30:00', '14:00:00'),
(41, 5, 'dr. MAHENDRA. Sp.B', 'SPESIALIS BEDAH UMUM', 'SABTU', '07:30:00', '14:00:00'),
(42, 6, 'dr. DIDI YUDA PUTRA. Sp.PD', 'SPESIALIS PENYAKIT DALAM', 'SENIN', '07:30:00', '14:00:00'),
(43, 6, 'dr. DIDI YUDA PUTRA. Sp.PD', 'SPESIALIS PENYAKIT DALAM', 'SELASA', '07:30:00', '14:00:00'),
(44, 6, 'dr. WIDYA SAFITRI. Sp.PD.', 'SPESIALIS PENYAKIT DALAM', 'RABU', '07:30:00', '14:00:00'),
(45, 6, 'dr. ARNALDI FERNANDO. Sp.PD', 'SPESIALIS PENYAKIT DALAM', 'KAMIS', '07:30:00', '14:00:00'),
(46, 6, 'dr. RAMA FADILA. Sp.PD', 'SPESIALIS PENYAKIT DALAM', 'JUMAT', '07:30:00', '14:00:00'),
(47, 6, 'dr. RAMA FADILA. Sp.PD', 'SPESIALIS PENYAKIT DALAM', 'SABTU', '07:30:00', '14:00:00'),
(48, 7, 'dr. TUTI ASRYANI. Sp.PK', 'SPESIALIS PATOLOGI KLINIK', 'SENIN', '07:30:00', '14:00:00'),
(49, 7, 'dr. RENI LENGGOGENI. Sp.PK', 'SPESIALIS PATOLOGI KLINIK', 'SELASA', '07:30:00', '14:00:00'),
(50, 7, 'dr. RIDHA AMALIA. Sp.PK', 'SPESIALIS PATOLOGI KLINIK', 'RABU', '07:30:00', '14:00:00'),
(54, 7, 'dr. RIDHA AMALIA. Sp.PK', 'SPESIALIS PATOLOGI KLINIK', 'KAMIS', '07:30:00', '14:00:00'),
(55, 7, 'dr. DYNA MERYTA A. M.Ked (clin-path). Sp.PK(k)', 'SPESIALIS PATOLOGI KLINIK', 'JUMAT', '07:30:00', '14:00:00'),
(56, 7, 'dr. TUTI ASRYANI. Sp.PK', 'SPESIALIS PATOLOGI KLINIK', 'SABTU', '07:30:00', '14:00:00'),
(57, 8, 'dr. MEILANIA HASNATASHA. Sp.DV', 'SPESIALIS KULIT DAN KELAMIN', 'SENIN', '07:30:00', '14:00:00'),
(58, 8, 'dr. MEILANIA HASNATASHA. Sp.DV', 'SPESIALIS KULIT DAN KELAMIN', 'SELASA', '07:30:00', '14:00:00'),
(59, 8, 'dr. MEILANIA HASNATASHA. Sp.DV', 'SPESIALIS KULIT DAN KELAMIN', 'RABU', '07:30:00', '14:00:00'),
(60, 8, 'dr. DINA FEBRIANI. Sp.DV', 'SPESIALIS KULIT DAN KELAMIN', 'KAMIS', '07:30:00', '14:00:00'),
(61, 8, 'dr. DINA FEBRIANI. Sp.DV', 'SPESIALIS KULIT DAN KELAMIN', 'JUMAT', '07:30:00', '14:00:00'),
(62, 8, 'dr. DINA FEBRIANI. Sp.DV', 'SPESIALIS KULIT DAN KELAMIN', 'SABTU', '07:30:00', '14:00:00'),
(63, 9, 'dr. BUDI. Sp.OG', 'SPESIALIS KEBIDANAN DAN KANDUNGAN', 'SENIN', '07:30:00', '14:00:00'),
(64, 9, 'dr. BUDI. Sp.OG', 'SPESIALIS KEBIDANAN DAN KANDUNGAN', 'SELASA', '07:30:00', '14:00:00'),
(65, 9, 'dr. DIAN FEBRINA. Sp.OG', 'SPESIALIS KEBIDANAN DAN KANDUNGAN', 'RABU', '07:30:00', '14:00:00'),
(66, 9, 'dr. ROMI ALFIANTO. Sp. OG', 'SPESIALIS KEBIDANAN DAN KANDUNGAN', 'KAMIS', '07:30:00', '14:00:00'),
(67, 9, 'dr. ROMI ALFIANTO. Sp. OG', 'SPESIALIS KEBIDANAN DAN KANDUNGAN', 'JUMAT', '07:30:00', '14:00:00'),
(75, 9, 'dr. DIAN FEBRINA. Sp.OG', 'SPESIALIS KEBIDANAN DAN KANDUNGAN', 'SABTU', '07:30:00', '14:00:00'),
(76, 10, 'drg. YULIANASARI S. Sp.KG', 'DOKTER GIGI SPESIALIS KONSERVASI', 'SENIN', '07:30:00', '14:00:00'),
(77, 10, 'drg. YULIANASARI S. Sp.KG', 'DOKTER GIGI SPESIALIS KONSERVASI', 'SELASA', '07:30:00', '14:00:00'),
(78, 10, 'drg. YULIANASARI S. Sp.KG', 'DOKTER GIGI SPESIALIS KONSERVASI', 'RABU', '07:30:00', '14:00:00'),
(79, 10, 'drg. YULIANASARI S. Sp.KG', 'DOKTER GIGI SPESIALIS KONSERVASI', 'KAMIS', '07:30:00', '14:00:00'),
(80, 10, 'drg. YULIANASARI S. Sp.KG', 'DOKTER GIGI SPESIALIS KONSERVASI', 'JUMAT', '07:30:00', '14:00:00'),
(81, 10, 'drg. YULIANASARI S. Sp.KG', 'DOKTER GIGI SPESIALIS KONSERVASI', 'SABTU', '07:30:00', '14:00:00'),
(82, 11, 'drg. DESWI ARWELI. Sp.Ort', 'DOKTER GIGI SPESIALIS ORTHODONTIST', 'SENIN', '07:30:00', '14:00:00'),
(83, 11, 'drg. DESWI ARWELI. Sp.Ort', 'DOKTER GIGI SPESIALIS ORTHODONTIST', 'SELASA\r\n', '07:30:00', '14:00:00'),
(84, 11, 'drg. DESWI ARWELI. Sp.Ort', 'DOKTER GIGI SPESIALIS ORTHODONTIST', 'RABU', '07:30:00', '14:00:00'),
(85, 11, 'drg. DESWI ARWELI. Sp.Ort', 'DOKTER GIGI SPESIALIS ORTHODONTIST', 'KAMIS', '07:30:00', '14:00:00'),
(86, 11, 'drg. DESWI ARWELI. Sp.Ort', 'DOKTER GIGI SPESIALIS ORTHODONTIST', 'JUMAT', '07:30:00', '14:00:00'),
(87, 11, 'drg. DESWI ARWELI. Sp.Ort', 'DOKTER GIGI SPESIALIS ORTHODONTIST', 'SABTU', '07:30:00', '14:00:00');

-- --------------------------------------------------------

--
-- Struktur dari tabel `patient`
--

CREATE TABLE `patient` (
  `id` int(11) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `nik` varchar(255) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `tgl_lahir` date DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `specialization` varchar(255) DEFAULT NULL,
  `dokter` varchar(255) DEFAULT NULL,
  `day` varchar(255) DEFAULT NULL,
  `tanggal` date DEFAULT NULL,
  `sesi` varchar(25) DEFAULT NULL,
  `booking_code` varchar(255) NOT NULL PRIMARY UNIQUE,
  `verif` tinyint(1) DEFAULT 0,
  `referral_letter` longblob DEFAULT NULL,
  `kk_photo` longblob DEFAULT NULL,
  `bpjs_photo` longblob DEFAULT NULL,
  `ktp_photo` longblob DEFAULT NULL
)

--
-- Dumping data untuk tabel `patient`
--

INSERT INTO `patient` (`id`, `name`, `nik`, `address`, `tgl_lahir`, `phone`, `specialization`, `dokter`, `day`, `tanggal`, `sesi`, `booking_code`, `verif`, `referral_letter`, `kk_photo`, `bpjs_photo`, `ktp_photo`) VALUES
(1, 'd', 'dq', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '', 0, NULL, NULL, NULL, NULL);

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `doctor_schedule`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `patient`
--
ALTER TABLE `patient`
  ADD PRIMARY KEY (`booking_code`),
  ADD UNIQUE KEY `booking_code` (`booking_code`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT untuk tabel `doctor_schedule`
--
ALTER TABLE `doctor_schedule`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=96;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
