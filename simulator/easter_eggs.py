def print_start(Logging_level):
        print("\n ============================================================ \n        \
  Simulation Started with logging at level: " + Logging_level+                    
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
    from playsound import playsound

    path="N:\\TESE\\Bullwhip\\data\\audio\\super_mario_stage_clear.mp3"
    playsound(path)
        
def play_error_sound():
    from playsound import playsound

    path="N:\\TESE\\Bullwhip\\data\\audio\\super_mario_dies.mp3"
    playsound(path)
