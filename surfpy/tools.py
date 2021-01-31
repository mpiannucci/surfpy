import math
import json
import datetime
import bisect
import time
try:
    import requests
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry
except:
    pass


def scalar_from_uv(ucomponent, vcomponent):
    # Calculates the scalar magnitude and heading angle from uv vector components
    angle = (270.0 - (math.atan2(vcomponent, ucomponent) * (180.0 / math.pi))) % 360
    speed = math.sqrt(math.pow(abs(vcomponent), 2) + math.pow(abs(ucomponent), 2))
    return speed, angle


def ldis(period, depth):
    # Computes the wavelength for a wave with the given period
    # and depth. Units are metric, gravity is 9.81.
    gravity = 9.81
    eps = 0.000001
    max_iteration = 50
    iteration = 0
    err = float(1.0)

    OMEGA = float(2 * math.pi / period)
    D = float(math.pow(OMEGA, 2) * depth / gravity)

    Xo = 0.0
    Xf = 0.0
    F = 0.0
    DF = 0.0

    # Make an initial guess for non dimentional solutions
    if D >= 1:
        Xo = D
    else:
        Xo = math.sqrt(D)

    # Solve using Newton Raphson Iteration
    while (err > eps) and (iteration < max_iteration):
        F = Xo - (D / math.tanh(Xo))
        DF = 1 + (D / math.pow(math.sinh(Xo), 2))
        Xf = Xo - (F / DF)
        err = abs((Xf - Xo) / Xo)
        Xo = Xf
        iteration += 1

    # Check for convergence failure
    if iteration >= max_iteration:
        return -1.0

    return 2 * math.pi * depth / Xf


def breaking_characteristics(period, incident_angle, deep_wave_height, beach_slope, water_depth):
    # Solves for the Breaking Wave Height and Breaking Water Depth given a swell and beach conditions.
    # All units are metric and gravity is 9.81.
    gravity = 9.81
    incident_angle_rad = math.radians(incident_angle)

    # Find all of the wave characteristics
    wavelength = ldis(period, water_depth)

    deep_wavelength = (gravity * math.pow(period, 2)) / (2 * math.pi)
    initial_celerity = (gravity * period) / (2 * math.pi)
    celerity = wavelength / period
    theta = math.asin(celerity * ((math.sin(incident_angle_rad)) / initial_celerity))
    refraction_coeff = math.sqrt(math.cos(incident_angle_rad) / math.cos(theta))
    a = 43.8 * (1 - math.exp(-19*beach_slope))
    b = 1.56 / (1 + math.exp(-19.5*beach_slope))
    deep_refracted_wave_height = refraction_coeff * deep_wave_height
    w = 0.56 * math.pow(deep_refracted_wave_height/deep_wavelength, -0.2)

    # Find the breaking wave height!
    breaking_wave_height = w * deep_refracted_wave_height

    # Solve for the breaking depth
    K = b - a*(breaking_wave_height/(gravity*math.pow(period, 2)))
    breaking_water_depth = breaking_wave_height / K

    return breaking_wave_height, breaking_water_depth


def refraction_coefficient(wavelength, depth, incident_angle):
    # Calculate the refraction coefficient Kr with given
    # inputs on a straight beach with parrellel bottom contours
    incident_angle_rad = math.radians(incident_angle)
    wavenumber = (2.0 * math.pi) / wavelength
    shallow_incident_angle_rad = math.asin(math.sin(incident_angle_rad) * math.tanh(wavenumber*depth))
    refraction_coeff = math.sqrt(math.cos(incident_angle_rad) / math.cos(shallow_incident_angle_rad))
    shallow_incident_angle = shallow_incident_angle_rad * 180 / math.pi
    return refraction_coeff, shallow_incident_angle


def shoaling_coefficient(wavelength, depth):
    # Calculate the shoaling coeffecient Ks. Units are metric, gravity is 9.81
    gravity = 9.81

    # Basic dispersion relationships
    wavenumber = (2.0 * math.pi) / wavelength
    deep_wavelength = wavelength / math.tanh(wavenumber*depth)
    w = math.sqrt(wavenumber * gravity)
    period = (2.0 * math.pi) / w

    # Celerity
    initial_celerity = deep_wavelength / period
    celerity = initial_celerity * math.tanh(wavenumber*depth)
    group_velocity = 0.5 * celerity * (1 + ((2 * wavenumber * depth) / (math.sinh(2 * wavenumber * depth))))

    return math.sqrt(initial_celerity / (2 * group_velocity))


def zero_spectral_moment(energy, bandwidth):
    # Calculates the zero moment of a wave spectra point given energy and bandwidth
    return energy * bandwidth


def second_spectral_moment(energy, bandwidth, frequency):
    # Calculates the second moment of a wave spectra point given enrgy, frequency and bandwith
    return energy * bandwidth * math.pow(frequency, 2)


def steepness_coeff_with_moments(zero_moment, second_moment):
    return (8.0 * math.pi * second_moment) / (9.81 * math.sqrt(zero_moment))


def steepness(significant_wave_height, dominant_period):
    val = math.exp(-3.3 * math.log(dominant_period))
    if significant_wave_height > (val / 250.0):
        return 'Very Steep'
    elif significant_wave_height > (val / 500.0):
        return 'Steep'
    elif significant_wave_height > (val / 1000.0):
        return 'Average'
    else:
        return 'Swell'


def peakdetect(v, delta, x = None):
    """
    Converted from MATLAB script at http://billauer.co.il/peakdet.html
    
    Returns two arrays
    
    function [maxtab, mintab]=peakdet(v, delta, x)
    %PEAKDET Detect peaks in a vector
    %        [MAXTAB, MINTAB] = PEAKDET(V, DELTA) finds the local
    %        maxima and minima ("peaks") in the vector V.
    %        MAXTAB and MINTAB consists of two columns. Column 1
    %        contains indices in V, and column 2 the found values.
    %      
    %        With [MAXTAB, MINTAB] = PEAKDET(V, DELTA, X) the indices
    %        in MAXTAB and MINTAB are replaced with the corresponding
    %        X-values.
    %
    %        A point is considered a maximum peak if it has the maximal
    %        value, and was preceded (to the left) by a value lower by
    %        DELTA.
    
    % Eli Billauer, 3.4.05 (Explicitly not copyrighted).
    % This function is released to the public domain; Any use is allowed.
    
    """
    min_indexes = []
    min_values = []
    max_indexes = []
    max_values = []
       
    if x is None:
        x = range(len(v))
    
    mn, mx = float('inf'), -float('inf')
    mnpos, mxpos = float('nan'), float('nan')
    
    lookformax = True
    
    for i in range(len(v)):
        this = v[i]
        if this > mx:
            mx = this
            mxpos = x[i]
        if this < mn:
            mn = this
            mnpos = x[i]
        
        if lookformax:
            if this < mx-delta:
                max_indexes.append(mxpos)
                max_values.append(mx)
                mn = this
                mnpos = x[i]
                lookformax = False
        else:
            if this > mn+delta:
                min_indexes.append(mnpos)
                min_values.append(mn)
                mx = this
                mxpos = x[i]
                lookformax = True

    return min_indexes, min_values, max_indexes, max_values


def parse_float(raw_value):
    value = float('nan')
    try:
        value = float(raw_value)
    except:
        pass
    return value


def parse_int(raw_value):
    value = int('nan')
    try:
        value = int(raw_value)
    except:
        pass
    return value


def simple_serialize(obj):
    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial

    return obj.__dict__


def dump_json(obj):
    return json.dumps(obj, default=simple_serialize).replace('NaN', 'null')


def download_data(url):
    if not len(url):
        return None
    try:
        response = requests.get(url)
    except:
        print('Failed to download ' + url)
        return False
    if not len(response.content):
        return False
    return response.content


def retry_session(retries=1):
    session = requests.Session()
    retries = Retry(total=retries,
                backoff_factor=0.1,
                status_forcelist=[500, 502, 503, 504],
                method_whitelist=frozenset(['GET', 'POST']))

    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.mount('http://', HTTPAdapter(max_retries=retries))
    return session


def download_with_retry(url):
    if not len(url):
        return None

    try:
        session = retry_session(retries=2)
        response = session.get(url, timeout=5)
    except Exception as e:
        print('Failed to download ' + url + ': ' + str(e))
        return None
    if not len(response.content):
        return None
    return response.content


def closest_index(in_list, val):
    pos = bisect.bisect_left(in_list, val)
    if pos == 0:
        return 0
    if pos == len(in_list):
        return -1
    return pos-1
