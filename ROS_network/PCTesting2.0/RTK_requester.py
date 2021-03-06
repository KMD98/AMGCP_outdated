#!/usr/bin/env python3
# Creator: Kha Dan Research Engineer
# Code info: Gather all RTK data on I2C and publish lat lon heading speed of autonomous robot
# and publishes lat lon heigh of UAV  
#from smbus import SMBus
import time
import rospy
from ros_essentials_cpp.msg import drone_RTKpose, AMGCP_RTKpose
addr_droneCoor = 0x08
addr_MGCPCoor = 0x09
addr_heading = 0x07
#bus = SMBus(1)
#time.sleep(0.100)
    
#I2C subroutines for master and send back data from each slave
def readingI2CbusDrone(addr):
    #grab coordinates
    temp = bus.read_i2c_block_data(addr,0,19)
    return bytetoFloatDrone(temp)

def readingI2CBusMGCP(addr):
    temp = bus.read_i2c_block_data(addr,0,19)
    return bytetoFloatMGCP(temp)    

def readingI2CBusHeading(addr):
    temp = bus.read_i2c_block_data(addr,0,4)
    return bytetoFloatHeading(temp)

def bytetoFloatDrone(temp):
    data = []
    coor = []
    i = 0
    c = 0
    #note that data in the third entry or data[2] may lose a zero if character count is less than 4
    # make sure to append that 0 before conversion to float array
    while i <=14:
        data.append(str((temp[i]<<8) + temp[i+1]))
        i = i + 2
    #Scan the i2c data to see if any of the lat,lon, or height is negative and change value to appropriate sign
    if temp[16] == 1:
        data[0] = str(-1*int(data[0]))
    if temp[17] == 1:
        data[3] = str(-1*int(data[3]))
    if temp[18] == 1:
        data[6] = str(-1*int(data[6]))
    #make sure the 4 remaining decimal for lat and lon always has 4 characters, if not that means a leading 0 was dropped. Insert the 0
    #keep adding 0 to the front until len of 4 has been met. Not needing for heigh because heigh decimal can be represented with a single int
    while len(data[2]) < 4:
        data[2] = "0" + data[2]
    while len(data[5]) < 4:
        data[5] = "0" + data[5]
    #Now convert to string list
    count = 0
    while count <=6:
        if count < 6:
            coor.append(data[count] + "." + data[count+1] + data[count+2])
            count+=3
        elif count == 6:
            coor.append(data[count] + "." + data[count+1])
            break
    data.clear()
    #convert strings in coor list to floats
    coor = [float(i) for i in coor]
    return coor

def bytetoFloatMGCP(temp):
    data = []
    i = 0
    #the order is lat,lon,height,groundspeed
    while i <=12:
        data.append((temp[i]<<24) + (temp[i+1]<<16) +(temp[i+2]<<8) + temp[i+3])
        i+=4
    #Divide lat and lon data by 10000000.0f and height by 1000.0f to get decimal place
    if temp[16] == 1:
        data[0] = -1*(float(data[0])/float(10000000.0))
    elif temp[16] == 0:
        data[0] = float(data[0])/float(10000000.0)
    if temp[17] == 1:
        data[1] = -1*(float(data[1])/float(10000000.0))     
    elif temp[17] == 0:
        data[1] = float(data[1])/float(10000000.0)      
    if temp[18] == 1:
        data[2] = -1*(float(data[2])/float(1000.0))
    if temp[18] == 0:
        data[2] = float(data[2])/float(1000.0)
    #ground speed cannot be negative so no condition statement needed here
    data[3] = float(data[3])/float(1000.0) #m/s
    return data

def bytetoFloatHeading(temp):
    data = (float((temp[0]<<24) + (temp[1]<<16) + (temp[2]<<8) + temp[3])/float(100.0))
    return data

        
def odometryPub():
    rospy.init_node('RTK_odometry_node', anonymous = True)
    node_name = rospy.get_name()
    rospy.loginfo("Started node %s" % node_name)
    ugs_pub = rospy.Publisher('/RTK/amgcp_RTKpose',AMGCP_RTKpose,queue_size=10)
    uav_pub = rospy.Publisher('/RTK/drone_RTKpose',drone_RTKpose,queue_size=10)
    #loop rate is 1Hz
    rate = rospy.Rate(1)
    while not rospy.is_shutdown():
        amgcp_data = AMGCP_RTKpose()
        drone_data = drone_RTKpose()
        '''time.sleep(0.005)
        drone_coor = readingI2CbusDrone(addr_droneCoor)
        #delay between reads to be definite that SDA Has pulled low
        time.sleep(0.005)
        mgcp_coor = readingI2CBusMGCP(addr_MGCPCoor)
        time.sleep(0.005)
        mgcp_heading = readingI2CBusHeading(addr_heading)
        drone_data.drone_lat = drone_coor[0] #y axis
        drone_data.drone_lon = drone_coor[1] #x-axis
        drone_data.drone_height = drone_coor[2]
        amgcp_data.amgcp_lat = mgcp_coor[0]
        amgcp_data.amgcp_lon = mgcp_coor[1]
        amgcp_data.amgcp_height = mgcp_coor[2]
        amgcp_data.speed2D = mgcp_coor[3]
        amgcp_data.bearing = mgcp_heading'''
        drone_data.drone_lat = 33.4776589 #y axis
        drone_data.drone_lon = -88.8263006 #x-axis
        drone_data.drone_hmsl = 120
        amgcp_data.amgcp_lat = 33.4776589
        amgcp_data.amgcp_lon = -88.8263006
        amgcp_data.amgcp_height = 98
        amgcp_data.speed2D = 1
        amgcp_data.bearing = 250.30
        '''rospy.loginfo("I published: ")
        rospy.loginfo(drone_data)
        rospy.loginfo(amgcp_data)'''
        uav_pub.publish(drone_data)
        ugs_pub.publish(amgcp_data)
        rate.sleep()
        
if __name__ == '__main__':
    try:
        odometryPub()
        rospy.loginfo("Finished")
        rospy.spin()
    except rospy.ROSInterruptException:
        pass

