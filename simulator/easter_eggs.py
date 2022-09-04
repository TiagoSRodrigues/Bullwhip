import time
import math
from playsound import playsound

def print_start(LOGGING_LEVEL):
        print("\n ============================================================ \n        \
  Simulation Started with logging at level: " + LOGGING_LEVEL+
                "\n ============================================================\n")

def print_sucess():
        print("\n\n\
    ███████╗██╗   ██╗ ██████╗███████╗███████╗███████╗ ██████╗   ██╗ ██╗ ██╗ \n\
    ██╔════╝██║   ██║██╔════╝██╔════╝██╔════╝██╔════╝██╔═══██╗  ██║ ██║ ██║ \n\
    ███████╗██║   ██║██║     █████╗  ███████╗███████╗██║   ██║  ██║ ██║ ██║ \n\
    ╚════██║██║   ██║██║     ██╔══╝  ╚════██║╚════██║██║   ██║  ╚═╝ ╚═╝ ╚═╝ \n\
    ███████║╚██████╔╝╚██████╗███████╗███████║███████║╚██████╔╝  ██╗ ██╗ ██╗ \n\
    ╚══════╝ ╚═════╝  ╚═════╝╚══════╝╚══════╝╚══════╝ ╚═════╝   ╚═╝ ╚═╝ ╚═╝ \n\
                                                                            \n")


def play_final_sound():
    path=r"N:\\TESE\Bullwhip\data\audio\super_mario_stage_clear.mp3"
    try:
        playsound(path)
    except:
        playsound(path)

def play_error_sound():
    path="N:\\TESE\\Bullwhip\\data\\audio\\super_mario_dies.mp3"
    try:
        playsound(path)
    except:
        playsound(path)
        

def final_prints(start_time):
    print_sucess()
    final_time = time.perf_counter()-start_time
    hr, min, sec = 0, 0, 0
    hr=math.floor(final_time/3600)
    min=math.floor((final_time - hr*3600)/60)
    sec=math.floor(final_time-(hr*3600+min*60))
    ms=round(final_time-(hr*3600+min*60+sec),2)

    print("Run in {}h {}m {}s {}ms \nFinished at {}".format(hr, min, sec, ms,
          time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())))
