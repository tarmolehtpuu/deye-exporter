from typing import Dict

from prometheus import Metric

METRICS: Dict[str, Metric] = {
    # --- 1. SYSTEM ---
    "inverter/status": (
        Metric.builder()
        .name("deye_inverter_status")
        .gauge()
        .desc("Inverter operational state")
        .build()
    ),
    "radiator_temp": (
        Metric.builder()
        .name("deye_radiator_temperature")
        .gauge()
        .desc("Inverter radiator temperature")
        .build()
    ),
    "ac/temperature": (
        Metric.builder()
        .name("deye_ac_temperature")
        .gauge()
        .desc("AC stage temperature")
        .build()
    ),
    "day_energy": (
        Metric.builder()
        .name("deye_day_energy")
        .gauge()
        .desc("Daily energy generated")
        .build()
    ),
    "total_energy": (
        Metric.builder()
        .name("deye_total_energy")
        .counter()
        .desc("Total lifetime energy generated")
        .build()
    ),
    "ac/ongrid": (
        Metric.builder()
        .name("deye_ac_ongrid")
        .gauge()
        .desc("Grid connection status")
        .build()
    ),
    "ac/relay_status": (
        Metric.builder()
        .name("deye_ac_relay_status")
        .gauge()
        .desc("AC relay status code")
        .build()
    ),
    # --- 2. SETTINGS ---
    "settings/active_power_regulation": (
        Metric.builder()
        .name("deye_setting_active_power_regulation")
        .gauge()
        .desc("Active power regulation percentage")
        .build()
    ),
    "settings/system_time": (
        Metric.builder()
        .name("deye_setting_system_time")
        .gauge()
        .desc("Inverter system epoch timestamp")
        .build()
    ),
    "settings/workmode": (
        Metric.builder()
        .name("deye_setting_workmode")
        .gauge()
        .desc("Inverter workmode ID")
        .build()
    ),
    "settings/solar_sell_max_power": (
        Metric.builder()
        .name("deye_setting_solar_sell_max_power")
        .gauge()
        .desc("Max solar sell power")
        .build()
    ),
    "settings/solar_sell": (
        Metric.builder()
        .name("deye_setting_solar_sell")
        .gauge()
        .desc("Solar sell toggle")
        .build()
    ),
    "settings/battery/maximum_charge_current": (
        Metric.builder()
        .name("deye_setting_battery_max_charge")
        .gauge()
        .desc("Configured max charge current")
        .build()
    ),
    "settings/battery/maximum_discharge_current": (
        Metric.builder()
        .name("deye_setting_battery_max_discharge")
        .gauge()
        .desc("Configured max discharge current")
        .build()
    ),
    "settings/battery/maximum_grid_charge_current": (
        Metric.builder()
        .name("deye_setting_battery_max_grid_charge")
        .gauge()
        .desc("Configured max grid charge current")
        .build()
    ),
    "settings/battery/grid_charge": (
        Metric.builder()
        .name("deye_setting_battery_grid_charge")
        .gauge()
        .desc("Grid charge toggle")
        .build()
    ),
    # --- 3. DC ---
    "dc/pv/power": (
        Metric.builder()
        .name("deye_dc_pv_power")
        .gauge()
        .desc("PV power per MPPT")
        .build()
    ),
    "dc/pv/voltage": (
        Metric.builder()
        .name("deye_dc_pv_voltage")
        .gauge()
        .desc("PV voltage per MPPT")
        .build()
    ),
    "dc/pv/current": (
        Metric.builder()
        .name("deye_dc_pv_current")
        .gauge()
        .desc("PV current per MPPT")
        .build()
    ),
    "dc/total_power": (
        Metric.builder()
        .name("deye_dc_total_power")
        .gauge()
        .desc("Total DC power")
        .build()
    ),
    # --- 4. BATTERY ---
    "battery/soc": (
        Metric.builder()
        .name("deye_battery_soc")
        .gauge()
        .desc("Total Battery SOC")
        .build()
    ),
    "battery/power": (
        Metric.builder()
        .name("deye_battery_power")
        .gauge()
        .desc("Battery power")
        .build()
    ),
    "battery/voltage": (
        Metric.builder()
        .name("deye_battery_voltage")
        .gauge()
        .desc("Battery voltage")
        .build()
    ),
    "battery/current": (
        Metric.builder()
        .name("deye_battery_current")
        .gauge()
        .desc("Battery current")
        .build()
    ),
    "battery/temperature": (
        Metric.builder()
        .name("deye_battery_temperature")
        .gauge()
        .desc("Battery temperature")
        .build()
    ),
    "battery/daily_charge": (
        Metric.builder().name("deye_battery_daily_charge").gauge().build()
    ),
    "battery/daily_discharge": (
        Metric.builder().name("deye_battery_daily_discharge").gauge().build()
    ),
    "battery/total_charge": (
        Metric.builder().name("deye_battery_total_charge").counter().build()
    ),
    "battery/total_discharge": (
        Metric.builder().name("deye_battery_total_discharge").counter().build()
    ),
    # --- 5. BMS ---
    "bms/soc": (
        Metric.builder()
        .name("deye_bms_soc")
        .gauge()
        .desc("BMS reported State of Charge")
        .build()
    ),
    "bms/voltage": (
        Metric.builder()
        .name("deye_bms_voltage")
        .gauge()
        .desc("BMS reported battery voltage")
        .build()
    ),
    "bms/current": (
        Metric.builder()
        .name("deye_bms_current")
        .gauge()
        .desc("BMS reported battery current")
        .build()
    ),
    "bms/temperature": (
        Metric.builder()
        .name("deye_bms_temperature")
        .gauge()
        .desc("BMS reported battery temperature")
        .build()
    ),
    "bms/charging_voltage": (
        Metric.builder()
        .name("deye_bms_charging_voltage")
        .gauge()
        .desc("BMS requested charging voltage")
        .build()
    ),
    "bms/discharge_voltage": (
        Metric.builder()
        .name("deye_bms_discharge_voltage")
        .gauge()
        .desc("BMS requested discharge voltage")
        .build()
    ),
    "bms/charge_current_limit": (
        Metric.builder()
        .name("deye_bms_charge_current_limit")
        .gauge()
        .desc("BMS charge current limit")
        .build()
    ),
    "bms/discharge_current_limit": (
        Metric.builder()
        .name("deye_bms_discharge_current_limit")
        .gauge()
        .desc("BMS discharge current limit")
        .build()
    ),
    "bms/charging_max_current": (
        Metric.builder()
        .name("deye_bms_charging_max_current")
        .gauge()
        .desc("BMS max allowable charge current")
        .build()
    ),
    "bms/discharge_max_current": (
        Metric.builder()
        .name("deye_bms_discharge_max_current")
        .gauge()
        .desc("BMS max allowable discharge current")
        .build()
    ),
    # --- 6. AC ---
    "ac/line/voltage": (
        Metric.builder()
        .name("deye_ac_voltage")
        .gauge()
        .desc("AC voltage per phase")
        .build()
    ),
    "ac/line/current": (
        Metric.builder()
        .name("deye_ac_current")
        .gauge()
        .desc("AC current per phase")
        .build()
    ),
    "ac/line/power": (
        Metric.builder()
        .name("deye_ac_power")
        .gauge()
        .desc("AC power per phase")
        .build()
    ),
    "ac/total_power": (
        Metric.builder()
        .name("deye_ac_total_power")
        .gauge()
        .desc("Total AC power")
        .build()
    ),
    "ac/total_internal_power": (
        Metric.builder()
        .name("deye_ac_total_internal_power")
        .gauge()
        .desc("Total power measured by internal CTs")
        .build()
    ),
    "ac/line/ct/internal": (
        Metric.builder()
        .name("deye_ac_ct_internal")
        .gauge()
        .desc("Internal CT power per phase")
        .build()
    ),
    "ac/line/ct/external": (
        Metric.builder()
        .name("deye_ac_ct_external")
        .gauge()
        .desc("External CT power per phase")
        .build()
    ),
    "ac/daily_energy_bought": (
        Metric.builder()
        .name("deye_ac_daily_energy_bought")
        .gauge()
        .desc("Daily energy imported from grid")
        .build()
    ),
    "ac/total_energy_bought": (
        Metric.builder()
        .name("deye_ac_total_energy_bought")
        .counter()
        .desc("Total lifetime energy imported from grid")
        .build()
    ),
    "ac/daily_energy_sold": (
        Metric.builder()
        .name("deye_ac_daily_energy_sold")
        .gauge()
        .desc("Daily energy exported to grid")
        .build()
    ),
    "ac/total_energy_sold": (
        Metric.builder()
        .name("deye_ac_total_energy_sold")
        .counter()
        .desc("Total lifetime energy exported to grid")
        .build()
    ),
    # --- 7. UPS ---
    "ac/ups/total_power": (
        Metric.builder()
        .name("deye_ac_ups_total_power")
        .gauge()
        .desc("Total UPS/Load output power")
        .build()
    ),
    "ac/ups/line/power": (
        Metric.builder()
        .name("deye_ac_ups_power")
        .gauge()
        .desc("UPS/Load power per phase")
        .build()
    ),
    "ac/ups/line/voltage": (
        Metric.builder()
        .name("deye_ac_ups_voltage")
        .gauge()
        .desc("UPS/Load voltage per phase")
        .build()
    ),
    "ac/ups/daily_energy": (
        Metric.builder()
        .name("deye_ac_ups_daily_energy")
        .gauge()
        .desc("Daily energy consumed by UPS/Load")
        .build()
    ),
    "ac/ups/total_energy": (
        Metric.builder()
        .name("deye_ac_ups_total_energy")
        .counter()
        .desc("Total lifetime energy consumed by UPS/Load")
        .build()
    ),
    # --- 8. GENERATOR ---
    "ac/generator/total_power": (
        Metric.builder()
        .name("deye_ac_generator_total_power")
        .gauge()
        .desc("Total generator input power")
        .build()
    ),
    "ac/generator/line/power": (
        Metric.builder()
        .name("deye_ac_generator_power")
        .gauge()
        .desc("Generator power per phase")
        .build()
    ),
    "ac/generator/line/voltage": (
        Metric.builder()
        .name("deye_ac_generator_voltage")
        .gauge()
        .desc("Generator voltage per phase")
        .build()
    ),
    "ac/generator/daily_energy": (
        Metric.builder()
        .name("deye_ac_generator_daily_energy")
        .gauge()
        .desc("Daily energy provided by generator")
        .build()
    ),
    "ac/generator/total_energy": (
        Metric.builder()
        .name("deye_ac_generator_total_energy")
        .counter()
        .desc("Total lifetime energy provided by generator")
        .build()
    ),
}
