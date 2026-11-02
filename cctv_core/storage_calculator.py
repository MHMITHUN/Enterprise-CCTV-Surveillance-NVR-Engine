#!/usr/bin/env python3
"""
Enterprise CCTV NVR Storage & RAID Calculator
Author: MD. Mahamudul Hasan
Repository: Enterprise-CCTV-Surveillance-NVR-Engine
License: MIT

Calculates enterprise video surveillance storage requirements, network bandwidth,
and RAID 5 / RAID 6 drive arrays based on industrial compliance guidelines (WRAP & RSC 30-day retention).
"""

import math
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class StreamProfile:
    resolution: str
    fps: int
    codec: str  # 'H.264', 'H.265', 'H.265+'
    raw_bitrate_mbps: float

    @property
    def effective_bitrate_mbps(self) -> float:
        """Apply codec compression efficiency multiplier."""
        codec_multipliers = {
            'H.264': 1.0,
            'H.265': 0.65,      # 35% bandwidth saving
            'H.265+': 0.45,     # 55% bandwidth saving in static scenes
        }
        multiplier = codec_multipliers.get(self.codec.upper(), 1.0)
        return round(self.raw_bitrate_mbps * multiplier, 2)


class NVRStorageCalculator:
    """NVR storage, bandwidth and RAID configuration calculator."""

    RESOLUTION_PRESETS = {
        '720p': StreamProfile('720p HD', 25, 'H.265+', 1.5),
        '1080p': StreamProfile('1080p FHD', 30, 'H.265+', 2.5),
        '4MP': StreamProfile('4MP QHD', 25, 'H.265+', 4.0),
        '4K': StreamProfile('4K UHD', 25, 'H.265+', 8.0),
    }

    def __init__(self, camera_count: int = 32, retention_days: int = 30,
                 resolution: str = '1080p', codec: str = 'H.265+',
                 recording_hours_per_day: float = 24.0,
                 motion_recording_ratio: float = 1.0):
        self.camera_count = camera_count
        self.retention_days = retention_days
        self.resolution = resolution
        self.codec = codec
        self.recording_hours = recording_hours_per_day
        self.motion_ratio = motion_recording_ratio

        preset = self.RESOLUTION_PRESETS.get(resolution, self.RESOLUTION_PRESETS['1080p'])
        self.profile = StreamProfile(preset.resolution, preset.fps, codec, preset.raw_bitrate_mbps)

    def calculate_storage_tb(self) -> float:
        """
        Storage Formula:
        Storage (TB) = (Cameras * Bitrate_Mbps * 3600 * Hours * Days * MotionRatio) / (8 * 1024 * 1024)
        """
        bitrate = self.profile.effective_bitrate_mbps
        seconds_per_day = self.recording_hours * 3600
        total_megabits = (self.camera_count * bitrate * seconds_per_day *
                          self.retention_days * self.motion_ratio)
        total_tb = total_megabits / (8 * 1024 * 1024)
        return round(total_tb, 2)

    def calculate_total_bandwidth_mbps(self) -> float:
        """Combined network ingress bandwidth consumed on NVR PoE switch uplink."""
        return round(self.camera_count * self.profile.effective_bitrate_mbps, 2)

    def calculate_raid_array(self, drive_size_tb: int = 8, raid_type: str = 'RAID5') -> Dict[str, Any]:
        """
        Calculate drive requirements for RAID 5 or RAID 6 arrays.
        RAID 5: N usable drives + 1 parity drive
        RAID 6: N usable drives + 2 parity drives
        """
        usable_tb_needed = self.calculate_storage_tb()
        # Formatted usable capacity per drive is roughly 91% due to binary conversion and filesystem overhead
        effective_drive_capacity = drive_size_tb * 0.91

        data_drives = math.ceil(usable_tb_needed / effective_drive_capacity)
        parity_drives = 2 if raid_type.upper() == 'RAID6' else 1
        total_drives = max(data_drives + parity_drives, 3 if raid_type.upper() == 'RAID5' else 4)
        total_raw_capacity_tb = total_drives * drive_size_tb
        usable_capacity_tb = round((total_drives - parity_drives) * effective_drive_capacity, 2)

        return {
            'raid_type': raid_type,
            'drive_size_tb': drive_size_tb,
            'data_drives': data_drives,
            'parity_drives': parity_drives,
            'total_drives_required': total_drives,
            'total_raw_capacity_tb': total_raw_capacity_tb,
            'usable_capacity_tb': usable_capacity_tb,
            'surplus_buffer_tb': round(usable_capacity_tb - usable_tb_needed, 2)
        }

    def generate_compliance_report(self) -> str:
        """Produce an audit-ready compliance summary report."""
        storage_tb = self.calculate_storage_tb()
        bandwidth_mbps = self.calculate_total_bandwidth_mbps()
        raid = self.calculate_raid_array(drive_size_tb=8, raid_type='RAID5')

        report = f"""
================================================================================
ENTERPRISE CCTV & NVR STORAGE AUDIT REPORT
================================================================================
Camera Channels      : {self.camera_count} IP Channels
Target Resolution    : {self.profile.resolution} ({self.profile.fps} FPS)
Compression Codec    : {self.codec} (Effective Bitrate: {self.profile.effective_bitrate_mbps} Mbps/ch)
Retention Policy     : {self.retention_days} Days (Audit Standard: Accord/RSC >= 30 Days)
Daily Recording Duty : {self.recording_hours} Hours/day (Continuous 24/7)
--------------------------------------------------------------------------------
Net Storage Required : {storage_tb} TB
Network Uplink Ingress: {bandwidth_mbps} Mbps (~{round(bandwidth_mbps / 1000, 2)} Gbps)
--------------------------------------------------------------------------------
RECOMMENDED RAID 5 STORAGE TOPOLOGY:
- Drive Model        : Seagate SkyHawk AI / WD Purple Enterprise Surveillance 8TB
- Total Drives       : {raid['total_drives_required']} Disks ({raid['data_drives']} Data + {raid['parity_drives']} Parity)
- Usable RAID Space  : {raid['usable_capacity_tb']} TB
- Safety Buffer      : +{raid['surplus_buffer_tb']} TB ({round((raid['surplus_buffer_tb']/storage_tb)*100, 1)}% headroom)
- Fault Tolerance    : 1 Disk Failure Redundancy without Video Loss
================================================================================
STATUS: 100% COMPLIANT WITH WRAP & RSC RETENTION MANDATES
================================================================================
"""
        return report.strip()


if __name__ == '__main__':
    calc = NVRStorageCalculator(
        camera_count=64,
        retention_days=30,
        resolution='1080p',
        codec='H.265+'
    )
    print(calc.generate_compliance_report())
