# MIT License
# Copyright (c) 2018-2019 Jetsonhacks

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import GPUtil
import psutil  # doc : https://psutil.readthedocs.io/en/latest/

fig = plt.figure(figsize=(6,4))
plt.subplots_adjust(top=0.85, bottom=0.30)
fig.set_facecolor('#F2F1F0')
fig.canvas.set_window_title('GPU CPU Activity Monitor')


# assume we only have one GPU (e.g. for my personal pc)
# Subplot for the GPU activity
gpuAx = plt.subplot2grid((2,1), (0,0), rowspan=1, colspan=1)
cpuAx = plt.subplot2grid((2,1), (1,0), rowspan=1, colspan=1)

# https://matplotlib.org/users/tight_layout_guide.html
plt.tight_layout(rect=[0.03, 0.05, 1, 0.95]) # [left, bottom, right, top]
#plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=None)

# For the GPU usage
gpuLineUsage, = gpuAx.plot([],[])
gpuLineUsage.set_label('GPU Usage')

# For the GPU memory
gpuLineMemory, = gpuAx.plot([],[])
gpuLineMemory.set_label('GPU Memory')

gpu_text_use = gpuAx.text(0, 0.0, "", size=10)
gpu_text_mem = gpuAx.text(0, 0.0, "", size=10)

# For cpu RAM
cpuLineUse, = cpuAx.plot([],[])
cpuLineUse.set_label('CPU Usage')

cpuLineRAM, = cpuAx.plot([],[])
cpuLineRAM.set_label('CPU RAM')

cpu_text_use = cpuAx.text(0, 0.0, "", size=10)
cpu_text_ram = cpuAx.text(0, 0.0, "", size=10)

# gives a single float value
#psutil.cpu_percent()
# gives an object with many fields
#psutil.virtual_memory()
# you can convert that object to a dictionary 
#dict(psutil.virtual_memory()._asdict())
# you can have the percentage of used RAM
#psutil.virtual_memory().percent
#79.2
# you can calculate percentage of available memory
#psutil.virtual_memory().available * 100 / psutil.virtual_memory().total
#20.8

# The line points in x,y list form
gpuy_list = deque([0]*240)
gpuy_list_mem = deque([0]*240)
cpuy_list = deque([0]*240)
cpuy_list_use = deque([0]*240)
gpux_list = deque(np.linspace(60,0,num=240))

fill_lines = 0
fill_lines_mem = 0

fill_lines_cpu = 0
fill_lines_cpu_use = 0

def initGraph():
    global gpuAx
    global gpuLineUsage
    global gpuLineMemory
    global fill_lines
    global fill_lines_mem

    global cpuAx
    global cpuLineRAM
    global cpuLineUse
    global fill_lines_cpu
    global fill_lines_cpu_use


    gpuAx.set_xlim(60, 0)
    gpuAx.set_ylim(-5, 105)
    gpuAx.set_title('GPU History')
    #gpuAx.set(xticklabels=[])
    gpuAx.set_ylabel('Percentage (%)')
    #gpuAx.set_xlabel('Seconds');
    gpuAx.grid(color='gray', linestyle='dotted', linewidth=1)
    gpuAx.legend(loc='upper left')

    gpuLineUsage.set_data([],[])
    gpuLineMemory.set_data([],[])

    fill_lines = gpuAx.fill_between(gpuLineUsage.get_xdata(),50,0)
    fill_lines_mem = gpuAx.fill_between(gpuLineUsage.get_xdata(),50,0)

    cpuAx.set_xlim(60, 0)
    cpuAx.set_ylim(-5, 105)
    cpuAx.set_title('CPU History')
    cpuAx.set_ylabel('Percentage (%)')
    cpuAx.set_xlabel('Seconds');
    cpuAx.grid(color='gray', linestyle='dotted', linewidth=1)
    cpuAx.legend(loc='upper left')

    cpuLineRAM.set_data([],[])
    cpuLineUse.set_data([],[])
    fill_lines_cpu = cpuAx.fill_between(cpuLineRAM.get_xdata(),50,0)
    fill_lines_cpu_use = cpuAx.fill_between(cpuLineUse.get_xdata(),50,0)

    return [gpuLineUsage] + [gpuLineMemory] + [fill_lines] + [fill_lines_mem] + [cpuLineRAM] + [fill_lines_cpu] + [cpuLineUse] + [fill_lines_cpu_use]

def updateGraph(frame):
    global fill_lines
    global fill_lines_mem
    global gpuy_list
    global gpuy_list_mem
    global gpux_list
    global gpuLineUsage
    global gpuLineMemory
    global gpuAx
    global gpu_text_mem, gpu_text_use

    global cpuAx
    global cpuLineRAM
    global cpuLineUse
    global cpuy_list
    global cpuy_list_use
    global fill_lines_cpu_use
    global fill_lines_cpu
    global cpu_text_use, cpu_text_ram

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
    #gpu_text_use.remove()
    #start = 1
    #if fileData >= 10:
    #    start = 2
    #gpu_text_use = gpuAx.text(start, fileData, str(int(fileData)), color=gpuLineUsage.get_color(), size=10, weight='heavy')

    gpuy_list_mem.popleft()
    fileData = gpu.memoryUsed * 100 /gpu.memoryTotal
    gpuy_list_mem.append(fileData)
    gpuLineMemory.set_data(gpux_list,gpuy_list_mem)

    gpu_text_mem.remove()
    start = 1
    if fileData >= 10:
        start = 2
    gpu_text_mem = gpuAx.text(start, fileData+5, str(int(fileData)), color=gpuLineMemory.get_color(), size=10, weight='heavy')


    fill_lines.remove()
    fill_lines = gpuAx.fill_between(gpux_list,0,gpuy_list, facecolor='cyan', alpha=0.50)

    fill_lines_mem.remove()
    fill_lines_mem = gpuAx.fill_between(gpux_list,0,gpuy_list_mem, facecolor='wheat', alpha=0.50)
 
    cpu_value = psutil.virtual_memory().percent
    cpuy_list.popleft()
    cpuy_list.append(cpu_value)
    cpuLineRAM.set_data(gpux_list,cpuy_list)

    cpu_text_ram.remove()
    start = 1
    if cpu_value >= 10:
        start = 2
    cpu_text_ram = cpuAx.text(start, cpu_value+5, str(int(cpu_value)), color=cpuLineRAM.get_color(), size=10, weight='heavy')

    cpu_value = psutil.cpu_percent()
    cpuy_list_use.popleft()
    cpuy_list_use.append(cpu_value)
    cpuLineUse.set_data(gpux_list,cpuy_list_use)

    fill_lines_cpu.remove()
    fill_lines_cpu = cpuAx.fill_between(gpux_list,0,cpuy_list, facecolor='wheat', alpha=0.50)

    fill_lines_cpu_use.remove()
    fill_lines_cpu_use = cpuAx.fill_between(gpux_list,0,cpuy_list_use, facecolor='cyan', alpha=0.50)

    return [gpuLineUsage] + [gpuLineMemory] + [fill_lines] + [fill_lines_mem] + [cpuLineRAM] + [fill_lines_cpu] + [cpuLineUse] + [fill_lines_cpu_use] + [gpu_text_mem,cpu_text_ram]


# Keep a reference to the FuncAnimation, so it does not get garbage collected
animation = FuncAnimation(fig, updateGraph, frames=200,
                    init_func=initGraph,  interval=250, blit=True)

plt.show()

