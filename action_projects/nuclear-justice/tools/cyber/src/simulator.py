"""
Nuclear Facility Simulator —用于测试网络破坏剂的沙箱环境。
模拟：离心机阵列、冷却系统、传感器、控制网络。
这是模拟环境，不接触真实基础设施。
"""

import time
import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import json

@dataclass
class Centrifuge:
    """单个离心机"""
    id: str
    rpm: float = 0.0
    temperature: float = 25.0  # °C
    status: str = "running"  # running, stopped, faulty
    vibration: float = 0.0
    lifetime_hours: float = 0.0

@dataclass
class CoolantSystem:
    """冷却系统"""
    flow_rate: float = 100.0  # L/min
    temperature: float = 30.0  # °C
    pressure: float = 2.0  # bar
    pump_status: bool = True
    alarms: List[str] = field(default_factory=list)

@dataclass
class SensorNetwork:
    """传感器网络 (温度、压力、振动、辐射)"""
    readings: Dict[str, float] = field(default_factory=dict)
    compromised: bool = False  # 是否被入侵

@dataclass
class ControlSystem:
    """控制系统 (SCADA)"""
    auto_mode: bool = True
    setpoints: Dict[str, float] = field(default_factory=dict)
    alarms: List[str] = field(default_factory=list)

@dataclass
class NuclearFacility:
    """完整核设施模拟"""
    name: str
    centrifuge_array: List[Centrifuge]
    coolant: CoolantSystem
    sensors: SensorNetwork
    control: ControlSystem
    enriched_uranium_kg: float = 0.0
    operational: bool = True
    log: List[str] = field(default_factory=list)

    def step(self, dt: float = 1.0):
        """推进模拟一个时间步长 (seconds)"""
        if not self.operational:
            return

        # 更新离心机
        for c in self.centrifuge_array:
            c.lifetime_hours += dt / 3600
            if c.status == "running":
                # RPM有轻微波动
                c.rpm += random.uniform(-10, 10)
                c.rpm = max(0, c.rpm)
                # 温度随rpm上升
                c.temperature += (c.rpm / 100000) * dt
                # 振动随不balance增加
                c.vibration += random.uniform(-0.1, 0.1)
                c.vibration = max(0, c.vibration)

                # 如果温度过高或振动过大 → 自动停机
                if c.temperature > 80 or c.vibration > 5.0:
                    c.status = "faulty"
                    self.log.append(f"[ALERT] Centrifuge {c.id} failed: T={c.temperature:.1f}, V={c.vibration:.1f}")

        # 更新冷却系统
        if self.coolant.pump_status:
            self.coolant.temperature += random.uniform(-0.1, 0.1)  # 缓慢变化
            self.coolant.flow_rate = max(0, self.coolant.flow_rate + random.uniform(-2, 2))
        else:
            self.coolant.temperature += 0.5  # 无冷却时温度上升
            if self.coolant.temperature > 50:
                self.log.append("[WARNING] Coolant temperature high")

        #  enriching uranium: 每运行一小时，浓缩量增加
        if all(c.status == "running" for c in self.centrifuge_array):
            self.enriched_uranium_kg += 0.01 * dt / 3600  # 0.01 kg/h per cascade

        # 传感器读数更新
        self.sensors.readings = {
            "overall_rpm": sum(c.rpm for c in self.centrifuge_array) / len(self.centrifuge_array),
            "avg_temp": sum(c.temperature for c in self.centrifuge_array) / len(self.centrifuge_array),
            "coolant_temp": self.coolant.temperature,
            "coolant_flow": self.coolant.flow_rate,
            "enriched_level": self.enriched_uranium_kg,
        }

    def inject_cyber_error(self, error_type: str, severity: float = 0.5):
        """注入网络错误 (模拟黑客攻击)"""
        if error_type == "rpm_spike":
            for c in self.centrifuge_array:
                c.rpm += random.uniform(5000, 20000) * severity
            self.log.append(f"[CYBER] RPM spike injected (+{severity*10000:.0f} avg)")
        elif error_type == "temp_drift":
            for c in self.centrifuge_array:
                c.temperature += 30 * severity
            self.log.append(f"[CYBER] Temperature drift injected (+{30*severity:.1f}°C)")
        elif error_type == "sensor_spoof":
            self.sensors.compromised = True
            self.sensors.readings["enriched_level"] *= (1 + severity)  # 虚报产量
            self.log.append("[CYBER] Sensor data spoofed")
        elif error_type == "coolant_cut":
            self.coolant.pump_status = False
            self.log.append("[CYBER] Coolant pump disabled")
        elif error_type == "cascade_imbalance":
            # 让一些离心机停，一些加速，造成不平衡
            for i, c in enumerate(self.centrifuge_array):
                if i % 2 == 0:
                    c.rpm *= 0.1  # 减速至10%
                else:
                    c.rpm *= 1.5  # 加速
            self.log.append("[CYBER] Cascade imbalance created")

    def status_report(self) -> Dict:
        return {
            "facility": self.name,
            "operational": self.operational,
            "centrifuges_running": sum(1 for c in self.centrifuge_array if c.status == "running"),
            "total_centrifuges": len(self.centrifuge_array),
            "enriched_uranium_kg": round(self.enriched_uranium_kg, 3),
            "coolant_temp": round(self.coolant.temperature, 1),
            "sensor_compromised": self.sensors.compromised,
            "recent_alerts": self.log[-5:],
        }

# ------------------------------
# Helper functions
# ------------------------------

def build_default_facility(name: str = "NucFac-1", n_centrifuges: int = 100) -> NuclearFacility:
    centrifuges = [Centrifuge(id=f"CF-{i+1:03d}", rpm=90000, temperature=25.0) for i in range(n_centrifuges)]
    coolant = CoolantSystem(flow_rate=100.0, temperature=30.0, pressure=2.0)
    sensors = SensorNetwork(readings={})
    control = ControlSystem(auto_mode=True, setpoints={"rpm": 90000, "temp": 30.0})
    return NuclearFacility(name, centrifuges, coolant, sensors, control)

def simulate_operation(facility: NuclearFacility, hours: float = 1.0):
    """模拟运行若干小时"""
    steps = int(hours * 3600)  # 每秒一步
    for _ in range(steps):
        facility.step(1.0)
    return facility
