import sys
import datetime
import time
import traceback
import socket
from listener import GT7Communication
import os
from threading import Lock

class TelemetryDisplay:
    def __init__(self, playstation_ip):
        self.gt7_comm = GT7Communication(playstation_ip)
        self.lock = Lock()
        self.last_connection_state = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def move_cursor(self, row, column):
        print(f"\033[{row};{column}H", end='')

    def print_static_display(self):
        self.clear_screen()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                    GT7 Telemetry Monitor                     ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print("║ Time (UTC):                                                  ║")
        print("║ User:                                                        ║")
        print("║ Connection:                                                  ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print("║ RACE INFORMATION                                            ║")
        print("║ Lap:                                                        ║")
        print("║ Position:                                                   ║")
        print("║ Best Lap:                                                  ║")
        print("║ Last Lap:                                                  ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print("║ CAR TELEMETRY                                              ║")
        print("║ Speed:                                                     ║")
        print("║ RPM:                                                       ║")
        print("║ Gear:                                                      ║")
        print("║ Throttle:                                                  ║")
        print("║ Brake:                                                     ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print("║ FUEL AND TEMPS                                             ║")
        print("║ Fuel:                                                      ║")
        print("║ Oil Temp:                                                  ║")
        print("║ Water Temp:                                                ║")
        print("╚══════════════════════════════════════════════════════════════╝")

    def update_value(self, row, value, prefix="", suffix="", max_length=50):
        with self.lock:
            self.move_cursor(row, len(prefix) + 3)  # +3 for the box drawing
            formatted_value = f"{value}{suffix}"
            # Pad with spaces to clear the line
            formatted_value = f"{formatted_value:<{max_length}}"
            print(formatted_value, end='', flush=True)

    def handle_connection(self):
        try:
            if not self.gt7_comm.is_connected():
                if self.last_connection_state:  # Was connected before
                    self.reconnect_attempts += 1
                    if self.reconnect_attempts <= self.max_reconnect_attempts:
                        print(f"Connection lost. Attempting to reconnect ({self.reconnect_attempts}/{self.max_reconnect_attempts})...")
                        self.gt7_comm.restart()
                    else:
                        print("Max reconnection attempts reached. Please restart the application.")
                        return False
                self.last_connection_state = False
            else:
                self.last_connection_state = True
                self.reconnect_attempts = 0
            return True
        except Exception as e:
            print(f"Connection error: {str(e)}")
            return False

    def run(self):
        try:
            self.gt7_comm.start()
            self.print_static_display()
            
            while True:
                if not self.handle_connection():
                    break

                # Update time and user (rows 4 and 5)
                current_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                self.update_value(4, current_time, "Time (UTC):", "")
                self.update_value(5, "LeSamourai23", "User:", "")
                
                # Update connection status (row 6)
                conn_status = "Connected" if self.gt7_comm.is_connected() else "Disconnected"
                status_color = "\033[32m" if self.gt7_comm.is_connected() else "\033[31m"  # Green/Red
                self.update_value(6, f"{status_color}{conn_status}\033[0m", "Connection:", "")

                data = self.gt7_comm.get_last_data()
                if data and hasattr(data, 'package_id'):
                    # Race Information 
                    if hasattr(data, 'current_lap'):
                        self.update_value(9, f"{data.current_lap}/{data.total_laps}", "Lap:", "")
                        self.update_value(10, f"{data.current_position}/{data.total_positions}", "Position:", "")
                        self.update_value(11, f"{data.best_lap/1000:.3f}", "Best Lap:", " s")
                        self.update_value(12, f"{data.last_lap/1000:.3f}", "Last Lap:", " s")

                        # Car Telemetry 
                        self.update_value(15, f"{data.car_speed:.1f}", "Speed:", " km/h")
                        self.update_value(16, f"{data.rpm:.0f}", "RPM:", "")
                        self.update_value(17, f"{data.current_gear}", "Gear:", "")
                        self.update_value(18, f"{data.throttle:.1f}", "Throttle:", " %")
                        self.update_value(19, f"{data.brake:.1f}", "Brake:", " %")

                        # Fuel and Temps 
                        self.update_value(22, f"{data.current_fuel:.1f}/{data.fuel_capacity:.1f}", "Fuel:", " L")
                        self.update_value(23, f"{data.oil_temp:.1f}", "Oil Temp:", " °C")
                        self.update_value(24, f"{data.water_temp:.1f}", "Water Temp:", " °C")

                time.sleep(0.016)  # ~ 60Hz refresh rate

        except KeyboardInterrupt:
            print("\nShutting down GT7 Telemetry Monitor...")
            self.gt7_comm.stop()
            sys.exit(0)
        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            print(traceback.format_exc())
            self.gt7_comm.stop()
            sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python listener.py <playstation-ip>")
        print("Example: python listener.py 192.168.xx.xx")
        sys.exit(1)

    playstation_ip = sys.argv[1]
    display = TelemetryDisplay(playstation_ip)
    display.run()

if __name__ == "__main__":
    main()