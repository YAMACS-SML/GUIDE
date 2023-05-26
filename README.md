# GUIDE
Yasara Plugin for QM calculations

GUIDE is a plugin that enables users to perform ORCA and MOPAC Quantum Mechanical (QM) calculations through YASARA, providing a graphical user interface (GUI) for running calculations typically performed via a command-line interface. The plugin was developed using Python programming language. To install the plugin user needs to install YASARA (Structure), ORCA (version 5.0 or letter), MOPAC (MOPAC2016) and Python (3.8 or higher) in the system. The exact installation process is mentioned below in chronological order.

1.	Download and install ORCA and MOPAC for your system. 
	ORCA:	https://orcaforum.kofo.mpg.de/app.php/portal 
	MOPAC:	http://openmopac.net/Download_MOPAC_Executable_Step2.html

2.	Download and install YASARA view suite (free) or YASARA structure suite from YASARA official page (http://www.yasara.org/downloads.htm).

3.	From the GitHub page https://github.com/YAMACS-SML/GUIDE download the Guide files
	a.	If you have YASARA View installed, download the file GUIDE_YASARA_view.py 
	b.	If you have Yasara Structure installed, download the file GUIDE_YASARA_structure.py
		(Unlike the YASARA view (free version), the YASARA Structure suite has some extra features like Energy minimization, Charge calculation, Fixing of atoms etc., allowing several advanced-level QM calculations using GUIDE)

4.	Place the .py file in the plg folder inside YASARA installation path (...Yasara/plg). 
	For more information, please watch the video https://github.com/YAMACS-SML/GUIDE/blob/main/video_tutorials/1_GUIDE_installation.mp4. 

5.	Launch the GUIDE plugin from the YASARA toolbar. 
	a.	The YASARA window will display the YASARA python path information.
	b.	A file named "module_command.txt" will be generated in the specific directory.
	c.	Additionally, the YASARA python path information will be written in the "module.txt" file located in the YASARA installation's "plg" folder.
	d.	The "module_command.txt" file will provide installation instructions for the required Python modules. Follow the instructions to install the necessary modules.
	For further details, refer to section 2.1 of the manual.

If you encounter an issue, please check the FAQs in the Wiki section. There may already be a solution to your problem!
