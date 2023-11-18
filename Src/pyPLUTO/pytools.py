from .libraries import *

def savefig(filename = 'img.png', bbox = 'tight'):
    warning_message = """
    pyPLUTO.savefig is deprecated. 
    Please call savefig from the Image class instead"""
    warnings.warn(warning_message, DeprecationWarning)
    plt.savefig(filename, bbox_inches = bbox)

def show(block = True):
    plt.show(block = block)

