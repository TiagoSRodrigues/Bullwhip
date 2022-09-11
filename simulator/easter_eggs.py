import time
import math
from playsound import playsound
import simulation_configuration as sim_cfg
def print_start(LOGGING_LEVEL):
    if not sim_cfg.PRINT_LOGS_IN_TERMINAL:
        return
    else:
        print("\n ================================================ ")
        print( f"                Simulation Started ")
        print("\n ================================================ ")
        print(f"           Logging at level: {sim_cfg.LOGGING_LEVEL}:")
        if sim_cfg.DB_TYPE == 1:
            print("          Database:         MongoDB")
        if sim_cfg.DB_TYPE == 2:
            print("           Database:         Local files")
        if sim_cfg.SIMULATION_MODE == 1:
            print("           Simulation mode:  Traditional")
        if sim_cfg.SIMULATION_MODE == 3:
            print("           Simulation mode:  Blockchain")
            print(f"        Slowdown level:   {sim_cfg.TIME_SLOWDOWN}:")
        print("\n ================================================ ")


def print_days(days):
    if not sim_cfg.PRINT_LOGS_IN_TERMINAL:
        return
    else:
        print(f"\n               Days simulated: {days}\n ================================================ \n")


def print_actor(id,reorder):
    if not sim_cfg.PRINT_LOGS_IN_TERMINAL:
        return
    else:
       print("          actor",id, "Reorder _history:",reorder)



def print_after_simulation():
    if not sim_cfg.PRINT_LOGS_IN_TERMINAL:
        return
    else:
        print("\n\n ================================================ ")
        print("\n               Finishing simulation ...")
        print("\n ================================================ ")

def print_sucess():
    if not sim_cfg.PRINT_LOGS_IN_TERMINAL:
        return
    else:
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
    if not sim_cfg.PRINT_LOGS_IN_TERMINAL:
        return
    else:
        print_sucess()
        final_time = time.perf_counter()-start_time
        hr, min, sec = 0, 0, 0
        hr=math.floor(final_time/3600)
        min=math.floor((final_time - hr*3600)/60)
        sec=math.floor(final_time-(hr*3600+min*60))
        ms=round(final_time-(hr*3600+min*60+sec),2)

        print("Run in {}h {}m {}s {}ms \nFinished at {}".format(hr, min, sec, ms,
            time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())))
