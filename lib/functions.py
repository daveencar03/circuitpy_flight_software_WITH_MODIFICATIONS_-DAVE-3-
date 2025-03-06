'''
This is the class that contains all of the functions for our CubeSat. 
We pass the cubesat object to it for the definitions and then it executes 
our will.
Authors: Nicole Maggard, Michael Pham, and Rachel Sarmiento
'''
import time
import alarm
import gc
import traceback
import random
from debugcolor import co
import sys
import os
import math

class functions:

    # INSPIREFLY FUNCTIONS:
    
    def AX_25Wrapper(self, message):
        # TO-DO
        return

    def TransmitMessage(self, message):
        # TO-DO
        return

    def transmit_image(self):
        
        file_path = "blue.jpg"
        file_info = os.stat(file_path)
        file_size = file_info[6]  # The 7th item in the stat tuple is the file size
        print(f"Image size: ", file_size)
        image = open(r"blue.jpg", 'rb') 
        
        
        bytes_per_packet = 10
        total_packets = math.ceil(file_size / bytes_per_packet)
        print("Total Packets: ", total_packets)
        
        current_packet_index = 0
        current_packet = image.read(bytes_per_packet)
        
        send_command = 0x28
        call_sign = "KQ4LFD"
        call_sign_bytes = bytearray(call_sign, "utf-8")
        
        
        received_packet_index = 0
        packet = None
        
        
        
        while True:
            send_message = call_sign_bytes + bytearray(" ", "utf-8") + send_command.to_bytes(1, 'big') + total_packets.to_bytes(2, 'big') + call_sign_bytes
            #send_message = send_command.to_bytes(1, 'big') + total_packets.to_bytes(2, 'big')
            print("Sending: ", send_message)
            
            #for i in range(1):
            self.cubesat.radio1.send(send_message)
            
            
            time.sleep(0.1)
            
            packet = self.cubesat.radio1.receive()
            print("Received Loop 1: ", packet)
            
            if packet is not None:
                if (packet[0:1] == b'\x34'): 
                    break
            
            
            
        while True:
            
            print("Received Loop 2: ", packet)
            
            if packet is not None:
                if (packet[0:1] == b'\x34'):
                    received_packet_index = int.from_bytes(packet[1:3], "big")
                    print("Received packet index: ", received_packet_index)
                    
                    if received_packet_index == current_packet_index:
                        
                        message = call_sign_bytes + bytearray(" ", "utf-8") + send_command.to_bytes(1, 'big') + current_packet_index.to_bytes(2, "big") + current_packet + call_sign_bytes
                        
                        print("Sending: ", message)
                        
                        packet = None
                        while True:
                            for i in range(10):
                                self.cubesat.radio1.send(message)
                                
                            packet = self.cubesat.radio1.receive()           
                            print("Received packet in bugging part: ", packet)
                            
                            if packet:
                                if int.from_bytes(packet[1:3], "big") == current_packet_index + 1:
                                    break
                        
                        current_packet = image.read(bytes_per_packet)
                        current_packet_index += 1
            else:
                packet = self.cubesat.radio1.receive()
                
            print(current_packet_index)
            
            if current_packet_index >= total_packets:
                break
            
            #time.sleep(0.2)
            
        print("Finished Sending Image")
            
            

    def debug_print(self, statement):
        if self.debug:
            print(co("[Functions]" + str(statement), 'green', 'bold'))

    def __init__(self, cubesat):
        self.cubesat = cubesat
        self.debug = cubesat.debug
        self.debug_print("Initializing Functionalities")
        self.Errorcount = 0
        self.facestring = []
        self.jokes = ["Hey Its pretty cold up here, did someone forget to pay the electric bill?"]
        self.last_battery_temp = 20
        self.callsign = "KQ4LFD"
        self.state_bool = False
        self.face_data_baton = False
        self.detumble_enable_z = True
        self.detumble_enable_x = True
        self.detumble_enable_y = True
        try:
            self.cubesat.all_faces_on()
        except Exception as e:
            self.debug_print("Couldn't turn faces on: " + ''.join(traceback.format_exception(e)))
    
    # ... Other methods remain unchanged ...
    def beacon(self):
        """Calls the RFM9x to send a beacon. """
        import Field
        try:
            lora_beacon = f"{self.callsign} Hello I am Yearling^2! I am in: " + str(self.cubesat.power_mode) +" power mode. V_Batt = " + str(self.cubesat.battery_voltage) + f"V. IHBPFJASTMNE! {self.callsign}"
        except Exception as e:
            self.debug_print("Error with obtaining power data: " + ''.join(traceback.format_exception(e)))
            lora_beacon = f"{self.callsign} Hello I am Yearling^2! I am in: " + "an unidentified" +" power mode. V_Batt = " + "Unknown" + f". IHBPFJASTMNE! {self.callsign}"

        self.field = Field.Field(self.cubesat,self.debug)
        self.field.Beacon(lora_beacon)
#         if self.cubesat.f_fsk:
#             self.cubesat.radio1.cw(lora_beacon)
        del self.field
        del Field
        
    def all_face_data(self):
        self.cubesat.all_faces_on()
        try:
            import Big_Data
            a = Big_Data.AllFaces(self.debug, self.cubesat.tca)

            self.debug_print("[DEBUG] Running Face_Test_All()...")
            facestring_data = a.Face_Test_All()
            self.debug_print(f"[DEBUG] Face_Test_All() returned: {facestring_data}")

            # Validate facestring_data before assigning
            if not isinstance(facestring_data, list):
                self.debug_print(f"[ERROR] Face_Test_All() did not return a list! Value: {facestring_data}")
                self.facestring = ["ERROR"] * 5  # Default fallback
            elif len(facestring_data) < 5:
                self.debug_print(f"[ERROR] Face_Test_All() returned too few elements: {facestring_data}")
                self.facestring = facestring_data + ["MISSING"] * (5 - len(facestring_data))  # Pad list
            else:
                self.facestring = facestring_data  # Assign valid data

            del a
            del Big_Data

        except Exception as e:
            self.debug_print("[ERROR] Big_Data error: " + ''.join(traceback.format_exception(e)))
            self.facestring = ["EXCEPTION"] * 5  # Prevent crash

        return self.facestring
    
    def listen(self):
        import cdh
        #This just passes the message through. Maybe add more functionality later. 
        try:
            self.debug_print("Listening")
            
            
            # Change timeout back to 10
            self.cubesat.radio1.receive_timeout=10
            received = self.cubesat.radio1.receive_with_ack(keep_listening=True)
        except Exception as e:
            self.debug_print("An Error has occured while listening: " + ''.join(traceback.format_exception(e)))
            received=None

        try:
            if received is not None:
                self.debug_print("Recieved Packet: "+str(received))
                cdh.message_handler(self.cubesat,received)
                return True
        except Exception as e:
            self.debug_print("An Error has occured while handling command: " + ''.join(traceback.format_exception(e)))
        finally:
            del cdh
        
        return False
    
    def format_state_of_health(self, hardware):
        to_return = ""
        for key, value in hardware.items():
            to_return = to_return + key + "="
            if value:
                to_return += "1"
            else:
                to_return += "0"

            if len(to_return) > 245:
                return to_return

        return to_return
    
    def state_of_health(self):
        import Field
        self.state_list=[]
        #list of state information 
        try:
            self.state_list = [
                f"PM:{self.cubesat.power_mode}",
                f"VB:{self.cubesat.battery_voltage}",
                f"ID:{self.cubesat.current_draw}",
                f"IC:{self.cubesat.charge_current}",
                f"VS:{self.cubesat.system_voltage}",
                f"UT:{self.cubesat.uptime}",
                f"BN:{self.cubesat.c_boot}",
                f"MT:{self.cubesat.micro.cpu.temperature}",
                f"RT:{self.cubesat.radio1.former_temperature}",
                f"AT:{self.cubesat.internal_temperature}",
                f"BT:{self.last_battery_temp}",
                f"AB:{int(self.cubesat.burned)}",
                f"BO:{int(self.cubesat.f_brownout)}",
                f"FK:{int(self.cubesat.f_fsk)}"
            ]
        except Exception as e:
            self.debug_print("Couldn't aquire data for the state of health: " + ''.join(traceback.format_exception(e)))
        
        self.field = Field.Field(self.cubesat,self.debug)
        if not self.state_bool:
            self.field.Beacon(f"{self.callsign} Yearling^2 State of Health 1/2" + str(self.format_state_of_health(self.cubesat.hardware))+ f"{self.callsign}")
#             if self.cubesat.f_fsk:
#                 self.cubesat.radio1.cw(f"{self.callsign} Yearling^2 State of Health 1/2" + str(self.state_list)+ f"{self.callsign}")
            self.state_bool=True
        else:
            self.field.Beacon(f"{self.callsign} YSOH 2/2" + str(self.cubesat.hardware) +f"{self.callsign}")
#             if self.cubesat.f_fsk:
#                 self.cubesat.radio1.cw(f"{self.callsign} YSOH 2/2" + str(self.cubesat.hardware) +f"{self.callsign}")
            self.state_bool=False
        del self.field
        del Field
    
    def send_face(self):
        """Calls the data transmit function from the field class"""
        import Field
        self.field = Field.Field(self.cubesat, self.debug)

        try:
            self.debug_print("Sending Face Data")
            time.sleep(1)

            # Debugging step: Check facestring content
            if not hasattr(self, 'facestring') or not isinstance(self.facestring, list):
                self.debug_print(f"[ERROR] self.facestring does not exist or is not a list: {self.facestring}")
                return

            if len(self.facestring) < 5:
                self.debug_print(f"[ERROR] self.facestring has insufficient elements: {self.facestring}")
                return  # Avoid indexing error

            # Safe message construction
            message = f'{self.callsign} Y-: {self.facestring[0]} Y+: {self.facestring[1]} X-: {self.facestring[2]} X+: {self.facestring[3]}  Z-: {self.facestring[4]} {self.callsign}'
            self.debug_print(f"[DEBUG] Sending message: {message}")  # Debug message before sending
            
            self.field.Beacon(message)

            if self.cubesat.f_fsk:
                self.cubesat.radio1.cw(message)

        except Exception as e:
            self.debug_print(f"[ERROR] send_face failed: {e}")

        finally:
            del self.field
            del Field
            
    def get_imu_data(self):
        
        self.cubesat.all_faces_on()
        try:
            data=[]
            data.append(self.cubesat.IMU.acceleration)
            data.append(self.cubesat.IMU.gyro)
            data.append(self.cubesat.magnetometer.magnetic)
        except Exception as e:
            self.debug_print("Error retrieving IMU data" + ''.join(traceback.format_exception(e)))
        
        return data
    
    def send(self,msg):
        """Calls the RFM9x to send a message. Currently only sends with default settings.
        
        Args:
            msg (String,Byte Array): Pass the String or Byte Array to be sent. 
        """
        import Field
        self.field = Field.Field(self.cubesat,self.debug)
        message=f"{self.callsign} " + str(msg) + f" {self.callsign}"
        self.field.Beacon(message)
#         if self.cubesat.f_fsk:
#             self.cubesat.radio1.cw(message)
        if self.cubesat.is_licensed:
            self.debug_print(f"Sent Packet: " + message)
        else:
            self.debug_print("Failed to send packet")
        del self.field
        del Field
        
    def detumble(self,dur = 7, margin = 0.2, seq = 118):
        self.debug_print("Detumbling")
        self.cubesat.RGB=(255,255,255)
        self.cubesat.all_faces_on()
        try:
            import Big_Data
            a=Big_Data.AllFaces(self.debug, self.cubesat.tca)
        except Exception as e:
            self.debug_print("Error Importing Big Data: " + ''.join(traceback.format_exception(e)))

        try:
            a.sequence=52
        except Exception as e:
            self.debug_print("Error setting motor driver sequences: " + ''.join(traceback.format_exception(e)))
        
        def actuate(dipole,duration):
            #TODO figure out if there is a way to reverse direction of sequence
            if abs(dipole[0]) > 1:
                a.Face2.drive=52
                a.drvx_actuate(duration)
            if abs(dipole[1]) > 1:
                a.Face0.drive=52
                a.drvy_actuate(duration)
            if abs(dipole[2]) > 1:
                a.Face4.drive=52
                a.drvz_actuate(duration)
            
        def do_detumble():
            try:
                import detumble
                for _ in range(3):
                    data=[self.cubesat.IMU.gyro,self.cubesat.IMU.Magnetometer]
                    data[0]=list(data[0])
                    for x in range(3):
                        if data[0][x] < 0.01:
                            data[0][x]=0.0
                    data[0]=tuple(data[0])
                    dipole=detumble.magnetorquer_dipole(data[1],data[0])
                    self.debug_print("Dipole: " + str(dipole))
                    self.send("Detumbling! Gyro, Mag: " + str(data))
                    time.sleep(1)
                    actuate(dipole,dur)
            except Exception as e:
                self.debug_print("Detumble error: " + ''.join(traceback.format_exception(e)))
        try:
            self.debug_print("Attempting")
            do_detumble()
        except Exception as e:
            self.debug_print('Detumble error: ' + ''.join(traceback.format_exception(e)))
        self.cubesat.RGB=(100,100,50)
    
    # PCB Communication Functions with Fixes:
    
    def pcb_comms(self):
        """Main PCB communications routine."""
        self.debug_print("Yapping to the PCB now - D")
        gc.collect()
        image_count = 1
        image_dir = "/sd"

        # Check that the SD card is accessible and get the list of existing files.
        existing_files = self.get_existing_files(image_dir)
        if existing_files is None:
            self.debug_print("[ERROR] SD card not detected or cannot be accessed!")
            gc.collect()
            return

        gc.collect()
        self.debug_print(f"[DEBUG] Free memory before communication start: {gc.mem_free()} bytes")

        # Initialize communication objects.
        com1, fcb_comm = self.initialize_comms()
        if com1 is None or fcb_comm is None:
            return

        # Process communication cycles.
        self.process_communication(com1, fcb_comm, image_dir, existing_files, image_count)

        # Cleanup communication objects.
        self.cleanup_comms(com1, fcb_comm)

    def get_existing_files(self, image_dir):
        """Attempt to list files on the SD card. Returns a set of filenames or None on failure."""
        try:
            return set(os.listdir(image_dir))
        except OSError:
            return None

    def initialize_comms(self):
        """Initializes the communication objects."""
        try:
            # Lazy import of hardware-specific modules to defer heavy initialization.
            from board import TX, RX
            from easy_comms_circuit import EasyComms
            from FCB_class import FCBCommunicator

            com1 = EasyComms(TX, RX, baud_rate=9600)
            com1.start()
            fcb_comm = FCBCommunicator(com1)
            return com1, fcb_comm
        except Exception as e:
            self.debug_print(f"[ERROR] Failed to initialize communication: {str(e)}")
            return None, None

    def process_communication(self, com1, fcb_comm, image_dir, existing_files, image_count):
        """Runs the main communication loop."""
        while True:
            try:
                self.debug_print(f"[DEBUG] Free memory before cycle: {gc.mem_free()} bytes")
                # Read an overhead command (if any) – this may be used to drive logic.
                overhead_command = com1.overhead_read()

                # For our example, we assume a "chunk" command is desired.
                command = 'chunk'
                if command.lower() == 'chunk':
                    fcb_comm.send_command("chunk")
                    if fcb_comm.wait_for_acknowledgment():
                        time.sleep(1)  # Pause for stability.
                        gc.collect()
                        self.debug_print(f"[DEBUG] Free memory before data transfer: {gc.mem_free()} bytes")
                        # Get the next available image filename.
                        image_count = self.find_next_image_count(existing_files, image_count)
                        # Write the image data to SD card.
                        self.write_image(fcb_comm, image_dir, image_count)

                # For demonstration, we end the communication cycle after the chunk.
                command = 'end'
                if command.lower() == 'end':
                    fcb_comm.end_communication()

            except MemoryError:
                self.debug_print("[ERROR] MemoryError: Restarting communication cycle")
                gc.collect()
                continue  # Restart the cycle.
            except Exception as e:
                self.debug_print("[ERROR] PCB communication failed: " + traceback.format_exc())
                break  # Break out of the loop after logging the error.

    def find_next_image_count(self, existing_files, image_count):
        """Find the next available image filename based on the current set of files."""
        filename = f"inspireFly_Capture_{image_count}.jpg"
        while filename in existing_files:
            image_count += 1
            filename = f"inspireFly_Capture_{image_count}.jpg"
        return image_count

    def write_image(self, fcb_comm, image_dir, image_count):
        """Handles the image file writing process with safe allocation for each chunk."""
        img_file_path = f"{image_dir}/inspireFly_Capture_{image_count}.jpg"
        try:
            with open(img_file_path, "wb") as img_file:
                offset = 0
                while True:
                    # Force GC before each allocation attempt.
                    gc.collect()
                    # Use our safe chunk request to mitigate MemoryError.
                    jpg_bytes = self.safe_send_chunk_request(fcb_comm)
                    if jpg_bytes is None:
                        self.debug_print("[ERROR] Failed to allocate memory for chunk after retries.")
                        break  # Abort the transfer if allocation fails.
                    if not jpg_bytes:
                        # End-of-data condition.
                        break
                    img_file.write(jpg_bytes)
                    offset += len(jpg_bytes)
                    del jpg_bytes
                    if offset % 1024 == 0:
                        gc.collect()
                gc.collect()  # Final GC after the loop.
                self.debug_print(f"[INFO] Finished writing image. Data size: {offset} bytes")
        except OSError as e:
            self.debug_print(f"[ERROR] Writing to SD card failed: {str(e)}")

    def safe_send_chunk_request(self, fcb_comm, retries=3, delay=0.1):
        """
        Attempts to retrieve a data chunk from the PCB.
        If a MemoryError occurs (e.g., failing to allocate ~472 bytes), forces garbage collection
        and retries a few times before giving up.
        """
        for attempt in range(retries):
            try:
                return fcb_comm.send_chunk_request()
            except MemoryError:
                self.debug_print(f"[WARN] MemoryError during chunk request, retry {attempt+1}/{retries}.")
                gc.collect()
                time.sleep(delay)
        return None

    def cleanup_comms(self, com1, fcb_comm):
        """Closes communication objects and frees resources."""
        try:
            com1.close()
        except Exception:
            pass
        del com1, fcb_comm
        gc.collect()
        self.debug_print(f"[DEBUG] Free memory after cleanup: {gc.mem_free()} bytes")

    # ... Remaining methods of your class remain unchanged ...
    
    def overhead_send(self, msg):
        """Lightweight function to initialize UART and send overhead data."""
        try:
            from board import TX, RX
            from easy_comms_circuit import EasyComms

            com1 = EasyComms(TX, RX, baud_rate=9600)
#             com1.start()
            com1.overhead_send(msg)
            self.debug_print(f"[INFO] Overhead data sent: {msg}")
        except Exception as e:
            self.debug_print(f"[ERROR] Failed to send overhead data: {str(e)}")
        finally:
            if 'com1' in locals():
                com1.close()
