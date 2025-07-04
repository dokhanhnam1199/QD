import os
import glob
from omegaconf import OmegaConf
import matplotlib.pyplot as plt
import seaborn as sns  # Add this import

def filter_traceback(stdout_str):
    if "Traceback" in stdout_str:
        return "error"
    return ""

def read_bd_values_from_stdout(folder, bd_list, bd_step):
    bd_arrays = {bd: [] for bd in bd_list}
    for stdout_filepath in sorted(glob.glob(os.path.join(folder, "*.txt_stdout.txt"))):
        with open(stdout_filepath, 'r') as f:
            stdout_str = f.read()
        traceback_msg = filter_traceback(stdout_str)
        if traceback_msg == '':
            try:
                lines = stdout_str.strip().split('\n')
                l = len(bd_list)
                for i, bd in enumerate(bd_list):
                    val = float(lines[-l + i])
                    bd_arrays[bd].append(val)
            except Exception as e:
                print(f"Error parsing {stdout_filepath}: {e}")
        else:
            print(f"Error in {stdout_filepath}: {traceback_msg}")
    return bd_arrays

if __name__ == "__main__":
    # Load bd_list and bd_step from config.yaml
    config = OmegaConf.load("cfg/config.yaml")
    bd_list = config.bd_list
    bd_step = config.bd_step
    folder = "outputs/main/hsevo-qd_bpp_online_2025-07-02_12-45-34" 

    # Create output directory for distributions
    dist_folder = os.path.join("bd_distribution", os.path.basename(folder))
    os.makedirs(dist_folder, exist_ok=True)

    bd_arrays = read_bd_values_from_stdout(folder, bd_list, bd_step)
    for bd in bd_list:
        plt.figure()
        sns.kdeplot(bd_arrays[bd], fill=True)
        plt.title(f"Distribution of {bd}")
        plt.xlabel(f"{bd} value")
        plt.ylabel("Density")
        plt.grid(True)
        plt.savefig(os.path.join(dist_folder, f"{bd}_kde.png"))
        plt.close()
    print(f"Plots saved as PNG files in {dist_folder}.")