import os
import subprocess
import re
import sys
import webbrowser
import bs4, requests
from tkinter import *
from tkinter import filedialog
import customtkinter
from threading import Thread
from tkinter.messagebox import askyesno, showinfo

steam_folder = None
steam_paths = {
    "stplugin": None,
    "config_depotcache": None,
    "depotcache": None, 
    "stui": None,
    "stats": None
}
select_steam_path_flg = False


def get_game_name(game_id):
    try:
        url = f"https://store.steampowered.com/app/{game_id}/"
        response = requests.get(url)
        bs = bs4.BeautifulSoup(response.text, "lxml")
        return bs.find("div", id="appHubAppName").text
    except:
        return "-"


def show_message(title, message):
    showinfo(title=title, message=message)


def update_log(text, color="white"):
    files_text.configure(state="normal")
    files_text.tag_config(color, foreground=color)
    files_text.insert(customtkinter.END, text, color)
    files_text.see("end")
    files_text.configure(state="disabled")


def delete_game():
    if not select_steam_path_flg:
        show_message("Error", "Select steam folder!")
        return
        
    game_id = entry_id.get()
    if not game_id.isdigit():
        update_log("Invalid ID...\n\n", "red")
        return
        
    file_count = 0
    game_name = get_game_name(game_id)
    update_log(f"AppID: {game_id}\nDeleting files:\n", "yellow")
    pattern = rf"{game_id[0:-1]}\d\D+"
    
    for path_key, path in steam_paths.items():
        if path is None:
            continue
            
        for file in os.listdir(path):
            if path_key == "stats":
                match = f"_{game_id}_" in file
            else:
                match = re.match(pattern, file)
                
            if match and file:
                try:
                    full_path = os.path.join(path, file).replace("/", '\\')
                    update_log(f"{full_path}\n", "cyan")
                    os.remove(os.path.join(path, file))
                    file_count += 1
                except Exception as e:
                    update_log(f"Error deleting {full_path}: {str(e)}\n", "red")
    
    if file_count > 0:
        update_log(f"\nGame «{game_name}» has been removed.\n\n", "green")
    else:
        update_log(f"\nThe AppID: {game_id} files were not found.\n\n", "yellow")


def delete_all_games():
    if not select_steam_path_flg:
        show_message("Error", "Select steam folder!")
        return
        
    update_log("Deletion files...\n", "yellow")
    
    files_to_delete = []
    for path in steam_paths.values():
        if path is None:
            continue
            
        for file in os.listdir(path):
            if file.endswith((".st", ".manifest", ".bin")):
                files_to_delete.append(os.path.join(path, file))
    
    if askyesno(title="Delete all games?", message="Do you want to delete ALL games?"):
        for file in files_to_delete:
            try:
                os.remove(file)
                update_log(f"{file.replace('/', '\\')}\n", "cyan")
            except Exception as e:
                update_log(f"Error deleting {file}: {str(e)}\n", "red")
        update_log("The games have been successfully deleted!\n\n", "green")
    else:
        update_log("File deletion aborted...\n\n", "red")


def delete_steamtools():
    if not select_steam_path_flg:
        show_message("Error", "Select steam folder!")
        return
        
    os.system("taskkill /f /im Steamtools.exe")
    
    stui_path = steam_paths["stui"]
    try:
        files_deleted = 0
        
        if os.path.exists(stui_path):
            for file in os.listdir(stui_path):
                full_path = os.path.join(stui_path, file)
                os.remove(full_path)
                update_log(f"Deleted: {full_path}\n", "cyan")
                files_deleted += 1
        
        if files_deleted > 0:
            update_log("The Steamtools have been successfully deleted!\n\n", "green")
        else:
            update_log("Steamtools has already been deleted.\n\n", "yellow")
    except Exception as e:
        update_log(f"Error: {str(e)}\n", "red")


def ask_delete_steamtools():
    update_log("Delete Steamtools?\n", "yellow")
    if askyesno(title="Delete Steamtools?", message="Do you want to delete Steamtools?"):
        delete_steamtools()
    else:
        update_log("Steamtools deletion aborted...\n\n", "red")


def browse_steam_folder():
    global steam_folder, select_steam_path_flg, steam_paths
    
    folder_selected = filedialog.askdirectory()
    if not folder_selected:
        return
        
    if "config" not in os.listdir(folder_selected):
        show_message("Error", "Select valid steam folder!")
        return
        
    steam_folder = folder_selected
    steam_paths = {
        "stplugin": os.path.join(steam_folder, "config", "stplug-in"),
        "config_depotcache": os.path.join(steam_folder, "config", "depotcache"),
        "depotcache": os.path.join(steam_folder, "depotcache"),
        "stui": os.path.join(steam_folder, "config", "stUI"),
        "stats": os.path.join(steam_folder, "config", "StatsExport")
    }
    
    select_steam_path_flg = True
    
    entry_path.configure(state="normal")
    entry_path.delete(0, "end")
    entry_path.insert("1", steam_folder)
    entry_path.configure(state="disabled")


def restart_steam():
    if not select_steam_path_flg:
        show_message("Error", "Select steam folder!")
        return
        
    steam_exe = "Steam.exe"
    steam_path = os.path.join(steam_folder, steam_exe)
    
    update_log("Restarting Steam\n\n", "yellow")
    
    try:
        subprocess.run(["taskkill", "/f", "/im", steam_exe], check=True)
    except:
        pass
    
    try:
        if os.path.exists(steam_path):
            subprocess.Popen(steam_path, shell=True)
            update_log("Steam has been restarted.\n\n", "green")
        else:
            update_log("Steam.exe not found in the selected folder.\n", "red")
    except Exception as e:
        update_log(f"Error: {str(e)}\n", "red")


def setup_ui():
    global root, entry_path, files_text, entry_id
    
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("blue")
    
    root = customtkinter.CTk()
    root.title("Games Remover")
    root.geometry("800x750")
    root.resizable(False, False)
    root.configure(fg_color="#1e1e2d")
    
    # Header section
    header_frame = customtkinter.CTkFrame(
        root,
        width=760,
        height=80,
        fg_color="#292938",
        corner_radius=12
    )
    header_frame.place(x=20, y=20)
    header_frame.grid_propagate(False)
    
    title = customtkinter.CTkLabel(
        header_frame,
        text="Games Remover",
        font=("Inter", 28, "bold"),
        text_color="#6366f1"
    )
    title.place(relx=0.05, rely=0.5, anchor="w")

    # Steam folder selection
    folder_frame = customtkinter.CTkFrame(
        root,
        width=760,
        height=60,
        fg_color="#292938",
        corner_radius=12
    )
    folder_frame.place(x=20, y=120)
    folder_frame.grid_propagate(False)
    
    entry_path = customtkinter.CTkEntry(
        folder_frame,
        placeholder_text="Select Steam folder",
        width=640,
        height=40,
        corner_radius=8,
        border_color="#363645",
        fg_color="#1e1e2d"
    )
    entry_path.place(relx=0.03, rely=0.5, anchor="w")
    entry_path.configure(state="disabled")
    
    browse_button = customtkinter.CTkButton(
        folder_frame,
        text="Browse",
        width=80,
        height=40,
        corner_radius=8,
        fg_color="#6366f1",
        hover_color="#5355cc",
        command=browse_steam_folder
    )
    browse_button.place(relx=0.97, rely=0.5, anchor="e")
    
    # Game control section
    game_frame = customtkinter.CTkFrame(
        root,
        width=760,
        height=140,
        fg_color="#292938",
        corner_radius=12
    )
    game_frame.place(x=20, y=200)
    game_frame.grid_propagate(False)
    
    entry_id = customtkinter.CTkEntry(
        game_frame,
        placeholder_text="Enter game ID",
        width=720,
        height=45,
        corner_radius=8,
        border_color="#363645",
        fg_color="#1e1e2d"
    )
    entry_id.place(relx=0.5, rely=0.2, anchor="center")
    
    button_frame = customtkinter.CTkFrame(
        game_frame,
        fg_color="transparent"
    )
    button_frame.place(relx=0.5, rely=0.7, anchor="center")
    
    delete_button = customtkinter.CTkButton(
        button_frame,
        text="Delete Game",
        width=200,
        height=45,
        corner_radius=8,
        fg_color="#6366f1",
        hover_color="#5355cc",
        command=delete_game
    )
    delete_button.grid(row=0, column=0, padx=10)
    
    delete_all_button = customtkinter.CTkButton(
        button_frame,
        text="Delete All Games",
        width=200,
        height=45,
        corner_radius=8,
        fg_color="#dc2626",
        hover_color="#b91c1c",
        command=delete_all_games
    )
    delete_all_button.grid(row=0, column=1, padx=10)
    
    # Progress section
    progress_frame = customtkinter.CTkFrame(
        root,
        width=760,
        height=350,
        fg_color="#292938",
        corner_radius=12
    )
    progress_frame.place(x=20, y=360)
    progress_frame.grid_propagate(False)
    
    progress_label = customtkinter.CTkLabel(
        progress_frame,
        text="Progress",
        font=("Inter", 16, "bold"),
        text_color="#6366f1"
    )
    progress_label.place(relx=0.03, rely=0.1)
    
    files_text = customtkinter.CTkTextbox(
        progress_frame,
        width=720,
        height=270,
        corner_radius=8,
        fg_color="#1e1e2d",
        border_color="#363645",
        border_width=1,
        font=("Inter", 12)
    )
    files_text.place(relx=0.5, rely=0.6, anchor="center")
    files_text.configure(state="disabled")


if __name__ == "__main__":
    setup_ui()
    root.mainloop()