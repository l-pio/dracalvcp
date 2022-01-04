# dracalVCP
An unofficial Python package to access the atmospheric sensors from Dracal Technologies via
virtual comport (VCP), to accurately monitor air temperature, pressure, humidity, and carbon dioxide (CO2)
concentration. 

## Installation
Please simply copy the package directory to your workspace, and install the requirements by running:
```
$ pip install -r requirements.txt
```

## Usage
```
with dracalvcp.Device('COMx') as device:  # Replace x by comport number
    pressure = device.get_press()  #  (Pa)
    temperature = device.get_temp()  # (K)
    humidity = device.get_hum()  # (%)
    co2_concentration = device.get_co2()  # (ppm)
```

Another example can be found [here](./example.py).