''' Imports '''
from Adafruit_IO import Client
import time
import datetime
#import help
#from apscheduler.schedulers.background import BlockingScheduler
from threading import Thread
import RPi.GPIO as gp
#from rpi_lcd import LCD as my_lcd
#from mfrc522 import SimpleMFRC522
#import MFRC522
rfid = SimpleMFRC522()
ids={
    "5000":"Ibrahim",
    "4000":"Toqa",
    "3000":"Ola"}
''' MAX of Cars Allowed In Garage '''
MAX = 2
first_check=1
#my_lcd= LCD()

''' Access Token Vaiables '''
ADAFRUIT_IO_USERNAME = "Ibrahim_Elsayed"
ADAFRUIT_IO_KEY = "aio_LCcj21HT3iCxRMDU9nxO35ctHH63"

''' create new client to send and receive data with adafruitIO '''
aio = Client(username=ADAFRUIT_IO_USERNAME, key=ADAFRUIT_IO_KEY)


''' Text feed '''
text = f"Smart Garage"
aio.send("text", text)
aio.send("no-dot-of-cars", 0)
aio.send("unit-1", "Empty")
aio.send("unit-2", "Empty")
aio.send("new-client", 0)

time.sleep(5)


# PIn definarion
buzzer1 = 11
buzzer2 = 12
Units_Number = 2
switch = 18
Infrared_Pins = [15, 16]
Unit_State = 0
Empty_Units_Number = 2
minute_money = 10/60


# Pin initialization
gp.setmode(gp.BOARD)

for i in range(Units_Number):
    gp.setup(Infrared_Pins[i], gp.IN)
    
gp.setwarnings(False)
gp.setup(buzzer1, gp.OUT)
gp.setup(buzzer2, gp.OUT)
gp.setup(switch, gp.IN ,pull_up_down=gp.PUD_UP)



def ChangeEmptyUnitsNum():
    book_flag=0
    online_booking={}
    ids_currently_booking=[]
    while 1:
        #store the ir_reads every loop
        ir_reads=[]
        ir_states=[]
        for irs in Infrared_Pins:
            ir_reads.append(gp.input[irs])

        #Assign States
        for irs in ir_reads:
            if (irs == 1):
                ir_states.append("Empty")
            else:
                ir_states.append("Busy")  

        if (ir_reads[0] == 1):
            state1 = "Empty"
        elif (ir_reads[0] == 0):
            state1 = "Busy"
        if (ir_reads[1] == 1 ):
            state2 = "Empty"
        elif (ir_reads[1] == 0):
            state2 = "Busy"

        try:
            book_mess=str(aio.receive('book').value)
            if (book_mess=="1"):
                rfid_mess=str(aio.receive('cars').value)
                if(rfid_mess in ids):
                    if (rfid_mess in ids_currently_booking):
                        try:
                            ids_currently_booking.append(rfid_mess)
                            first_empty=ir_reads.index(0)
                            book_flag=1
                            book_time = datetime.datetime.now()
                            online_booking[first_empty]=(book_time.hour,book_time.minute)
                            print(rfid_mess)
                            aio.send("confirmation", f"{ids[rfid_mess]}, Your Unit Is:{first_empty+1}")
                        except:
                            aio.send("confirmation", "No Empty Units!")
                    else:
                        aio.send("confirmation", "You have already booked")
                else:
                    aio.send("confirmation", "Not Valid ID!")
            #else:
                #aio.send("confirmation", "Waiting For Booking")
        except:
            pass

        if len(online_booking):
            now=datetime.datetime.now()
            for id,time in online_booking:
                if (((now.hour-time[0])*60) + (now.minute - time[1]) < 30):
                    ir_states[id]="Busy"
                else:
                    online_booking.pop(id)





        if first_check:
            ir_states_old=ir_states.copy()
            first_check=0

        for i in range(len(ir_states)):    
            Unit_State_new = help.Convert_To_True_False(ir_states[i])
            Unit_State_old= help.Convert_To_True_False(ir_states_old[i])

        ''' by checking IR sensors, we can know no.of cars in garage '''
        if Unit_State_new != Unit_State_old:
            Unit_State_old = Unit_State_new
            aio.send("unit-1", str(help.Convert_To_Empty_Busy(Unit_State_new)))
            time.sleep(0.5)
            if Unit_State_new == True and NoOfCarsInGarage != 2:
                NoOfCarsInGarage += 1
                aio.send("no-dot-of-cars", NoOfCarsInGarage)
                time.sleep(0.5)
            else:
                if Unit_State_new == False and NoOfCarsInGarage != 0:
                    NoOfCarsInGarage -= 1
                    aio.send("no-dot-of-cars", NoOfCarsInGarage)
                    time.sleep(0.5)






def ReadRFID():
    rfid_dic = {}
    while 1:
        time.sleep(5)
        print("rfid")
        uid,text=rfid.read()
        if uid in rfid_dic:
            start_time=rfid_dic[uid]
            end_time=datetime.datetime.now()
            rfid_dic.pop(uid)
            money_to_pay = ((end_time.hour-start_time[0])*60) + (end_time.minute - start_time[1]) * minute_money
        else:
            rfid_dic[uid]=(datetime.datetime.now().hour,datetime.datetime.now().minute)
        print(rfid_dic)
        '''
        MIFAREReader = MFRC522.MFRC522 ()

        # Scan for cards
        (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        if status == MIFAREReader.MI_OK:
            # Get the UID of the card
            (status, uid) = MIFAREReader.MFRC522_Anticoll()
            
        if status == MIFAREReader.MI_OK:
          
            if (gp.input(switch) == 0):
                while(gp.input(switch) == 0):
                    pass
                dic[uid] = (time.time)/3600

            else:
                cur_time = (time.time)/3600
                whole_time = cur_time - dic[uid]
                dic.pop(uid)
                money_to_pay = whole_time * minute_money
                my_lcd.text(money_to_pay,1)
              '''  

# sched = BlockingScheduler()
#sched.add_job(ChangeEmptyUnitsNum(), 'interval', seconds = 30)  # will do the 'GetEmptyUnits' every 30 seconds
#sched.add_job(ReadRFID(), 'interval', seconds = 5)

#sched.start()

    #''' cheching everything has send successfully by printing data read from each feed '''
    #print("Unit 1 state: " + aio.receive('unit-1').value)
    #print("Unit 2 state: " + aio.receive('unit-2').value)
    #print("No.of Cars in Garage is: " + aio.receive('no-dot-of-cars').value
units_thread = Thread(target=ChangeEmptyUnitsNum)
rfid_thread = Thread(target=ReadRFID)


#units_thread.start()
#rfid_thread.start()
    #ReadRFID()
