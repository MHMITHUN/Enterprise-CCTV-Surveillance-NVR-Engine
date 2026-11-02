#!/usr/bin/env python3
"""
Enterprise IP Camera RTSP Stream Heartbeat & Dropout Monitor
Author: MD. Mahamudul Hasan (IT Officer)
Repository: Enterprise-CCTV-Surveillance-NVR-Engine
License: MIT

Continuously monitors enterprise RTSP camera channels, measures round-trip latency,
flags connection timeouts or stream corruption, and dispatches incident alerts.
"""

import time
import socket
import json
import logging
from typing import List, Dict, Any
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [CCTV-NOC] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('CCTVMonitor')


class CameraChannel:
    def __init__(self, channel_id: str, name: str, ip: str, port: int = 554,
                 rtsp_path: str = '/live/ch0', zone: str = 'General'):
        self.channel_id = channel_id
        self.name = name
        self.ip = ip
        self.port = port
        self.rtsp_path = rtsp_path
        self.zone = zone
        self.status = 'ONLINE'
        self.last_check = None
        self.latency_ms = 0.0
        self.consecutive_failures = 0

    @property
    def rtsp_url(self) -> str:
        return f"rtsp://admin:******@{self.ip}:{self.port}{self.rtsp_path}"


class CCTVStreamMonitor:
    def __init__(self, channels: List[CameraChannel], timeout_sec: float = 2.0,
                 alert_threshold: int = 2):
        self.channels = channels
        self.timeout = timeout_sec
        self.alert_threshold = alert_threshold
        self.incident_history: List[Dict[str, Any]] = []

    def check_channel_socket(self, camera: CameraChannel) -> bool:
        """Check TCP handshake on RTSP port 554 and compute round-trip latency."""
        start_time = time.time()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                sock.connect((camera.ip, camera.port))
                camera.latency_ms = round((time.time() - start_time) * 1000, 2)
                camera.status = 'ONLINE'
                camera.consecutive_failures = 0
                camera.last_check = datetime.now().isoformat()
                return True
        except (socket.timeout, socket.error) as err:
            camera.latency_ms = 0.0
            camera.consecutive_failures += 1
            camera.last_check = datetime.now().isoformat()

            if camera.consecutive_failures >= self.alert_threshold:
                if camera.status != 'OFFLINE':
                    camera.status = 'OFFLINE'
                    self.trigger_incident_alert(camera, str(err))
            return False

    def trigger_incident_alert(self, camera: CameraChannel, error_msg: str):
        """Dispatch instant incident notification to IT operations team."""
        incident = {
            'event': 'CCTV_STREAM_DROP_CRITICAL',
            'channel_id': camera.channel_id,
            'channel_name': camera.name,
            'ip_address': camera.ip,
            'zone': camera.zone,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': error_msg,
            'action_required': 'Dispatch technician to inspect PoE switch port / camera power.'
        }
        self.incident_history.append(incident)
        logger.error(
            f"ALERT: Channel {camera.channel_id} ({camera.name} - {camera.ip}) "
            f"DROPPED in zone '{camera.zone}'! Cause: {error_msg}"
        )

    def run_polling_cycle(self) -> Dict[str, Any]:
        """Execute one complete polling cycle across all registered channels."""
        logger.info(f"Initiating health check for {len(self.channels)} camera streams...")
        results = []
        for cam in self.channels:
            is_alive = self.check_channel_socket(cam)
            results.append({
                'id': cam.channel_id,
                'name': cam.name,
                'ip': cam.ip,
                'status': cam.status,
                'latency_ms': cam.latency_ms,
                'zone': cam.zone
            })
            time.sleep(0.05)  # small pacing between sockets

        online_count = sum(1 for r in results if r['status'] == 'ONLINE')
        health_pct = round((online_count / len(self.channels)) * 100, 1)
        logger.info(f"Polling cycle complete. System Health: {health_pct}% ({online_count}/{len(self.channels)} online)")
        return {
            'timestamp': datetime.now().isoformat(),
            'total_channels': len(self.channels),
            'online_channels': online_count,
            'health_score': health_pct,
            'channels': results
        }


def get_default_factory_topology() -> List[CameraChannel]:
    """Sample enterprise factory CCTV camera topology."""
    return [
        CameraChannel('CAM-01', 'Factory Main Gate Turnstiles', '192.168.20.101', zone='Perimeter Access'),
        CameraChannel('CAM-02', 'Sewing Production Line 04', '192.168.20.102', zone='Production Floor'),
        CameraChannel('CAM-03', 'Server Room IT Rack NOC', '192.168.20.103', zone='Critical Infrastructure'),
        CameraChannel('CAM-04', 'Finished Goods Shipping Dock', '192.168.20.104', zone='Logistics & Cargo'),
    ]


if __name__ == '__main__':
    topology = get_default_factory_topology()
    monitor = CCTVStreamMonitor(topology, timeout_sec=1.0)
    print("\n--- Running Sample CCTV Health Polling Cycle ---")
    summary = monitor.run_polling_cycle()
    print(json.dumps(summary, indent=2))
