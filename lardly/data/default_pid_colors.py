
default_pid_colors = {2212:'rgb(153,55,255)', # protons (purple)
                      13:'rgb(255,0,0)', # muons (red)
                      -13:'rgb(255,0,0)', # muons (red)
                      211:'rgb(255,128,255)',# pi+ (light magenta)
                      -211:'rgb(255,0,127)',# pi- (dark magenta/fusia)
                      22:'rgb(0,153,0)', # gamma (green)
                      11:'rgb(0,0,255)', # e+ (blue)
                      -11:'rgb(0,0,255)', # e-(blue)                
                      0:'rgb(0,0,0)'# other (black)
                      }

def get_pid_color( pid ):
    if pid not in default_pid_colors:
        print("pid not recognized: ",pid)
        return default_pid_colors[0]
    else:
        return default_pid_colors[pid]
