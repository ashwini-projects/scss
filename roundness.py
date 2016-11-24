import serial
import time
import math
import matplotlib.pyplot as plt
import numpy as np
import random


sensorSerialPort = 4  # serial port for gauge
arduinoSerialPort = 6 # serial port for arduino
resultDir = r"C:\Users\surendrankn\Desktop\camreadings\readings"
testProgramWithSetup = 1
debug = False

##################################################
##### Interact with the sensor
##################################################
def getReadingsFromSensor_V2(sensorPort = 4, ardPort = 3):
    realValPlot = []
    # theta = [0]
    points = float(input("Enter number of points: "))
    theta = [i * (360/points) * 0.01745  for i in range(int(points)+1)]
    print "\nMotor will rotate by [", str(360 / points), "] degrees for each reading"

    def recordGaugeReading(seportHandler, i = 0):
        # request reading from the gauge port by sending "?" char
        seportHandler.write("?\r\n")
        line = seportHandler.readline()
        if debug:
            print "\t\t reading from the gauge", str(line.strip())
        print str(i+1), "|", str(line)
        val = float(line.strip())
        # todo: why are you adding 10?
        realValPlot.append( val + 10.0)

    def writeToArduino(portHandle, i):
        # write "h" to arduino for rotating motor, read back 't\r\n'
        portHandle.write('h')
        if debug:
            print str(i) + "\t\t..hoping that i wrote to arduino"
        val = 't\r\n' # expected value: hard coding for now
        return val

    if testProgramWithSetup:
        print "checking if arduino and sensor are connected properly"
        gaugeport = serial.Serial(sensorPort)  # serial port for gauge
        arduino = serial.Serial(ardPort) # serial port for arduino
        print ">> >> arduino and sensor check successful..."
        if debug: 
            print ">> >> sensor & arduino ports ", sensorPort, ardPort

        ##################################################
        """
        Set the degrees of revolution for arduino
        """
        # tell arduino to rotate by the calculated number of degrees...
        # stepsPerRevolution will be set to the value being passed below
        ################################################## 
        s = 'v' + str(int(360 / points)) + ','
        print "...setting stepsPerRevolution value", s
        arduino.write(s)
        time.sleep(1)
        print ">> >> motor to rotate by", str(360/points), "degrees\n"
        ################################################## 


        # get initial reading from the gauge
        recordGaugeReading(gaugeport)

        # start reading more values as the gauge rotates
        for i in range(int(points)):
            gaugeport.setDTR(level=0)
            val = writeToArduino(arduino, i)
            time.sleep(2) # allow the motor to rotate before taking the reading
            if val =='t\r\n' :
                recordGaugeReading(gaugeport, i)
             
        gaugeport.close()
        arduino.close()
    else:
        realValPlot = [1 + (random.randrange(0,10.0) / float(random.randrange(10.0, 100.0))) for i in range(int(points)+1)]
    return theta, realValPlot
##################################################

##################################################
#####  FUNCTION to create the results TABLE
##################################################
"""
input values---
    inRotation      : rotation values of the motor
    inGaugeReading : readings from the gauge
    outDir         : directory where to create the calculated csv file
"""
def generateResultTable(inRotation, inGaugeReading, outdir=resultDir):
    import csv
    import datetime
    filedir = r"d:/temp/" if outdir is None else outdir
   

    def getCalculatedValues(iRotation, iGaugeReading):
        inReading = []
        totalPts = len(iRotation)
        resXo = 0
        resYo = 0
        resRo = 0
        resRE = 0    

        # convert radians to degrees
        rot = [math.degrees(r) for r in iRotation]
        iRotation = rot
        
        # calc Xi, Yi
        Xi = []
        Yi = []
        for i in range(totalPts):
            Xi.append(iGaugeReading[i] * math.cos(iRotation[i]))
            Yi.append(iGaugeReading[i] * math.sin(iRotation[i]))

        ### calc Xo, Yo (items 1 & 2)
        resXo = Xo = 2 * sum(Xi) / len(Xi)
        resYo = Yo = 2 * sum(Yi) / len(Yi)
        # todo: check if the below formula is correct
        resRo = Ro = 2 * sum(iGaugeReading) / len(Yi)
    
        # calc Xr, Yr
        Xr = []
        Yr = []
        for i in range(totalPts):
            Xr.append(Xo * math.cos(iRotation[i]))
            Yr.append(Yo * math.sin(iRotation[i]))
        
        # calculate Ri
        Ri = []
        for i in range(totalPts):
            Ri.append(Ro + Xo * math.cos(iRotation[i]) + Yo * math.sin(iRotation[i]))

        # calculate deviation
        deviation = []
        for i in range(totalPts):
            deviation.append(iGaugeReading[i] - Ri[i])
        
        for i in range(totalPts):
            inReading.append([iRotation[i], iGaugeReading[i], Xi[i], Yi[i], Xr[i], Yr[i], Ri[i], deviation[i]])

        # Roundness error
        resRE = RoundnessError = math.fabs(min(deviation)) + math.fabs(max(deviation))

        summaryReport(resXo, resYo, resRo, resRE)
        return inReading


    def summaryReport(resXo, resYo, resRo, resRE):
        # Xo, Yo, Ro, RoundnessError, Eccentricity, Angle, Concentricity
        print "="*30
        print "Summary Report:"
        print " Xo=", resXo
        print " Yo=", resYo
        print " Ro=", resRo
        print " Roundness Error", resRE
        print "="*30

    """
    return the filename that contains todays date, time (hms)
    """
    def getFileName(fdir=filedir):
        now = datetime.datetime.now()
        name = now.strftime("%Y_%M_%d_%H_%M_%S")
        return str(fdir) + "/" + str(name) + ".csv"

    """
    writes the calculated results to a csv file
    """
    def writetocsv(records, filename = getFileName()):
        # readings = [[{degree: "", reading: "", val1 : ""}], ...]
        with open (filename, 'wb') as csvfile:
            mywriter = csv.writer(csvfile, delimiter=',')
            # write the header row first
            mywriter.writerow(["Rotation in degrees", "Dial gauge reading", "Xi", "Yi", "Xr", "Yr", "Ri", "Deviation"])
            # then write all the records to the csv
            [mywriter.writerow(row) for row in records]
        print "XLS:", filename
        csvfile.close()

    print inRotation
    readings = getCalculatedValues(inRotation, inGaugeReading)
    writetocsv(readings)

###############END RESULTS TABLE ####################

##################################################
##### FUNCTION to create the plot
##################################################
def doPlot(values, degrees) :
    plt.axes(polar=True)
    plt.polar(degrees, values, linestyle='solid', linewidth=1.5,
              color='blue', marker='.', markersize=2.0,
              markeredgecolor='red', markeredgewidth=0.5)
    plt.thetagrids([0.0, 90.0, 180.0, 270.0])
    plt.show()

###############END PLOT ###########################

######### main function #########
rotations, readings = getReadingsFromSensor_V2(sensorSerialPort, arduinoSerialPort) # controls the moto rotations and grabs the readings
print "got all the readings from the experiment; calculating results..."
print "..."
generateResultTable(rotations, readings) # performs calculations and writes to csv file
print "..."
print "Generating plot for the observed results"
doPlot(readings, rotations) # shows the final plot

######################### END WORKING CODE ##############

