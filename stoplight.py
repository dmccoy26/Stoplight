import os
import random
import time
from collections import deque

class Stoplight:
    def __init__(self, green_duration_ns, yellow_duration_ns, red_duration_ns):
        self.ns_state = "Green"  # North-South initially green
        self.ew_state = "Red"    # East-West initially red
        self.durations = {
            "NS": {"Green": green_duration_ns, "Yellow": yellow_duration_ns, "Red": red_duration_ns},
            "EW": {"Green": red_duration_ns, "Yellow": yellow_duration_ns, "Red": green_duration_ns + yellow_duration_ns}  # Adjusted to reflect NS durations
        }
        self.change_time_ns = time.time() + self.durations["NS"]["Green"]
        self.change_time_ew = float('inf')  # Initially, no change scheduled for East-West
        self.queues = {direction: deque() for direction in ["North", "South", "East", "West"]}
        self.red_light_violations = 0
        self.fine_per_car = 286
        self.red_light_violation_percentage = 0.1
        self.total_fines_collected = 0
        self.total_cars_passed = {"North": 0, "South": 0, "East": 0, "West": 0}
        self.cycle_count = {"North": 0, "South": 0, "East": 0, "West": 0}
        self.green_duration_ns = green_duration_ns  # Duration of green light for North/South
        self.yellow_duration_ns = yellow_duration_ns  # Duration of yellow light for North/South
        self.red_duration_ns = red_duration_ns   # Duration of red light for North/South
        self.green_duration_ew = green_duration_ns  # Duration of green light for East/West
        self.yellow_duration_ew = yellow_duration_ns  # Duration of yellow light for East/West
        self.red_duration_ew = red_duration_ns   # Duration of red light for East/West

        self.change_time_ns = time.time() + self.green_duration_ns
        self.change_time_ew = time.time() + self.red_duration_ns  # Initially, East/West is red for the duration of NS green

    def update_state(self):
        current_time = time.time()

        # North/South light state change
        if current_time >= self.change_time_ns:
            if self.ns_state == "Green":
                self.ns_state = "Yellow"
                self.change_time_ns = current_time + self.yellow_duration_ns
            elif self.ns_state == "Yellow":
                self.ns_state = "Red"
                self.ew_state = "Green"  # Corrected to ensure EW turns green when NS turns red
                self.change_time_ew = current_time + self.green_duration_ew + self.yellow_duration_ew
            elif self.ns_state == "Red" and current_time >= self.change_time_ew + self.red_duration_ew:
                self.ns_state = "Green"
                self.ew_state = "Red"
                self.change_time_ns = current_time + self.green_duration_ns

        # East/West light state change
        if current_time >= self.change_time_ew:
            if self.ew_state == "Green":
                self.ew_state = "Yellow"
                self.change_time_ew = current_time + self.yellow_duration_ew
            elif self.ew_state == "Yellow":
                self.ew_state = "Red"
                self.ns_state = "Green"  # Corrected to ensure NS turns green when EW turns red
                self.change_time_ns = current_time + self.green_duration_ns + self.yellow_duration_ns

    def simulate_traffic(self, duration):
        start_time = time.time()
        end_time = start_time + duration
        cycle_count = 0
        total_violations = 0
        total_red_light_stopped_cars = 0

        while time.time() < end_time:
            self.update_state()
            elapsed_time = time.time() - start_time
            remaining_time = end_time - time.time()

            for direction in self.queues:
                state = self.ns_state if direction in ["North", "South"] else self.ew_state
                cars = random.randint(0, 2)

                if state == "Red":
                    self.queues[direction].append(cars)
                    total_red_light_stopped_cars += cars

                    # Check for red light violations every 20 cycles
                    if cycle_count % 20 == 0:
                        violations = round(total_red_light_stopped_cars * self.red_light_violation_percentage)
                        total_violations += violations
                        # Reset total red light stopped cars count
                        total_red_light_stopped_cars = 0

                else:
                    # For green and yellow lights
                    # Directly increment cars passed, reflecting cars passing through the light
                    self.total_cars_passed[direction] += cars

                    if self.queues[direction]:
                        # Dequeue without processing
                        self.queues[direction].popleft()

                    # Update cycle count when state changes to green or yellow
                    if state in ["Green", "Yellow"]:
                        cycle_count += 1

            # Update red light violation count
            self.red_light_violations = total_violations

            self.print_status(elapsed_time, remaining_time)
            time.sleep(1)

        # Update total fines collected based on red light violations
        self.total_fines_collected = self.red_light_violations * self.fine_per_car

    def print_status(self, elapsed_time, remaining_time):
        os.system('cls' if os.name == 'nt' else 'clear')
        elapsed_str = time.strftime("%M:%S", time.gmtime(elapsed_time))
        remaining_str = time.strftime("%M:%S", time.gmtime(remaining_time))
        print(f"Elapsed Time: {elapsed_str}, Remaining Time: {remaining_str}")
        ns_color = "\033[92mGreen\033[0m" if self.ns_state == "Green" else "\033[93mYellow\033[0m" if self.ns_state == "Yellow" else "\033[91mRed\033[0m"
        ew_color = "\033[92mGreen\033[0m" if self.ew_state == "Green" else "\033[93mYellow\033[0m" if self.ew_state == "Yellow" else "\033[91mRed\033[0m"
        print(f"North/South Current State: {ns_color}")
        print(f"East/West Current State: {ew_color}")
        for direction, queue in self.queues.items():
            print(f"{direction}bound Queue: {list(queue)}")
        self.display_live_report()


    def display_live_report(self):
        print("\nLive Simulation Report:")
        for direction in ["North", "South", "East", "West"]:
            total_passed = self.total_cars_passed[direction]
            cycle_count = self.cycle_count[direction]
            average_per_cycle = total_passed / cycle_count if cycle_count > 0 else 0
            queue = self.queues[direction]
            print(" ")
            print(f"Direction: {direction}")
            print(f"Total Cars Passed: {total_passed}")
            print(f"Average Cars Passed Per Cycle: {average_per_cycle:.2f}")
            #print(f"Maximum Cars Passed in a Cycle: {max(queue, default=0)}")
            #print(f"Minimum Cars Passed in a Cycle: {min(queue, default=0)}")
            #print(" ")

        #print(f"Red Light Violations: {self.red_light_violations}")
        #print(f"Stopped Cars at Red Light: {self.stopped_cars_at_red_light}")
        #print(f"Total Fines Collected: ${self.total_fines_collected}")

    def generate_summary_report(self):
        print("\nSimulation Summary Report:")
        print("=================================")
        print(f"Total Red Light Violations: {self.red_light_violations}")
        # Remove the line attempting to print stopped_cars_at_red_light
        print(f"Total Fines Collected: ${self.total_fines_collected}")

        print("\nTraffic Flow Summary:")
        print("=================================")
        for direction in ["North", "South", "East", "West"]:
            total_passed = self.total_cars_passed[direction]
            cycle_count = self.cycle_count[direction]
            average_per_cycle = total_passed / cycle_count if cycle_count > 0 else 0
            print(f"Direction: {direction}")
            print(f"Total Cars Passed: {total_passed}")
            print(f"Average Cars Passed Per Cycle: {average_per_cycle:.2f}")
            print(f"Total Cycles: {cycle_count}")

            # Calculate duration of each light color
            green_duration = self.durations["NS"]["Green"] if direction in ["North", "South"] else self.durations["EW"][
                "Green"]
            yellow_duration = self.durations["NS"]["Yellow"] if direction in ["North", "South"] else \
            self.durations["EW"]["Yellow"]
            red_duration = self.durations["NS"]["Red"] if direction in ["North", "South"] else self.durations["EW"][
                "Red"]

            print(f"Green Light Duration: {green_duration} seconds")
            print(f"Yellow Light Duration: {yellow_duration} seconds")
            print(f"Red Light Duration: {red_duration} seconds")
            print("---------------------------------")


def main():
    print("Please enter the durations for the North/South bound traffic lights in seconds:")
    print("Press Enter without typing to use default values (Green: 60s, Yellow: 15s, Red: 60s).")

    green_duration_ns = input("Green light duration (default 60): ")
    yellow_duration_ns = input("Yellow light duration (default 15): ")
    red_duration_ns = input("Red light duration (default 60): ")

    # Use default values if the user input is empty
    green_duration_ns = int(green_duration_ns) if green_duration_ns else 60
    yellow_duration_ns = int(yellow_duration_ns) if yellow_duration_ns else 15
    red_duration_ns = int(red_duration_ns) if red_duration_ns else 60

    # Calculate total duration of one complete cycle for North/South bound lights
    total_cycle_duration = green_duration_ns + yellow_duration_ns + red_duration_ns
    print(f"Total cycle duration for North/South bound lights: {total_cycle_duration} seconds.")

    print("\nNow, let's set up the simulation duration.")
    simulation_duration = int(input("Enter the number of seconds for the simulation to run (default 300): ") or 300)

    stoplight = Stoplight(green_duration_ns, yellow_duration_ns, red_duration_ns)  # Passing North/South light durations
    # Passing North/South light durations
    print("\nSimulation started. Press Ctrl+C to exit early.")
    try:
        stoplight.simulate_traffic(simulation_duration)
        stoplight.generate_summary_report()  # Generate summary report when the timer runs out
    except KeyboardInterrupt:
        print("\nSimulation interrupted.")


if __name__ == "__main__":
    main()
