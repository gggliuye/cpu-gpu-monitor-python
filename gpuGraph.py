# MIT License
# Copyright (c) 2018-2019 Jetsonhacks

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import GPUtil

fig = plt.figure(figsize=(6,2))
plt.subplots_adjust(top=0.85, bottom=0.30)
fig.set_facecolor('#F2F1F0')
fig.canvas.set_window_title('GPU Activity Monitor')

# assume we only have one GPU (e.g. for my personal pc)
# Subplot for the GPU activity
gpuAx = plt.subplot2grid((1,1), (0,0), rowspan=2, colspan=1)

# For the GPU usage
gpuLineUsage, = gpuAx.plot([],[])
gpuLineUsage.set_label('GPU Usage')

# For the GPU memory
gpuLineMemory, = gpuAx.plot([],[])
gpuLineMemory.set_label('GPU Memory')

# The line points in x,y list form
gpuy_list = deque([0]*240)
gpuy_list_mem = deque([0]*240)
gpux_list = deque(np.linspace(60,0,num=240))

fill_lines = 0
fill_lines_mem = 0

def initGraph():
    global gpuAx
    global gpuLineUsage
    global gpuLineMemory
    global fill_lines
    global fill_lines_mem


    gpuAx.set_xlim(60, 0)
    gpuAx.set_ylim(-5, 105)
    gpuAx.set_title('GPU History')
    gpuAx.set_ylabel('Percentage (%)')
    gpuAx.set_xlabel('Seconds');
    gpuAx.grid(color='gray', linestyle='dotted', linewidth=1)
    gpuAx.legend(loc='upper left')

    gpuLineUsage.set_data([],[])
    gpuLineMemory.set_data([],[])
    fill_lines = gpuAx.fill_between(gpuLineUsage.get_xdata(),50,0)
    fill_lines_mem = gpuAx.fill_between(gpuLineUsage.get_xdata(),50,0)

    return [gpuLineUsage] + [gpuLineMemory] + [fill_lines] + [fill_lines_mem]

def updateGraph(frame):
    global fill_lines
    global fill_lines_mem
    global gpuy_list
    global gpuy_list_mem
    global gpux_list
    global gpuLineUsage
    global gpuLineMemory
    global gpuAx

    GPUs = GPUtil.getGPUs()
    #GPUavailability = GPUtil.getAvailability(GPUs)
    
    
    gpu = GPUs[0]
    #print(gpu.load, gpu.memoryUsed, gpu.memoryTotal, gpu.memoryFree)

    # Now draw the GPU usage
    # The GPU load is stored as a percentage * 10, e.g 256 = 25.6%

    gpuy_list.popleft()
    fileData = gpu.load * 100
    gpuy_list.append(fileData)
    gpuLineUsage.set_data(gpux_list,gpuy_list)

    gpuy_list_mem.popleft()
    fileData = gpu.memoryUsed * 100 /gpu.memoryTotal
    gpuy_list_mem.append(fileData)
    gpuLineMemory.set_data(gpux_list,gpuy_list_mem)

    fill_lines.remove()
    fill_lines = gpuAx.fill_between(gpux_list,0,gpuy_list, facecolor='cyan', alpha=0.50)

    fill_lines_mem.remove()
    fill_lines_mem = gpuAx.fill_between(gpux_list,0,gpuy_list_mem, facecolor='wheat', alpha=0.50)

    return [gpuLineUsage] + [gpuLineMemory] + [fill_lines] + [fill_lines_mem]


# Keep a reference to the FuncAnimation, so it does not get garbage collected
animation = FuncAnimation(fig, updateGraph, frames=200,
                    init_func=initGraph,  interval=250, blit=True)

plt.show()


