import math


def cosd(x):
    return math.cos(math.radians(x))

def sind(x):
    return math.sin(math.radians(x))

def tand(x):
    return math.tan(math.radians(x))

def acosd(x):
    return math.degrees(math.acos(x))

def asin(x):
    return math.degrees(math.asin(x))

def atand(x):
    return math.degrees(math.atan(x))

def atan2d(y,x):
    return math.degrees(math.atan2(y,x))

def atan2d_dash(y,x):
    tmp = atan2d(y,x)
    if tmp <= 0:
        return 360 + tmp
    else:
        return tmp

def theta_a(ttilt,ptilt,h,x,y):
    Xa = xa(ttilt,ptilt,h,x,y)
    Y0 = y0(x,y,ptilt)
    return atand(math.sqrt(abs(Xa)**2+abs(Y0)**2)/(h*cosd(ttilt)+h*sind(ttilt)))

def xa(ttilt,ptilt,h,x,y):
    X0 =  x0(x,y,ptilt)
    return (X0-h*tand(ttilt))*cosd(ttilt)

def phi_a(ttilt,ptilt,h,x,y):
    Xa = xa(ttilt,ptilt,h,x,y)
    Y0 = y0(x,y,ptilt)
    return atan2d(Y0,Xa)

def y0(x,y,ptilt):
    return math.sqrt(x**2+y**2) * sind(atan2d(y,x)-ptilt)

def x0(x,y,ptilt):
    return math.sqrt(x**2+y**2) * cosd(atan2d(y,x)-ptilt)

def db2pow(db):
    return 10**(db/10)

def pow2db(pow):
    return 10*math.log10(pow)

def pol2xy(r,deg):
    return r*cosd(deg),r*sind(deg)


def throughput(b, sinr):
    return b * math.log2(1 + sinr)

