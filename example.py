import dracalvcp


if __name__ == '__main__':
    # Dracal PTH420 (enhanced precision USB atmospheric pressure, temperature, and humidity sensor)
    with dracalvcp.Device('COM4') as device:
        press = device.get_press()
        temp = device.get_temp()
        hum = device.get_hum()
        
        print('p=%d Pa, T=%.2f °C, C=%.2f %%' % (press, temp, hum))
    
    # Dracal DXC100 (carbon dioxide sensor)
    with dracalvcp.Device('COM5') as device:
        press = device.get_press()
        temp = device.get_temp()  # Seems to be very inaccurate (in-case temperature)
        co2 = device.get_co2()
        
        print('p=%d Pa, T=%.2f °C, C=%.2f ppm' % (press, temp, co2))
