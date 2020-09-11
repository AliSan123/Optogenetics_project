![]()
<img src="https://github.com/AliSan123/Optogenetics_project/blob/master/Py2Pulse%20Logo.PNG" data-canonical-src="https://github.com/AliSan123/Optogenetics_project/blob/master/Py2Pulse%20Logo.PNG" width="200"  />
# Py2Pulse: A program for the parameter optimisation of a 2-photon optogenetics laser
Optogenetics studies have gained significant popularity in neuroscience in recent years, enabling researchers to examine neural circuits and control their responses.  Many studies have demonstrated improvements to the optical setup; but there is insufficient evidence on the optimal 2P laser parameters which evoke maximal photocurrents in opsin-transfected cells without photodamage.  In order to control the deployment of ultrafast laser pulses and find the optimal photostimulation parameters, this report presents a program called Py2Pulse written in Python 3, Arduino and QT. Py2Pulse is designed to be modular. Two Hardware Abstraction Layer (HAL) modules control their respective devices independently, enabling device-interchangeability and virtual testing. There is also a data analysis module containing functions for the optimisation algorithms. The modules are integrated into the Graphical User Interface (GUI) module. The interface enables researchers to set the parameters, control the lasing and upload results for analysis without requiring coding. Currently, the project is in the testing phase, requiring additional testing of the modules, especially the laser module when the laboratory is accessible. The completion of testing and deployment into production was limited by the laboratory being inaccessible due the COVID-19 pandemic. 
# Installation and use
Clone the repository and execute the MainApp.py script to begin the program. The data to be uploaded is saved in the example folder for testing.
The requirements.txt file contains an exhaustive list of libraries required, but note that not all of them were actually used. Many were in the same virtual environment used for other projects/ in the development of the program.
# Current phase
This project is in the testing phase. Acess to the laboratory was not allowed due to the COVID-19 pandemic and therefore the program was testing as far as possible remotely. Next steps towards deployment would be to test the Coerent module on the laser followed by all other modules and finally the system itself on the cells.
# Licencing
This is an open-source project, but any codes or theory utilised in other projects should be referenced.
