import zmq
import csv
import time
from pathlib import Path
import numpy as np

def asdasd(port=5556):
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect(f"tcp://localhost:{port}")
    subscriber.setsockopt_string(zmq.SUBSCRIBE, "emg_data")

    # Publisher to send commands to pygame
    publisher = context.socket(zmq.PUB)
    publisher.bind(f"tcp://*:{5558}")
    
    print("ready")
    
    # Initializations
    data = []
    rms1 = np.array([])
    rms2 = np.array([])
    baseline1 = 0
    baseline2 = 0
    rms1_mean = np.array([])
    rms2_mean = np.array([])
    rms1_std = np.array([])
    rms2_std = np.array([])
    calibration = False
    time_jump = time.time()
    time_sneak = time.time()
    
    # Parameters to vary
    buffersize = 300           # Baseline calculated over {buffersize} values 
    windowsize = 20            # Window of how many raw samples end up in RMS (must not exceed buffersize)
    window_stats = 20          # Window of how many RMS samples end up in mean & std calculations 
    timedelay = 1            # Time delay in which another command can not be triggered
    num_std = 4                # Number of standard deviations before threshold

    
    # loop to listen to subscriber
    while True:
        # Read messages one by one until there are none left
        num_messages = 0
        while True:
            try:
                _, message = subscriber.recv_string(flags=zmq.NOBLOCK).split()
                timestamp, sensor_1, sensor_2 = message.split(",")
                data += [[float(timestamp), float(sensor_1), float(sensor_2)] ]
                num_messages += 1
                
                # Flush the data to the file after each write
            except zmq.Again:
                # No more messages in the queue
                break
            
        np_data = np.array(data)


        ## CALCULATE RMS VALUES
        
        # Calculate rms values using adaptive threshold over the last {buffersize} samples      
        if (np_data.shape[0] > buffersize):
            
            # Calculate baseline as mean of the last {buffersize} values
            baseline1 = np.mean( np_data[-buffersize:,1] )
            baseline2 = np.mean( np_data[-buffersize:,2] )
     
            # Subtract baseline for zero centering & do absolute value
            abs_val1 = abs(np_data[-windowsize:,1] - baseline1)
            abs_val2 = abs(np_data[-windowsize:,2] - baseline2)
            
            # RMS of jumping & sneaking    
            rms1 = np.append( rms1, np.sqrt(1/windowsize * np.sum(abs_val1 * abs_val1)) )
            rms2 = np.append( rms2, np.sqrt(1/windowsize * np.sum(abs_val2 * abs_val2)) )
            calibration = True
        ## !!! Output rms1/2 values on serial monitor !!!  
            
            
        ## CALCULATE RMS STATISTICS
        
        if calibration == True:
            
            #print("calibration done")
            # Calculate mean & std for threshold detection (using the last {window_stats} samples)
            if (rms1.shape[0] >= window_stats): 
                # Calculate mean over the last {window_stats} RMS samples
                rms1_mean = np.append(rms1_mean, np.mean(rms1[-window_stats:]))
                rms2_mean = np.append(rms2_mean, np.mean(rms2[-window_stats:]))
            
                # Calculate std over the last {window_stats} RMS samples 
                rms1_std = np.append(rms1_std, np.std(rms1[-window_stats:]))
                rms2_std = np.append(rms2_std, np.std(rms2[-window_stats:]))
            
            # Calculate mean & std using the last values (if length < window_stats, used at the beginning with fewer values)
            elif (rms1.shape[0] >= 1 and rms1.shape[0] <= window_stats):
                rms1_mean = np.append(rms1_mean, np.mean(rms1[:]))
                rms2_mean = np.append(rms2_mean, np.mean(rms2[:]))
                
                # Calculate std over the last {window_stats} RMS samples 
                rms1_std = np.append(rms1_std, np.std(rms1[:]))
                rms2_std = np.append(rms2_std, np.std(rms2[:]))
            
        
            ## DETECT THRESHOLD CROSSING 
            # Detect jumping
            if (rms1[-1] > (rms1_mean[-1] + num_std * rms1_std[-1])) and (time.time() - time_jump) >= timedelay :
                print("emg_spike right")
                publisher.send_string(f"emg_spike right")       # Send "jump" command to game via publisher
                time_jump = time.time()                         # Start timer to not send another threshold crossing before {timedelay}
                
            # Detect sneaking
            if (rms2[-1] > (rms2_mean[-1] + num_std * rms2_std[-1])) and (time.time() - time_sneak) >= timedelay:
                print("emg_spike left")
                publisher.send_string(f"emg_spike left")        # Send "sneak" command to game via publisher
                time_sneak = time.time()                        # Start timer to not send another threshold crossing before {timedelay}
            
        # Implemented:
        # - Calculate RMS values 
        # - Thresholding mit RMS mean und RMS std 
        # - Output triggern
        # - Delay after 
        
        # Todo:
        # - Does output triggering work?
        # - Show RMS data live in serial monitor
        # - Vary parameters to see effect 
        time.sleep(0.01)
        
 
if __name__ == "__main__":
    asdasd()
