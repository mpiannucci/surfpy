import math

def scalar_from_uv(ucomponent, vcomponent):
    # Computes speed and heading given the u and vvector components
    heading = math.modf((270.0 - (math.atan2(vcomponent, ucomponent) * (180 / math.pi))), 360)
    speed = math.sqrt(math.pow(abs(vcomponent), 2) + math.pow(abs(ucomponent), 2))
    return speed, heading

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

    return 2 * math.Pi * depth / Xf

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
    group_velocity = 0.5 * celerity * (1 + ((2 * wavenumber * depth) / (math.Sinh(2 * wavenumber * depth))))

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

def peakdetect(y_axis, x_axis = None, lookahead = 200, delta=0):
    """
    Converted from/based on a MATLAB script at: 
    http://billauer.co.il/peakdet.html
    
    function for detecting local maxima and minima in a signal.
    Discovers peaks by searching for values which are surrounded by lower
    or larger values for maxima and minima respectively
    
    keyword arguments:
    y_axis -- A list containing the signal over which to find peaks
    
    x_axis -- A x-axis whose values correspond to the y_axis list and is used
        in the return to specify the position of the peaks. If omitted an
        index of the y_axis is used.
        (default: None)
    
    lookahead -- distance to look ahead from a peak candidate to determine if
        it is the actual peak
        (default: 200) 
        '(samples / period) / f' where '4 >= f >= 1.25' might be a good value
    
    delta -- this specifies a minimum difference between a peak and
        the following points, before a peak may be considered a peak. Useful
        to hinder the function from picking up false peaks towards to end of
        the signal. To work well delta should be set to delta >= RMSnoise * 5.
        (default: 0)
            When omitted delta function causes a 20% decrease in speed.
            When used Correctly it can double the speed of the function
    
    
    return: two lists [max_peaks, min_peaks] containing the positive and
        negative peaks respectively. Each cell of the lists contains a tuple
        of: (position, peak_value) 
        to get the average peak value do: np.mean(max_peaks, 0)[1] on the
        results to unpack one of the lists into x, y coordinates do: 
        x, y = zip(*max_peaks)
    """
    max_peaks = []
    min_peaks = []

    # Used to pop the first hit which almost always is false
    dump = [] 
       
    # check input data
    # x_axis, y_axis = _datacheck_peakdetect(x_axis, y_axis)
    # store data length for later use
    length = len(y_axis)
    
    # perform some checks
    if lookahead < 1:
        raise ValueError("Lookahead must be '1' or above in value")
    # if not (np.isscalar(delta) and delta >= 0):
    #     raise ValueError("delta must be a positive number")
    
    # maxima and minima candidates are temporarily stored in
    # mx and mn respectively
    mn, mx = float('inf'), -float('inf')
    
    # Only detect peak if there is 'lookahead' amount of points after it
    for index, (x, y) in enumerate(zip(x_axis[:-lookahead], 
                                        y_axis[:-lookahead])):
        if y > mx:
            mx = y
            mxpos = x
        if y < mn:
            mn = y
            mnpos = x
        
        # look for max
        if y < mx-delta and mx != float('inf'):
            # Maxima peak candidate found
            # look ahead in signal to ensure that this is a peak and not jitter
            if y_axis[index:index+lookahead].max() < mx:
                max_peaks.append([mxpos, mx])
                dump.append(True)
                # set algorithm to only find minima now
                mx = float('inf')
                mn = float('inf')
                if index+lookahead >= length:
                    # end is within lookahead no more peaks can be found
                    break
                continue
            # else:  #slows shit down this does
            #    mx = ahead
            #    mxpos = x_axis[np.where(y_axis[index:index+lookahead]==mx)]
        
        # look for min####
        if y > mn+delta and mn != -float('inf'):
            # Minima peak candidate found 
            # look ahead in signal to ensure that this is a peak and not jitter
            if y_axis[index:index+lookahead].min() > mn:
                min_peaks.append([mnpos, mn])
                dump.append(False)
                # set algorithm to only find maxima now
                mn = -float('inf')
                mx = -float('inf')
                if index+lookahead >= length:
                    # end is within lookahead no more peaks can be found
                    break
    
    
    # Remove the false hit on the first value of the y_axis
    try:
        if dump[0]:
            max_peaks.pop(0)
        else:
            min_peaks.pop(0)
        del dump
    except IndexError:
        # no peaks were found, should the function return empty lists?
        pass
        
    return [max_peaks, min_peaks]

def parse_float(raw_value):
    value = float('nan')
    try:
        value = float(raw_value)
    except:
        pass
    return value
