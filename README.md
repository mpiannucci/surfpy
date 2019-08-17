# surfpy

Wave and weather tools written in pure python

## Installing dependencies

First, this project makes heavy use of [`grippy`](https://github.com/mpiannucci/grippy), a pure python `grib2` library written by myself. This library allows for reading `grib2` files without needing to install `c` for `fortran` libraries. I have not worked out deployment perfectly yet, so for now the library should be cloned and then added to your `pythonpath`. I typically clone it into the same parent directory as I am cloning `surfpy` into, but anywhere `pythonpath` can find it is sufficient.

Finally, assuming `grippy` has been cloned and is available in your `pythonpath`, adding the following requirements.txt should be sufficient:
```
requests
numpy
matplotlib
```

## Running the Tests

Because of the crappy python 2/3 compatability fo packages, to run this test you must do so at the package level. So to run tests you can use below:

```bash
python -m surfpy.test_forecast
python -m surfpy.test_buoy
python -m surfpy.test_sun
python -m surfpy.test_tides
```

## License

This project is [`MIT` Licensed](LICENSE.txt). Please see [`LICENSE.txt`](LICENSE.txt) for more info. 
