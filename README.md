# **JEliOS**  
### **A Horror-Themed Handheld Gaming Environment**  
JEliOS is a custom desktop prototype designed with handheld gaming systems in mind. Built with Python and Pygame, JEliOS combines a retro-inspired gaming interface with an underlying horror narrative that gradually reveals itself through system interactions.  
The project explores interactive storytelling, persistent system states, custom interface design, and the use of unexpected events to turn an ordinary gaming environment into something unsettling.  
**JEliOS is currently a runnable application prototype, not (yet) a standalone bootable operating system.**  
## **Technologies**  
- Python  
- Pygame  
- Linux / Fedora  
- JSON for persistent system state  
- NumPy for experimental image-processing functionality  
## **Features**  
### **Boot Sequences and Persistent Events**  
JEliOS tracks system usage and changes certain startup sequences based on previous interactions.  
- First launch: A seven-second static/glitch sequence featuring the message GET ME OUT.  
- Fifth launch: An altered sequence featuring the message It wasn't your imagination... please help.  
- Other launches: Standard JEliOS logo sequence.  
- Persistent boot counter and interaction tracking.  
- System state stored locally in JSON.  
### **Main Interface**  
The main menu provides access to:  
- Emulators  
- Settings  
- Creator  
- Past Creator  
- Power Off  
** **  
### **Settings and Accessibility**  
The settings interface includes display customization and accessibility options.  
- Brightness adjustment (0–100%, in 5% increments).  
- Colorblind modes:  
  - Deuteranopia  
  - Protanopia  
  - Tritanopia  
- Monochrome display.  
- Extra Retro display mode.  
- CRT scanline effects.  
Brightness settings are saved between sessions.  
### **Characters and Interactive Storytelling**  
Aelita is an important part of the JEliOS experience, appearing during selected boot sequences and Creator-related interactions.  
Past Creator introduces additional narrative interactions and tracks visits through persistent system state.  
The horror elements are designed to develop through repeated use rather than relying entirely on traditional jumpscares.  
## **Installation and Running**  
### **Requirements**  
- Linux environment (developed and tested on Fedora).  
- Python 3.  
- Pygame.  
- NumPy for applicable display functionality.  
### **Setup**  
1. Open a terminal in the project directory.  
2. Install dependencies if necessary:  
sudo dnf install python3 python3-pip  
python3 -m pip install --user pygame numpy  
   
If Fedora reports that the Python environment is externally managed, use a virtual environment:  
   
python3 -m venv .venv  
source .venv/bin/activate  
pip install pygame numpy  
   
3. Launch JEliOS:  
python3 jelios.py  
** **  
## **Persistent Data**  
JEliOS stores application state locally:  
~/.config/jelios/state.json  
   
This file maintains information such as boot counts and interaction history.  
   
To reset the first-boot sequence for testing:  
rm ~/.config/jelios/state.json  
## **Development Status**  
JEliOS is an ongoing independent development project.  
Current development focuses on expanding interface functionality, accessibility options, interactive storytelling, and the overall handheld experience.  
Some narrative elements and planned features remain under development.  
**Developer:** Jerrica K. Godwin  
An independent project exploring software development, interface design, accessibility, persistent state management, and interactive horror storytelling.  
   
   
