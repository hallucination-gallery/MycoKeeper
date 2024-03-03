import adafruit_ahtx0
import board
import time
import curses


# Setup I2C Sensor
sensor = adafruit_ahtx0.AHTx0(board.I2C())


# Returns the temperature in celsius
def get_temperature():
    return round(sensor.temperature, 1)


# Returns the humidity in percentage
def get_humidity():
    return round(sensor.relative_humidity, 1)


# Poll the fan controller. If the fans are off, turn them on
# 🍃
def turn_on_fans():
    pass
    #click.echo("Turning on the fans")


# Poll the fan controller. If the fans are on, turn them off
def turn_off_fans():
    pass
    #click.echo("Turning off the fans")


# Poll the humidifier controller. If the humidifier is off, turn it on
# 🌧️
def turn_on_humidifier():
    pass
    #click.echo("Turning on the humidifier")


# Poll the humidifier controller. If the humidifier is on, turn it off
def turn_off_humidifier():
    pass
    #click.echo("Turning off the humidifier")


# Poll the heater controller. If the heater is off, turn it on
# 🔥
def turn_on_heater():
    pass
    #click.echo("Turning on the heater")


# Poll the heater controller. If the heater is on, turn it off
def turn_off_heater():
    pass
    #click.echo("Turning off the heater")


class Stats:
    def __init__(self, temperature, humidity, temperature_status, humidity_status, min_temp, max_temp, min_humidity, max_humidity):
        self.temperature = temperature
        self.humidity = humidity
        self.temperature_status = temperature_status
        self.humidity_status = humidity_status
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.min_humidity = min_humidity
        self.max_humidity = max_humidity
        self.fans_on = False
        self.heater_on = False
        self.humidifier_on = False


    # Adjust min_temp by +/- 1
    def adjust_min_temp(self, value):
        self.min_temp += value


    # Adjust max_temp by +/- 1
    def adjust_max_temp(self, value):
        self.max_temp += value


    # Adjust min_humidity by +/- 1
    def adjust_min_humidity(self, value):
        self.min_humidity += value


    # Adjust max_humidity by +/- 1
    def adjust_max_humidity(self, value):
        self.max_humidity += value

    
# Display the console
def display_console(win, stats: Stats):
    win.clear()

    win.addstr(1, 0, "       ~ MycoKeeper ~       ")
    win.addstr(2, 0, "____________________________")
    win.addstr(4, 0, f"Temperature Range: {stats.min_temp}c - {stats.max_temp}c")
    win.addstr(5, 0, f"Humidity Range: {stats.min_humidity}% - {stats.max_humidity}%")
    win.addstr(6, 0, f"Temperature: {stats.temperature}c ({stats.temperature_status})")
    win.addstr(7, 0, f"Humidity: {stats.humidity}% ({stats.humidity_status})")
    
    s = []
    if stats.fans_on:
        s.append("🍃 ")
    if stats.heater_on:
        s.append("🔥 ")
    if stats.humidifier_on:
        s.append("🌧️ ")
    if not stats.fans_on and not stats.heater_on and not stats.humidifier_on:
        if stats.temperature_status == "optimal":
            s.append("🌈 ")
        if stats.humidity_status == "optimal":
            s.append("✨")
        s.append("🍄 ")

    centered_text_pos = (28 - len(s)) // 2 #hard coding 28 here because of the width of the other text. Replace this when you've got the li'l scren going
    win.addstr(9, centered_text_pos, "".join(s))
    
    win.noutrefresh()

    curses.doupdate()


# Terminate the curses window
def terminate(screen):
    curses.nocbreak()
    screen.keypad(False)
    curses.echo()
    curses.endwin()


# Main function
def MycoKeeper(screen):
    try:
        # Initialize the curses window
        curses.noecho()
        screen.keypad(True)
        curses.curs_set(0)

        # Create a buffer window outside of the display_console function to reduce flickering
        bufferscreen = curses.newwin(curses.LINES, curses.COLS)

        # Establish the start time, to be used for delta time calculations
        start_time = time.time()
        last_time = start_time
            
        # Define the temperature and humidity ranges
        stats = Stats(0, 0, "normal", "normal", 20, 26, 80, 95)
        optimal_temp = stats.min_temp + stats.max_temp / 2
        optimal_humidity = stats.min_humidity + stats.max_humidity / 2

        # Flags that enable or disable the fans, heater and humidifier
        # this ALLOWS them to be turned on, but does not turn them on
        heater_enabled = True
        humidifier_enabled = True
        fans_enabled = True

        # Define the refresh rate in seconds
        refresh_rate = 2
        refresh_time = 0

        # FAE (Fresh Air Exchange) rate and run time in seconds
        fae_rate = 1800  #30 minutes
        fae_time = fae_rate
        fae_run_time = 0 # set to 5 minutes (in seconds) when the FAE starts

        # main loop. Continuously poll the temperature and humidity
        # set temperature status and humidity status
        # turn on the fans and disable heater if the temperature is too high
        # enable heater if temperature is too low
        # turn on the humidifier and reduce the max fan speed if the humidity is too low
        while True:
            # Calculate the delta time
            # This is used to calculate the time since the last loop
            delta_time = time.time() - last_time
            last_time = time.time()

            # Poll the temperature and humidity sensors
            stats.temperature = get_temperature()
            stats.humidity = get_humidity()

            # Set the temperature and humidity status
            # enable or disable the fans, heater and humidifier 
            if stats.temperature > stats.max_temp:
                if stats.temperature_status != "high":
                    stats.temperature_status = "high"
                    fans_enabled = True
                    heater_enabled = False
            elif stats.temperature < stats.min_temp:
                if stats.temperature_status != "low":
                    stats.temperature_status = "low"
                    fans_enabled = False
                    heater_enabled = True
            else:
                if stats.temperature > optimal_temp - 2 and stats.temperature < optimal_temp + 2:
                    stats.temperature_status = "optimal"
                else:
                    stats.temperature_status = "normal"
                    fans_enabled = True
                    heater_enabled = False

            if stats.humidity > stats.max_humidity:
                if stats.humidity_status != "high":
                    stats.humidity_status = "high"
                    humidifier_enabled = False
                    fans_enabled = True
            elif stats.humidity < stats.min_humidity:
                if stats.humidity_status != "low":
                    stats.humidity_status = "low"
                    humidifier_enabled = True
                    fans_enabled = False
            else:
                if stats.humidity > optimal_humidity - 2 and stats.humidity < optimal_humidity + 2:
                    stats.humidity_status = "optimal"
                    humidifier_enabled = False
                else:
                    stats.humidity_status = "normal"
                    humidifier_enabled = True
                    fans_enabled = True

            # Turn on the fans if the temperature or humidity is too high
            if fans_enabled and (stats.temperature_status == "high" or stats.humidity_status == "high"):
                if stats.fans_on == False:
                    stats.fans_on = True
                fae_time = fae_rate
            else:
                if stats.fans_on == True:
                    stats.fans_on = False

            # Turn on the heater if the temperature is too low
            if heater_enabled and stats.temperature_status == "low":
                if stats.heater_on == False:
                    stats.heater_on = True
            else:
                if stats.heater_on == True:
                    stats.heater_on = False

            # Turn on the humidifier if the humidity is too low
            if humidifier_enabled and stats.humidity_status == "low":
                if stats.humidifier_on == False:
                    stats.humidifier_on = True
            else:
                if stats.humidifier_on == True:
                    stats.humidifier_on = False

            # FAE (Fresh Air Exchange) rate and run time in seconds
            if fae_time <= 0:
                fae_run_time = 300
                fae_time = fae_rate
            else:
                fae_time -= 1
                fae_run_time -= 1

            # Turn off the humidifier and turn on the fans for 5 minutes
            if fae_run_time > 0:
                if stats.humidifier_on == True:
                    stats.humidifier_on = False
                if stats.fans_on == False:
                    stats.fans_on = True

            if stats.fans_on == True:
                turn_on_fans()
            else:
                turn_off_fans()

            if stats.heater_on == True:
                turn_on_heater()
            else:
                turn_off_heater()

            if stats.humidifier_on == True:
                turn_on_humidifier()
            else:
                turn_off_humidifier()

            # Print the status of the sensors and the active devices
            if refresh_time <= 0:
                display_console(bufferscreen, stats)
                refresh_time = refresh_rate
            else:
                refresh_time -= 1 * delta_time
    except KeyboardInterrupt:
        terminate(screen)
    finally:
        terminate(screen)
      

if __name__ == "__main__":
    curses.wrapper(MycoKeeper)

