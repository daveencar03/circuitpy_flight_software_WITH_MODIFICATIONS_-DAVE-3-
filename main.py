'''
Created by Nicole Maggard and Michael Pham 8/19/2022
Updated for Yearling by Nicole Maggard and Rachel Sarmiento 2/4/2023
This is where the processes get scheduled, and satellite operations are handeled
'''
print("Hi inspireFly")

from lib.pysquared import cubesat as c
import asyncio
import time
import traceback
import gc #Garbage collection
import microcontroller
import functions
from debugcolor import co
from easy_comms_circuit import EasyComms
import board
from FCB_class import FCBCommunicator
#from lib import rfm9xfsk
import sdcardio
import storage
import busio
import microcontroller
import board
import os
# 
# spi = busio.SPI(board.SPI0_SCK, board.SPI0_MOSI, board.SPI0_MISO)
# sd = sdcardio.SDCard(spi, board.SPI0_CS1)
# vfs = storage.VfsFat(sd)
# storage.mount(vfs, "/sd")

f=functions.functions(c)

# # inspireFly Test Mode Loop !!!
# runOnce = True
# while True:
#     if runOnce:
#         print("You are in inspireFly test mode. Comment this while loop out on line 34 in main")
#         c.all_faces_on()
#         runOnce = False
#         f.transmit_image()
#     f.listen()
#     #f.send(0xFF)
#     #print("Done")
    
    

def debug_print(statement):
    if c.debug:
        print(co("[MAIN]" + str(statement), 'blue', 'bold'))

try:
    debug_print("Boot number: " + str(c.c_boot))
    debug_print(str(gc.mem_free()) + " Bytes remaining")

    #power cycle faces to ensure sensors are on:
    #c.all_faces_off()
    time.sleep(1)
    c.all_faces_on()
    #test the battery:
    c.battery_manager()
    f.beacon()
    f.listen()
    distance1=0
    distance2=0
    tries=0
    loiter_time = 270
    dutycycle=0.15
    done=True
    debug_print("(iF) burn attempt status stuff")
    
    for i in range(1):
        done = c.burn('1', dutycycle, 1000, 1.2)
        time.sleep(0.5)
    #done = c.burn('1', dutycycle, 1000, 1)
    #done=c.smart_burn('1',dutycycle)


    
    """
    ******************ALL SMART_BURN CODE (commented out for testing)******************************
    debug_print("Burn attempt status: " + str(c.burnarm))
    debug_print("Burn status: " + str(c.burned))
    while c.burned is False and tries < 3:
        debug_print("Burn attempt try: " + str(tries+1))
        if tries == 0:
            debug_print("Loitering for " + str(loiter_time) + " seconds")
            try:
                c.neopixel[0] = (0,0,0)
                
                purple = (200, 8, 200)
                led_off = (0,0,0)
                
                for step in range(0,loiter_time):
                    
                    c.neopixel[0] = purple
                    time.sleep(0.5)
                    c.neopixel[0] = led_off
                    time.sleep(0.5)
                    debug_print(f"Entering full flight software in... {loiter_time-step} seconds")
            except Exception as e:
                debug_print("Error in Loiter Sequence: " + ''.join(traceback.format_exception(e)))
        try:
            debug_print("(iF) smart burn function is executing")
            dutycycle=dutycycle+0.02
            done=c.smart_burn('1',dutycycle)
            tries+=1
        except:
            debug_print("couldnt burn on try " + str(tries+1))
        if done is True:
            debug_print("attempt passed without error!")
            if c.burned is False and tries>=2:
                debug_print("Ran Out of Smart Burn Attempts. Will Attempt automated burn...")
                wait=0
                while(wait<5):
                    wait+=1
                    time.sleep(1)
                c.burn('1',0.28,1000,2)
            else:
                pass
        else:
            debug_print("burn failed miserably!")
            break
    ******************************************************************************************            
    """        


    f.beacon()
    f.listen()
    f.state_of_health()
    f.listen()

    c.battery_manager()
    #f.battery_heater()
    c.battery_manager() #Second check to make sure we have enough power to continue

    f.beacon()
    f.listen()
    f.state_of_health()
    f.listen()
except Exception as e:
    debug_print("Error in Boot Sequence: " + ''.join(traceback.format_exception(e)))
finally:
    debug_print("All Faces off!")
    #c.all_faces_off()

def critical_power_operations():
    
    f.beacon()
    f.listen()
    f.state_of_health()
    f.listen()  
     
    f.Long_Hybernate()

def minimum_power_operations():
    
    f.beacon()
    f.listen()
    f.state_of_health()
    f.listen()
    
    f.Short_Hybernate() 
        
def normal_power_operations():
    
    debug_print("Entering Norm Operations")
    FaceData=[]
    #Defining L1 Tasks
    def check_power():
        gc.collect()
        c.battery_manager()
        #f.battery_heater()
        c.check_reboot()
        c.battery_manager() #Second check to make sure we have enough power to continue
        
        if c.power_mode == 'normal' or c.power_mode == 'maximum': 
            pwr = True
            if c.power_mode == 'normal':
                c.RGB=(255,255,0)
            else:
                c.RGB=(0,255,0)
        else:
            pwr = False

        debug_print(c.power_mode)
        gc.collect()
        return pwr
    
    async def s_lora_beacon():
        while check_power():
            f.beacon()
            f.listen()
            f.state_of_health()
            f.listen()
            await asyncio.sleep(10)  # Reduced from 30 to 10 for better responsiveness

    async def g_face_data():
        while check_power():
            try:
                debug_print("Getting face data...")
                FaceData = f.all_face_data()
                for i, data in enumerate(FaceData):
                    debug_print(f"Face {i}: {data}")
            except Exception as e:
                debug_print('Error: ' + ''.join(traceback.format_exception(e)))
            gc.collect()
            await asyncio.sleep(30)  # Reduced from 60 to 30 for more frequent updates
        
    
    async def s_face_data():
        await asyncio.sleep(10)
        while check_power():
            try:
                debug_print("Sending face data...")
                f.send_face()
            except asyncio.TimeoutError as e:
                debug_print('Error: ' + ''.join(traceback.format_exception(e)))
            gc.collect()
            await asyncio.sleep(60)  # Reduced from 200 to 60 for more frequent transmissions

    async def s_imu_data():
        await asyncio.sleep(20)
        while check_power():
            try:
                debug_print("Getting IMU data...")
                IMUData = f.get_imu_data()
                f.send(IMUData)
            except Exception as e:
                debug_print('Error: ' + ''.join(traceback.format_exception(e)))
            gc.collect()
            await asyncio.sleep(45)  # Reduced from 100 to 45 for better real-time tracking
        
    async def detumble():
        await asyncio.sleep(50)
        while check_power():
            try:
                debug_print("Performing detumble...")
                f.detumble()
            except Exception as e:
                debug_print('Error: ' + ''.join(traceback.format_exception(e)))
            gc.collect()
            await asyncio.sleep(60)  # Reduced from 100 to 60 for better control

#     async def joke():
#         await asyncio.sleep(500)
# 
#         while check_power():
#             try:
#                 debug_print("Joke send go!")
#                 f.joke()
#                 if f.listen_joke():
#                     f.joke()
#                 debug_print("done!")
#             except Exception as e:
#                 debug_print(f'Outta time!' + ''.join(traceback.format_exception(e)))
#             
#             gc.collect()
#             await asyncio.sleep(300)
#     
# 
# 
# 
#     async def pcb_comms():
#         debug_print("Yapping to the PCB now - D")
#         await asyncio.sleep(30)
# 
#         image_count = 1  # Start from 1
#         image_dir = "/sd"
# 
#         # Ensure the directory exists (CircuitPython auto-mounts /sd, but this prevents issues)
#         try:
#             if "sd" not in os.listdir("/"):
#                 raise OSError("SD card not found")
#         except OSError:
#             debug_print("SD card not detected or cannot be accessed!")
#             return
# 
#         while True:
#             debug_print("Starting new PCB communication cycle")
#             gc.collect()
#             debug_print(f"Free memory before cycle: {gc.mem_free()} bytes")
# 
#             try:
#                 com1 = EasyComms(board.TX, board.RX, baud_rate=9600)
#                 com1.start()
#                 fcb_comm = FCBCommunicator(com1)
# 
#                 overhead_command = com1.overhead_read()
#                 command = 'chunk'
#                 await asyncio.sleep(2)
# 
#                 if command.lower() == 'chunk':
#                     fcb_comm.send_command("chunk")
# 
#                     if fcb_comm.wait_for_acknowledgment():
#                         await asyncio.sleep(1)
#                         gc.collect()
#                         debug_print(f"Free memory before data transfer: {gc.mem_free()} bytes")
# 
#                         # Get existing files and determine next available filename
#                         existing_files = os.listdir(image_dir)
#                         while f"inspireFly_Capture_{image_count}.jpg" in existing_files:
#                             image_count += 1
# 
#                         img_file_path = f"{image_dir}/inspireFly_Capture_{image_count}.jpg"
#                         temp_file_path = f"{image_dir}/inspireFly_Capture_{image_count}_temp.jpg"
# 
#                         try:
#                             # Preallocate file (estimated size)
#                             estimated_size = 1000  # Adjust as needed
#                             with open(img_file_path, "wb") as img_file:
#                                 img_file.write(b'\xFF' * estimated_size)
#                             debug_print(f"Preallocated {estimated_size} bytes for image storage.")
# 
#                             # Write data to the preallocated file
#                             offset = 0
#                             with open(img_file_path, "r+b") as img_file:
#                                 while True:
#                                     jpg_bytes = fcb_comm.send_chunk_request()
#                                     if jpg_bytes is None:
#                                         break
#                                     img_file.seek(offset)
#                                     img_file.write(jpg_bytes)
#                                     offset += len(jpg_bytes)
#                                     debug_print(f"Saved chunk of {len(jpg_bytes)} bytes at offset {offset}")
#                                     del jpg_bytes
#                                     gc.collect()
#                                     break
# 
#                             debug_print(f"Finished writing image. Data size: {offset} bytes")
# 
#                             # Workaround for truncate: copy valid data to a new file
#                             with open(img_file_path, "rb") as orig_file:
#                                 valid_data = orig_file.read(offset)
#                             with open(temp_file_path, "wb") as temp_file:
#                                 temp_file.write(valid_data)
# 
#                             # Remove the old file and rename the new file
#                             os.remove(img_file_path)
#                             os.rename(temp_file_path, img_file_path)
#                             debug_print(f"File saved as {img_file_path}")
# 
#                         except OSError as e:
#                             debug_print(f"Error writing to SD card: {str(e)}")
#                             continue
# 
#                 command = 'end'
# 
#                 if command.lower() == 'end':
#                     fcb_comm.end_communication()
#                     await asyncio.sleep(3)
# 
#             except Exception as e:
#                 debug_print(f"Error in PCB communication: {str(e)}")
# 
#             del com1, fcb_comm
#             gc.collect()
#             debug_print(f"Free memory after cleanup: {gc.mem_free()} bytes")
#             await asyncio.sleep(500)






    async def main_loop():
        tasks = [
            asyncio.create_task(s_lora_beacon()),
            asyncio.create_task(s_face_data()),
            asyncio.create_task(s_imu_data()),
            asyncio.create_task(g_face_data()),
            asyncio.create_task(detumble()),
        ]
        await asyncio.gather(*tasks)


    asyncio.run(main_loop())


######################### MAIN LOOP ##############################
try:
    c.all_faces_on()
    while True:
        #L0 automatic tasks no matter the battery level
        c.battery_manager()
        c.check_reboot()
        
        if c.power_mode == 'critical':
            c.RGB=(0,0,0)
            critical_power_operations()
            
        elif c.power_mode == 'minimum':
            c.RGB=(255,0,0)
            minimum_power_operations()
            
        elif c.power_mode == 'normal':
            c.RGB=(255,255,0)
            normal_power_operations()
            
        elif c.power_mode == 'maximum':
            c.RGB=(0,255,0)
            normal_power_operations()
            
        else:
            f.listen()
except Exception as e:
    debug_print("Error in Main Loop: " + ''.join(traceback.format_exception(e)))
    time.sleep(10)
    microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
    microcontroller.reset()
finally:
    #debug_print("All Faces off!")
    #c.all_faces_off()
    c.RGB=(0,0,0)
