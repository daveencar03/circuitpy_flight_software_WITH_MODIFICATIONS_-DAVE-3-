# 
# send_command = 40
# 
# total_packets = 456
# 
# 
# send_message = str(send_command.to_bytes(1, 'big') + total_packets.to_bytes(2, 'big'))
# print(send_message)
# print("Sending: ", send_message[2:-1])
# 
# print("----------")
# 
# num = b'\x16'
# print(int.from_bytes(num, 'big'))
# 
# print("-----------")
# string = "K4KDJ"
# stringBytes = bytearray(string, "utf-8")
# print(stringBytes)

tip = (5-1.25)/0.005
print(tip)