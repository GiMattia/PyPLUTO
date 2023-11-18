from .libraries import *

def savefig(filename = 'img.png', bbox = 'tight'):
    plt.savefig(filename, bbox_inches = bbox)

def show(block = True):
    plt.show(block = block)

