BRICK = "https://brickschema.org/schema/Brick#"


def cls(name: str) -> str:
    return f"{BRICK}{name}"


TESTS = [
    {"name": "AHU01 in bldg1", "query": "air handler unit AHU01 in bldg1", "constraint_any": [cls("Air_Handler_Unit")]},
    {"name": "AHU04N in bldg5", "query": "air handler unit AHU04N in bldg5", "constraint_any": [cls("Air_Handler_Unit")]},
    {"name": "AHU03 in bldg11", "query": "air handler unit AHU03 in bldg11", "constraint_any": [cls("Air_Handler_Unit")]},
    {"name": "Chiller serving AHUs", "query": "chiller serving ahus", "constraint_any": [cls("Chiller")]},
    {"name": "Reheat coil in smc", "query": "reheat coil in smc", "constraint_any": [cls("Reheat_Coil")]},
    {"name": "Discharge temp sensor in smc", "query": "discharge air temperature sensor in smc", "constraint_any": [cls("Discharge_Air_Temperature_Sensor")]},
    {"name": "Reheat coil on VAV in smc", "query": "reheat coil on vav in smc", "constraint_any": [cls("Reheat_Coil")]},
    {"name": "Air moving component on VAVRM107A in bldg1", "query": "air moving component on VAVRM107A in bldg1", "constraint_any": [cls("Damper")]},
    {"name": "Device serving RM107A in bldg1", "query": "device serving RM107A in bldg1", "constraint_any": [cls("VAV"), cls("RVAV")]},
    {"name": "Device serving RM2435 in bldg5", "query": "device serving RM2435 in bldg5", "constraint_any": [cls("VAV"), cls("RVAV")]},

    {"name": "Supply air temperature reading AHU01 bldg1", "query": "temperature reading for supply air on AHU01 in bldg1", "constraint_any": [cls("Supply_Air_Temperature_Sensor")]},
    {"name": "Outside condition reading AHU01 bldg1", "query": "outside condition reading on AHU01 in bldg1", "constraint_any": [cls("Outside_Air_Temperature_Sensor")]},
    {"name": "Return air condition reading AHU01 bldg1", "query": "return air condition reading on AHU01 in bldg1", "constraint_any": [cls("Return_Air_Temperature_Sensor")]},
    {"name": "Mixed air condition reading AHU01 bldg1", "query": "mixed air condition reading on AHU01 in bldg1", "constraint_any": [cls("Mixed_Air_Temperature_Sensor")]},
    {"name": "Supply air pressure on AHU02 bldg1", "query": "supply air static pressure sensor on AHU02 in bldg1", "constraint_any": [cls("Supply_Air_Static_Pressure_Sensor")]},
    {"name": "Temperature reading for RM107A bldg1", "query": "temperature reading for RM107A in bldg1", "constraint_any": [cls("Zone_Air_Temperature_Sensor")]},
    {"name": "Zone air temp RM107B bldg1", "query": "zone air temperature sensor for RM107B in bldg1", "constraint_any": [cls("Zone_Air_Temperature_Sensor")]},
    {"name": "Temperature reading for RM2435 bldg5", "query": "temperature reading for RM2435 in bldg5", "constraint_any": [cls("Zone_Air_Temperature_Sensor")]},
    {"name": "Temperature reading for RM2212A bldg11", "query": "temperature reading for RM2212A in bldg11", "constraint_any": [cls("Zone_Air_Temperature_Sensor")]},
    {"name": "Actual airflow for 1-1-7 smc", "query": "actual airflow for 1-1-7 in smc", "constraint_any": [cls("Supply_Air_Flow_Sensor")]},
    {"name": "Discharge temperature reading 1-1-7 smc", "query": "discharge temperature reading for 1-1-7 in smc", "constraint_any": [cls("Discharge_Air_Temperature_Sensor")]},
    {"name": "Chilled water supply temp bldg1", "query": "building chilled water supply temperature sensor in bldg1", "constraint_any": [cls("Chilled_Water_Supply_Temperature_Sensor")]},
    {"name": "Chilled water return temp bldg1", "query": "building chilled water return temperature sensor in bldg1", "constraint_any": [cls("Chilled_Water_Return_Temperature_Sensor")]},
    {"name": "Occupancy sensor in corpus", "query": "occupancy sensor in building hvac model", "constraint_any": [cls("Occupancy_Sensor")]},

    {"name": "Supply air temperature target AHU01 bldg1", "query": "temperature target for supply air on AHU01 in bldg1", "constraint_any": [cls("Supply_Air_Temperature_Setpoint")]},
    {"name": "Supply air temp setpoint AHU04N bldg5", "query": "supply air temperature setpoint on AHU04N in bldg5", "constraint_any": [cls("Supply_Air_Temperature_Setpoint")]},
    {"name": "Temperature target for RM107A bldg1", "query": "temperature target for RM107A in bldg1", "constraint_any": [cls("Zone_Air_Temperature_Setpoint")]},
    {"name": "Zone air temp setpoint RM2435 bldg5", "query": "zone air temperature setpoint for RM2435 in bldg5", "constraint_any": [cls("Zone_Air_Temperature_Setpoint")]},
    {"name": "Occupied cooling setpoint bldg37", "query": "occupied cooling temperature setpoint in bldg37 lab zone", "constraint_any": [cls("Occupied_Cooling_Temperature_Setpoint")]},
    {"name": "Occupied heating setpoint bldg37", "query": "occupied heating temperature setpoint in bldg37 lab zone", "constraint_any": [cls("Occupied_Heating_Temperature_Setpoint")]},
    {"name": "Unoccupied cooling setpoint bldg37", "query": "unoccupied cooling temperature setpoint in bldg37 lab zone", "constraint_any": [cls("Unoccupied_Air_Temperature_Cooling_Setpoint")]},
    {"name": "Unoccupied heating setpoint bldg37", "query": "unoccupied heating temperature setpoint in bldg37 lab zone", "constraint_any": [cls("Unoccupied_Air_Temperature_Heating_Setpoint")]},
    {"name": "Air flow setpoint 1-1-7 smc", "query": "air flow setpoint 1-1-7 in smc", "constraint_any": [cls("Air_Flow_Setpoint"), cls("Supply_Air_Flow_Setpoint")]},
    {"name": "Heating command 1-1-7 smc", "query": "heating command 1-1-7 in smc", "constraint_any": [cls("Heating_Command")]},
    {"name": "Cooling control point AHU01 bldg1", "query": "point that controls cooling on AHU01 in bldg1", "constraint_any": [cls("Cooling_Command"), cls("Valve_Command")]},
    {"name": "Chilled water pump control in bldg1", "query": "control point for the chilled water pump in bldg1", "constraint_any": [cls("Start_Stop_Command")]},

    {"name": "Floor1 in bldg1", "query": "floor1 in bldg1", "constraint_any": [cls("Floor")]},
    {"name": "Rooms on floor1 in bldg1", "query": "room on floor1 in bldg1", "constraint_any": [cls("Room")]},
    {"name": "HVAC zone RM107A in bldg1", "query": "hvac zone RM107A in bldg1", "constraint_any": [cls("HVAC_Zone")]},
    {"name": "HVAC zone RM2435 in bldg5", "query": "hvac zone RM2435 in bldg5", "constraint_any": [cls("HVAC_Zone")]},
    {"name": "HVAC zone RM2212A in bldg11", "query": "hvac zone RM2212A in bldg11", "constraint_any": [cls("HVAC_Zone")]},
    {"name": "Room RM2212A in bldg11", "query": "room RM2212A in bldg11", "constraint_any": [cls("Room")]},

    {"name": "Supply-side temperature on AHU01 ambiguous", "query": "supply side temperature point on AHU01 in bldg1", "constraint_any": [cls("Supply_Air_Temperature_Sensor")]},
    {"name": "Supply-side temperature target AHU01 ambiguous", "query": "supply side temperature target on AHU01 in bldg1", "constraint_any": [cls("Supply_Air_Temperature_Setpoint")]},
    {"name": "Actual flow on 1-1-7 ambiguous", "query": "actual flow for 1-1-7 in smc", "constraint_any": [cls("Supply_Air_Flow_Sensor")]},
    {"name": "Target flow on 1-1-7 ambiguous", "query": "target flow for 1-1-7 in smc", "constraint_any": [cls("Air_Flow_Setpoint"), cls("Supply_Air_Flow_Setpoint")]},
    {"name": "Damper control point RM107A ambiguous", "query": "damper control point for RM107A in bldg1", "constraint_any": [cls("Damper_Position_Setpoint"), cls("Damper_Position_Command")]},
    {"name": "Valve-related control on AHU01 ambiguous", "query": "valve related control point on AHU01 in bldg1", "constraint_any": [cls("Valve_Command"), cls("Cooling_Command")]},
    {"name": "Room mode-related point RM107A ambiguous", "query": "mode related point for RM107A in bldg1", "constraint_any": [cls("Heating_Command"), cls("Mode")]},
    {"name": "Zone temp control RM107A ambiguous", "query": "zone air control temperature for RM107A in bldg1", "constraint_any": [cls("Zone_Air_Temperature_Setpoint")]},
]




