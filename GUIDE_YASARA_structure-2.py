# YASARA PLUGIN FOR DFT
# TOPIC:       SML
# TITLE:       SML
# AUTHOR:      A.sarkar # VERSION 3.6
# LICENSE:     Non-Commercial
# DATE:        09.05.2024
# This is a YASARA plugin to be placed in the /plg subdirectory
# Go to www.yasara.org/plugins for documentation and downloads

# YASARA menu entry
"""
MainMenu: GUIDE
  PullDownMenu : QM Calculation
    CustomWindow: QM Calculation
      Width: 600
      Height: 400
      TextInput:   X= 20,Y=50,Text="*Please insert the path of working folder",Width=150,Chars=150
      TextInput:   X= 20,Y=140,Text="*Please give a name of your project",Width=150,Chars=150
      List: X=360,Y=100,Text="METHODS"
        Width=200,Height=175,MultipleSelections=No
       Options=2, Text="ORCA"
                  Text="MOPAC"
      Button:    X=542,Y=348,Text="OK"
    Request: 
"""
class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

#importing essential modules
import yasara 
import os
import sys
import platform

macrotarget = str((yasara.selection[0].text[0]))
nameobj = str((yasara.selection[0].text[1]))
nameobj= str(nameobj)+'_obj1'
print(nameobj )

def charge_calculation():
   tempomcr= os.path.join(macrotarget,"test.mcr")
   temp_mcr_contetnt='''
JoinObj all,1
SelectAtom Ru Ge As Nb Mo Tc Rh Sb W Fr Es Cf Bk Cm Am Np Pa Ac Rn At Po Bi Ho Sb3 Ru1 Ge1 Tc Sb Te Pm Ta Re Os Ir Bs Fm
x()= nameatom selected
listatom()= listatom selected
len = count listatom
if len > 0
  DuplicateObj 1 
  RemoveObj 2
  for i in listatom()
    SwapAtom Atom (i),Dummy,UpdateBonds=Yes,UpdateHyd=Yes 
  
  chargeinfo= ChargeObj all
  for k=1 to len
    if x(k) == 'Ru' or x(k) == 'Ru1' or x(k) == 'Ho' or x(k) == 'Fm'
      chargeinfo = (chargeinfo)+3
      chargeinfo = (0+chargeinfo)
    elif x(k) == 'Ge' or x(k) == 'Ge1' or x(k) == 'Te' or x(k) == 'Os' or x(k) == 'Ir'
      chargeinfo = (chargeinfo)+2
      chargeinfo = (0+chargeinfo)
    elif x(k) == 'As' or x(k) == 'As1' or x(k) == 'Pm' or x(k) == 'Re' or x(k) == 'Bs'
      chargeinfo = (chargeinfo)+3
      chargeinfo = (0+chargeinfo)
    elif x(k) == 'Nb' or x(k) == 'Nb1'
      chargeinfo = (chargeinfo)+5
      chargeinfo = (0+chargeinfo)
    elif x(k) == 'Mo' or x(k) == 'Mo1'
      chargeinfo = (chargeinfo)+4 
      chargeinfo = (0+chargeinfo)
    elif x(k) == 'Tc' or x(k) == 'Tc1'
      chargeinfo = (chargeinfo)+4 
      chargeinfo = (0+chargeinfo)
    elif x(k) == 'Rh' or x(k) == 'Rh1'
      chargeinfo = (chargeinfo)+3 
      chargeinfo = (0+chargeinfo)
    elif x(k) == 'Sb' or x(k) == 'Sb1'
      chargeinfo = (chargeinfo)+3 
      chargeinfo = (0+chargeinfo)
    elif x(k) == 'w' or x(k) == 'w1'
      chargeinfo = (chargeinfo)+2 
      chargeinfo = (0+chargeinfo)
    elif x(k) == 'Fr' or x(k) == 'Fr1'
      chargeinfo = (chargeinfo)+1 
      chargeinfo = (0+chargeinfo)
    elif x(k) == 'Es' or x(k) == 'Es1'
      chargeinfo = (chargeinfo)+3 
      chargeinfo = (0+chargeinfo)
    elif x(k) == 'Cf' or x(k) == 'Cf1'
      chargeinfo = (chargeinfo)+3 
      chargeinfo = (0+chargeinfo)
    elif x(k) == 'Bk' or x(k) == 'Bk1'
      chargeinfo = (chargeinfo)+3 
      chargeinfo = (0+chargeinfo)
    elif x(k) == 'Cm' or x(k) == 'Cm1'
      chargeinfo = (chargeinfo)+3 
      chargeinfo = (0+chargeinfo)
    elif x(k) == 'Am' or x(k) == 'Am1'
      chargeinfo = (chargeinfo)+2 
      chargeinfo = (0+chargeinfo)
    elif x(k) == 'Np' or x(k) == 'Np1'
      chargeinfo = (chargeinfo)+3 
      chargeinfo = (0+chargeinfo)
    elif x(k) == 'Pa' or x(k) == 'Pa1' or  x(k) == 'Sb' or  x(k) == 'Ta'
      chargeinfo = (chargeinfo)+5 
      chargeinfo = (0+chargeinfo)
    elif x(k) == 'Ac' or x(k) == 'Ac1'
      chargeinfo = (chargeinfo)+3 
      chargeinfo = (0+chargeinfo)
    elif x(k) == 'At' or x(k) == 'At1'
      chargeinfo = (chargeinfo)-1
      chargeinfo = (0+chargeinfo)
    elif x(k) == 'Po' or x(k) == 'Po1'
      chargeinfo = (chargeinfo)+2 
      chargeinfo = (0+chargeinfo)
    elif x(k) == 'Bi' or x(k) == 'Bi1'
      chargeinfo = (chargeinfo)+3 
      chargeinfo = (0+chargeinfo)
    elif x(k) == 'Tc' or x(k) == 'Tc1'
      chargeinfo = (chargeinfo)+7 
      chargeinfo = (0+chargeinfo)
    else
      print ("No exotic elements found")
  AddObj 2
  DelObj 1 
  NumberObj 2,First=1
    
else
  chargeinfo= ChargeObj all  
  chargeinfo = (0+chargeinfo)
  
PropObj all,(chargeinfo)
prop= PropObj all
prop=(0+prop)
print (prop)

'''
   tempwrite= open(tempomcr,'w+')
   tempwrite.write(temp_mcr_contetnt)
   tempwrite.close()
   yasara.run("PlayMacro "+tempomcr)
   prop=yasara.run("PropObj all")
   os.remove(tempomcr)
   return prop

def energy_minimization():
   energy_minimizatin_mcr= os.path.join(macrotarget,"energy_minimization.mcr")
   energy_mcr_content= '''
SelectAtom Ru Ge As Nb Mo Tc Rh Sb W Fr Es Cf Bk Cm Am Np Pa Ac Rn At Po Bi Ho Sb3 Ru1 Ge1 Tc Sb Te Pm Ta Re Os Ir Bs Fm
x()= nameatom selected
listatom()= listatom selected
len = count listatom
if len > 0
  DuplicateObj 2 
  RemoveObj 1
  for i in listatom()
    SwapAtom Atom (i),Dummy,UpdateBonds=Yes,UpdateHyd=Yes 
    FixAtom (i)
  Experiment Minimization
    Convergence 0.25
  Experiment On
  Wait ExpEnd 
  DelObj  SimCell
  FreeAtom all
  SelectAtom all Obj 2 and not element Du 
  DelAtom All obj 2 and not selected 
  AddObj 1
  SelectAtom Ru Ge As Nb Mo Tc Rh Sb W Fr Es Cf Bk Cm Am Np Pa Ac Rn At Po Bi Ho Sb3 Ru1 Ge1 Tc Sb Te Pm Ta Re Os Ir Bs Fm Obj 1 
  DelAtom all obj 1 and not selected  
  JoinObj all,2 
  NumberObj all,1
else
  Experiment Minimization
    Convergence 0.25
  Experiment On
  Wait ExpEnd 
  DelObj  SimCell
'''
   k= open(energy_minimizatin_mcr,'w+')
   k.write(energy_mcr_content)
   k.close()
   yasara.run("PlayMacro "+energy_minimizatin_mcr)
   os.remove(energy_minimizatin_mcr)

if macrotarget == '':
  yasara.ShowMessage("GUIDE must need a directory") 
  yasara.plugin.end() 
else:
  print('ok')
mod=(platform.system())
if mod== 'Linux' or mod == 'Darwin':
  mod=str(1)
  print('Linux')
else:
  mod=str(2)
  print('Windows')
yasarapath=os.getcwd()
if os.path.isfile(yasarapath+'/'+'module.txt'):
  print('++++')
else:
  modulelist =\
    yasara.ShowWin("Custom","modules",400,250,
     "Text", 20, 50, "Do you want to install essential modules?",
     "RadioButtons",2,1,
                    20, 100,"yes",
                    200,100,"no",
     "Button",      150,200," O K")
  attach= open((yasarapath)+'/'+'module.txt','w+')
  attach.write((str(modulelist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
  attach.close()  
  f = open((yasarapath)+'/'+'module.txt', "r")
  content= f.readlines()
  a = str((content[0]).strip('\n'))   
  
  if a == str(1):
    print(sys.executable)
    pypath= sys.executable
    modulepath= open(yasarapath+'/'+'module.txt','w')
    modulepath.write(str(pypath).replace('python.exe','').replace('pythonw.exe',''))
    modulepath.close()
    rmodule=open(yasarapath+'/'+'module.txt')
    pmodule= rmodule.readlines()
    moduleroad= str((pmodule[0]).strip('\n'))
    print(moduleroad)
    if mod == str(2):
      os.chdir(moduleroad)    
      md= open(moduleroad+'/'+'module_command.txt','w+')
      md.write("Step1: Please check your python version. Open a terminal in this folder and write the following command\n'python --version'\nStep2: If the python version is 3.8 or lower, please use the following commands to install the modules\n\n\nPIP INSTALLATION:\n'curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py'\n'python get-pip.py'\n\n\nPANDAS INSTALLATION\n'pip install pandas'\n\n\n NUMPY INSTALLATION:\n'pip install numpy'\n\n\nMATPLOTLIB INSTALLATION:\n'pip install matplotlib'\n\n\nPYTHON-CSV installation:\n'pip install python-csv'\n\n\nPYTEST-SHUTIL INSTALLATION:\n'pip install pytest-shutil'\n\n\nIf the python version is 3.10, please use the following commands to install the modules\n\n\nPIP INSTALLATION:\n'python -m pip install pip==22.2.2'\n\n\nPANDAS INSTALLATION\n'py -m pip install pandas'\n\n\n NUMPY INSTALLATION:\n'py -m pip install numpy'\n\n\nMATPLOTLIB INSTALLATION:\n'py -m pip install matplotlib'\n\n\nPYTHON-CSV installation:\n'py -m pip install python-csv'\n\n\nPYTEST-SHUTIL INSTALLATION:\n'py -m pip install pytest-shutil")
      md.close()   

      md_macro= open(macrotarget+'/'+'module_command.txt','w+')
      md_macro.write("Step1: Please check your python version. Open a terminal in this folder and write the following command\n'python --version'\nStep2: If the python version is 3.8 or lower, please use the following commands to install the modules\n\n\nPIP INSTALLATION:\n'curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py'\n'python get-pip.py'\n\n\nPANDAS INSTALLATION\n'pip install pandas'\n\n\n NUMPY INSTALLATION:\n'pip install numpy'\n\n\nMATPLOTLIB INSTALLATION:\n'pip install matplotlib'\n\n\nPYTHON-CSV installation:\n'pip install python-csv'\n\n\nPYTEST-SHUTIL INSTALLATION:\n'pip install pytest-shutil'\n\n\nIf the python version is 3.10, please use the following commands to install the modules\n\n\nPIP INSTALLATION:\n'python -m pip install pip==22.2.2'\n\n\nPANDAS INSTALLATION\n'py -m pip install pandas'\n\n\n NUMPY INSTALLATION:\n'py -m pip install numpy'\n\n\nMATPLOTLIB INSTALLATION:\n'py -m pip install matplotlib'\n\n\nPYTHON-CSV installation:\n'py -m pip install python-csv'\n\n\nPYTEST-SHUTIL INSTALLATION:\n'py -m pip install pytest-shutil'")
      md_macro.close()  

      yasara.ShowMessage("Please go to "+str(moduleroad)+" and follow the steps as given in module_command.txt")
      yasara.run("wait continuebutton")

    else:
      md_macro= open(macrotarget+'/'+'module_command.txt','w+')
      md_macro.write("Step1: Please check your python version. Open a terminal in this folder and write the following command\n'python --version'\nStep2: If the python version is 3.8 or lower, please use the following commands to install the modules\n\n\nPIP INSTALLATION:\n'curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py'\n'python get-pip.py'\n\n\nPANDAS INSTALLATION\n'pip install pandas'\n\n\n NUMPY INSTALLATION:\n'pip install numpy'\n\n\nMATPLOTLIB INSTALLATION:\n'pip install matplotlib'\n\n\nPYTHON-CSV installation:\n'pip install python-csv'\n\n\nPYTEST-SHUTIL INSTALLATION:\n'pip install pytest-shutil'\n\n\nIf the python version is 3.10, please use the following commands to install the modules\n\n\nPIP INSTALLATION:\n'python -m pip install pip==22.2.2'\n\n\nPANDAS INSTALLATION\n'py -m pip install pandas'\n\n\n NUMPY INSTALLATION:\n'py -m pip install numpy'\n\n\nMATPLOTLIB INSTALLATION:\n'py -m pip install matplotlib'\n\n\nPYTHON-CSV installation:\n'py -m pip install python-csv'\n\n\nPYTEST-SHUTIL INSTALLATION:\n'py -m pip install pytest-shutil'")
      md_macro.close()  

      yasara.ShowMessage("Please go to "+str(macrotarget)+" and follow the steps as given in module_command.txt")
      yasara.run("wait continuebutton") 
    #for python 3.8  
    #os.system('curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py')
    #os.system('python get-pip.py')
    #os.system('pip install pandas')
    #os.system('pip install numpy')   
    #os.system('pip install matplotlib')    
    #os.system('pip install python-csv')    
    #os.system('pip install pytest-shutil')
    
    #for 3.10
    #os.system('python -m pip install pip==22.2.2')
    #os.system('py -m pip install pandas')
    #os.system('py -m pip install numpy')   
    #os.system('py -m pip install matplotlib')    
    #os.system('py -m pip install python-csv')    
    #os.system('py -m pip install pytest-shutil') 
  else:
    print('++')  
  

import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
import shutil




#storing the path and method information in variables

methods= str((yasara.selection[0].list))
method= (methods.strip('[]'))
method= (method.replace("'", "").replace(",",""))

print(method)
 
plgpath=os.getcwd()
#sentence= macrotarget
#a=(sentence.count('/'))
#print(a)
#a= str(a)


print(mod)  

print(plgpath)

##storing orca path
if mod == str(2):
 mopacfile='mopac.exe'
else:
 mopacfile="mopac"

if method == 'ORCA':
  if os.path.isfile(plgpath+'/'+'orcapath.txt') :

    fk = open(plgpath+'/'+'orcapath.txt', "r")
    path= fk.readlines()
    orcap= str((path[0]).strip('\n'))
    if mod == str(1):
      orca=str((orcap)+'/'+'orca')
      print(orca) 
    else:
      orca=str((orcap)+"\orca.exe")    
 
  else:
    pathlist =\
      yasara.ShowWin("Custom","ORCA-PATH",400,250,
      "TextInput", 20, 48,"Please insert the path of orca",150,150,   
      "Button",      150,200," O K")
    k=open(plgpath+'/'+'orcapath.txt','w+')
    k.write((str(pathlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    k.close()
    fk = open(plgpath+'/'+'orcapath.txt', "r")
    path= fk.readlines()
    orcap= str((path[0]).strip('\n'))
    orca=str((orcap)+'/'+'orca')
    print(orca)
       
##storing mopac path
elif method == 'MOPAC':
  if os.path.isfile(plgpath+'/'+'mopacpath.txt') :

    fk = open(plgpath+'/'+'mopacpath.txt', "r")
    path= fk.readlines()
    mopacpath= str((path[0]).strip('\n'))
    mopac= os.path.join(mopacpath,mopacfile)
    #mopac=str((mopac)+'/'+mopacfile)
     
  else:
    pathlist =\
      yasara.ShowWin("Custom","MOPAC-PATH",400,250,
      "TextInput", 20, 48,"Please insert the path of MOPAC",150,150,   
      "Button",      150,200," O K")
    k=open(plgpath+'/'+'mopacpath.txt','w+')
    k.write((str(pathlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    k.close()
    fk = open(plgpath+'/'+'mopacpath.txt', "r")
    path= fk.readlines()
    mopacpath= str((path[0]).strip('\n'))
    mopac= os.path.join(mopacpath,mopacfile)

     
else:
  yasara.ShowMessage("GUIDE must need a QM method") 
  yasara.plugin.end()  
  
###charge_calculation function

  
####OPTIONS FOR ORCA  
if method == 'ORCA':
  yasara.ShowMessage('Make sure that ORCA is installed and path is provided in ..yasara/plg/orcapath.txt')
  #yasara.run("LabelAll 'Make sure that ORCA is installed and path is provided in orcapath.txt',Height=0.9,Color=Black,X=0,Y=19,Z=65")
  calculationlist=\
    yasara.ShowWin("Custom","CALCULATION",600,400,
    "Text", 20, 48, "Calculation type",
    "RadioButtons",10,1,
                   20, 65,"Single point",
                   20, 105,"Geometry optimization",
                   20, 155,"Transition state",
                   20, 205,"Vibrational frequencies",
                   20, 255,"UV-Vis spectroscopy",
                   20, 300,"HOMO-LUMO energy gap",
                   200, 65,"None of these",
                   20, 350,"Constraining QM",
                   200,155,"Multilevel DFT",
                   250,205,"Fukui function",
    "Button",      542,348," O K")    


  cal=open(macrotarget+'/'+'calculation.txt','w+')
  cal.write((str(calculationlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
  cal.close()
  methos_cal = open(macrotarget+'/'+'calculation.txt', "r")
  caltype= methos_cal.readlines()
  if os.path.getsize(macrotarget+'/'+'calculation.txt') == 0:
    yasara.ShowMessage("QM calculation failed, select a specific method") 
    os.remove(macrotarget+'/'+'calculation.txt')
    yasara.plugin.end() 
  else:
    print('ok') 

  methodology= str((caltype[0]).strip('\n')) 
 
  #yasara.run("LabelAll 'Make sure that ORCA is installed and path is provided in orcapath.txt',Height=0.9,Color=Black,X=0,Y=19,Z=65")
  #yasara.run('UnlabelAll')
####MOPAC options
else :
  yasara.ShowMessage('Make sure that MOPAC is installed and path is provided in ..yasara/plg/mopacpath.txt')
  calculationlist=\
    yasara.ShowWin("Custom","CALCULATION",600,400,
    "Text", 20, 48, "Theory",
    "RadioButtons",7,1,
                   20, 65,"AM1",
                   20, 105,"PM3",
                   20, 145,"PM6",
                   20, 185,"PM7",
                   160, 65,"RM1",
                   160, 105,"MNDO",
                   160, 145,"MNDOD",
    "Text", 20, 239, "HF type:",
    "RadioButtons",2,1,
                   20, 265,"RHF",
                   120, 265,"UHF",
    "List",        350,70,"Calculation type",220,140,"No",                 
                   4,    "Single-point",
                          "HOMO-LUMO",
                          "Equilibrium-geometry",
                          "Import-job",
    "Button",      542,348," O K")   

  cal=open(macrotarget+'/'+'calculation.txt','w+')
  cal.write((str(calculationlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
  cal.close()

  calcline= open(macrotarget+'/'+'calculation.txt')
  for line in calcline:
      if "0" in line:
         yasara.ShowMessage("GUIDE must need a specific QM method for MOPAC")
         yasara.plugin.end()
  methos_cal = open(macrotarget+'/'+'calculation.txt', "r")
  caltype= methos_cal.readlines()
  theory=str((caltype[0]).strip('\n')) 
  hf=str((caltype[1]).strip('\n'))
  methodology= str((caltype[3]).strip('\n'))  
  

  print("check")
  ## HF
  if hf == str(1):
    hf= "RHF"
  else:
    hf= "UHF"
  print(hf)
  ##Theory
  if theory ==str(1):
    theory= 'AM1'
  elif theory == str(2):
    theory= 'PM3'
  elif theory == str(3):
    theory = 'PM6'
  elif theory == str(4):
    theory= 'PM7'
  elif theory == str(5):
    theory= 'RM1'
  elif theory == str(6):
    theory = 'MNDO'
  else:
    theory= 'MNDOD'
  
  print(theory)  
  #yasara.run('UnlabelAll')
  ###methodology:
  if methodology == 'Single-point':
    firstkey='AUX 1SCF LARGE CHARGE='
    secondkey='NOOPT'
    thirdkey='PDBOUT THREADS=1'

  elif methodology == 'Equilibrium-geometry':
    firstkey='AUX LARGE CHARGE='
    thirdkey='PDBOUT THREADS=1'
    secondkey='BONDS XYZ PRNT=2 PRTXYZ FLEPO PRECISE GNORM=0.0'

  elif methodology == 'HOMO-LUMO':
    firstkey='1SCF GRAPH VECTORS ALLVEC BONDS CHARGE='
    thirdkey='PDBOUT THREADS=1'
    secondkey='EIGS'    
  elif methodology == 'Import-job':
    nonelist =\
      yasara.ShowWin("Custom","PROVIDE YOUR OWN FILE",400,250,
      "TextInput", 20, 48,"Insert the name of the file with extension(.mop)",150,150,   
      "Button",      150,200," O K")
    nonek=open(macrotarget+'/'+'file.txt','w+')
    nonek.write((str(nonelist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    nonek.close()
    none_fk = open(macrotarget+'/'+'file.txt', "r")
    ownfileinfo= none_fk.readlines()
    ownfile= str((ownfileinfo[0]).strip('\n'))    
  
  else:
    methodology = 'HOMO-LUMO'
 

#### ORCA INPUT FILE FORMATION 
if method == 'ORCA' and methodology == str(7):
  trjlist =\
    yasara.ShowWin("Custom","Create own QM project",400,250,
     "Text", 20, 50, "Do you want default functional,basis set?",
     "RadioButtons",2,1,
                    20, 100,"yes",
                    200,100,"no",
     "Button",      150,200," O K")
  attach= open((macrotarget)+'/'+'ownfileorca.txt','w+')
  attach.write((str(trjlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
  attach.close()  
  f = open((macrotarget)+'/'+'ownfileorca.txt', "r")
  content= f.readlines()
  uqm = str((content[0]).strip('\n'))  
  if uqm == str(2):
    keylist =\
      yasara.ShowWin("Custom","ORCA-kEYWORDS",400,250,
      "TextInput", 20, 48,"Please insert the functional keyword",150,150,   
      "TextInput", 20, 110,"Please insert the basis keyword",150,150,
      "Button",      150,200," O K")
    key=open(macrotarget+'/'+'keyword.txt','w+')
    key.write((str(keylist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    key.close()
    if os.path.getsize(macrotarget+'/'+'keyword.txt') == 0:
      yasara.ShowMessage("QM calculation failed, please insert a correct functional and basis set information. Restart the process") 
      os.remove(macrotarget+'/'+'keyword.txt')
      yasara.plugin.end() 
    else:
      print('ok')   
    fkey = open(macrotarget+'/'+'keyword.txt', "r")
    keyword= fkey.readlines()
    functional= str((keyword[0]).strip('\n'))
    basis=str((keyword[1]).strip('\n'))
    print(functional)
    print(basis)     



###################################################################################################
###all the below section will come under transition state for orca  
if method == 'ORCA' and methodology == str(3) :
  ##Building a reactant molecule by user
  yasara.ShowMessage("Please build your reactant molecule and then click continue")
  yasara.run("wait continuebutton")
  yasara.run("BFactorAtom all,0")
  yasara.run('ForceField AMBER03,SetPar=Yes')
###charge of the reactant molecule
  chargeinfo=charge_calculation()#yasara.run('ChargeObj all')
  cfmod=open(macrotarget+'/'+str(nameobj)+'charge.log','w')
  cfmod.write(str(chargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']','').replace(',','\n'))
  cfmod.close()
  if os.path.getsize(macrotarget+'/'+str(nameobj)+'charge.log') == 0:
    yasara.ShowMessage("Charge calculation failed, restart the process") 
    os.remove(macrotarget+'/'+str(nameobj)+'charge.log')
    yasara.plugin.end() 
  else:
    print('ok')   

  chargef= open(macrotarget+'/'+str(nameobj)+'charge.log','r')
  chargeall=chargef.readlines()
  charge=float((chargeall[0]).strip('\n'))
  charge=round(charge)
  print(charge)
  alllist =\
    yasara.ShowWin("Custom","INFORMATION",400,250,
    "NumberInput", 20, 88,"Charge",str(charge),-1000,1000,
    "NumberInput", 180, 88,"Multiplicity",1,1,1000,
    "Button",      150,200," O K")  
##counting the object present in the yasara window
  rcharge=open(macrotarget+'/'+str(nameobj)+'charge.log','w+')
  rcharge.write((str(alllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
  rcharge.close()
  if os.path.getsize(macrotarget+'/'+str(nameobj)+'charge.log') == 0:
    yasara.ShowMessage("Charge calculation failed, restart the process") 
    os.remove(macrotarget+'/'+str(nameobj)+'charge.log')
    yasara.plugin.end() 
  else:
    print('ok')   

  react_charge = open(macrotarget+'/'+str(nameobj)+'charge.log', "r")
  reactinfo= react_charge.readlines()
  reactcharge= str((reactinfo[0]).strip('\n'))    
  reactmultiplicity= str((reactinfo[1]).strip('\n')) 

  obj=yasara.run("CountObj all")
  deltext= open(macrotarget+'/'+'deltext.txt','w')
  deltext.write(str(obj).replace('object(s) match the selection.','').replace('[','').replace(']',''))
  deltext.close()
  g = open((macrotarget)+'/'+'deltext.txt', "r")
  content = g.readlines()
  noobj=str((content[0]).strip('\n'))
  g.close()
  os.remove((macrotarget)+'/'+'deltext.txt')
  if noobj == 0 :
    yasara.ShowMessage("Please build at least one molecule or see the terminal")
    print("C'mon, we can not calculate TS for a blank space !!!")
    yasara.plugin.end()
  
  else:
    yasara.run('JoinObj all,1')
    noatom=yasara.run("CountAtom all")
    atomtext= open(macrotarget+'/'+'atomnotext.txt','w')
    atomtext.write(str(noatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
    atomtext.close()
    a = open((macrotarget)+'/'+'atomnotext.txt', 'r')
    atomcontent = a.readlines()
    atom=str((atomcontent[0]).strip('\n'))
    atom=int(atom)
    a.close()
    os.remove((macrotarget)+'/'+'atomnotext.txt')
    i=0
    for i in range (0,atom):
      
        yasara.run("BFactorAtom "+str(i+1)+","+str(i+1))
        bfactor=yasara.run("BFactorAtom "+str(i+1))
        if i == 0:
          val= open(macrotarget+'/'+'bfactor.txt','w')
          val.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
          val.close()
        else:
          valread=open(macrotarget+'/'+'bfactor.txt','r')
          value=valread.readlines()
          valread.close()
          rewrite=open(macrotarget+'/'+'bfactor.txt','w')
          rewrite.writelines(value)
          rewrite.write('\n')
          rewrite.write(str(bfactor).replace('[','').replace(']',''))
          rewrite.close()
        
        i=i+1
##Saving the xyz file of the reactant
  yasara.run("SaveXYZ 1,"+str(macrotarget)+'/'+"reactant.xyz,transform=Yes") 
##modifying the reactant.xyz file without hamparing the main file
  reactantxyz=os.path.join(macrotarget,'reactant.xyz')
  bfactortxt=os.path.join(macrotarget,'bfactor.txt')
  reactanttxt=os.path.join((macrotarget),'reactant.txt')
  reactantfiletertxt=os.path.join(macrotarget,'reactant_filter.txt')
  os.chdir(macrotarget)
  time.sleep(3)
  with open(reactantxyz, 'r') as fin:
      data = fin.read().splitlines(True)
  with open(reactanttxt, 'w') as fout:
      fout.writelines(data[2:]) 
      fout.close()
   
##concatination of reactant xyz info with its b-factor value   
  combine =[]

  with open(bfactortxt) as xh:
    with open(reactanttxt) as yh:
      with open(reactantfiletertxt,"w") as zh:
         #Read first file
         xlines = xh.readlines()
         #Read second file
         ylines = yh.readlines()
         #Combine content of both lists
         #combine = list(zip(ylines,xlines))
         #Write to third file
         for i in range(len(xlines)):
            line = ylines[i].strip('\n') + '    ' + xlines[i]
            zh.write(line)
#os.remove((macrotarget)+'/'+'reactant.txt')
   
   

if method == 'ORCA' and methodology == str(1) or methodology == str(2) or methodology == str(3) or methodology == str(4) or methodology ==str(5) or methodology ==str(6) or methodology ==str(7) and uqm == str(1) or methodology ==str(8) or methodology ==str(10):
  resultlist =\
    yasara.ShowWin("Custom","Functional and Basis set",600,400,
    "Text", 20, 48, "Functional set:",
    "RadioButtons",14,1,
                   20, 65,"B3LYP",
                   20, 105,"BLYP",
                   20, 155,"HF",
                   20, 205,"MP2",
                   20, 255,"CCSD",
                   20, 305,"PBE",
                   140, 65,"revPBE",
                   140, 105,"PBE0",
                   140, 155,"B97-3C",
                   140, 205,"M06L Grid6",
                   140, 255,"XTB",
                   140, 305,"wB97X-D3",
                   20, 350,"None",
                   140, 350,"PM3",
    "List",        360,70,"Basis set",190,128,"No",                 
                   16,    "DEF2-SVP",
                          "DEF2-TZVP",
                          "DEF2-QZVP",
                          "DEF2-TZVPP",
                          "DEF2-QZVPP",
                          "DEF2-TZVPPD",
                          "ma-def2-SVP",
                          "ma-def2-TZVP",
                          "6-31G(d)",
                          "cc-pVDZ",
                          "cc-pVTZ",
                          "cc-pVQZ",
                          "aug-cc-pVDZ",
                          "aug-cc-pVTZ",
                          "aug-cc-pVQZ",
                          "none",
    "Button",      542,348," O K")

  pathYasara = os.getcwd()
  temp= open((pathYasara)+'/'+'ytempo.ini', 'w+')
  temp.write((str(resultlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
  temp.write('\n')
  temp.close()
  ycalcline= open((pathYasara)+'/'+'ytempo.ini')
  for line in ycalcline:
      if "0" in line:
         yasara.ShowMessage("GUIDE must need a specific functional and basis set information for ORCA")
         yasara.plugin.end()
      else:
         print('ok')


#the tempo.ini contains the input file information
  if os.path.getsize((pathYasara)+'/'+'ytempo.ini') == 1:
    yasara.ShowMessage("QM calculation failed, please insert a correct functional and basis set information. Restart the process") 
    os.remove((pathYasara)+'/'+'ytempo.ini')
    yasara.plugin.end() 
  else:
    print('ok')  
  f = open(pathYasara+'/'+'ytempo.ini', "r")
  content= f.readlines()
  functional= str((content[0]).strip('\n'))
  nothing=str((content[1]).strip('\n'))
  basis=str((content[2]).strip('\n'))      
  #yasara.run('UnlabelAll')
    
     
  if functional == str(1):
    functional="B3LYP"
  elif functional == str(2):
    functional="BLYP"
  elif functional == str(3):
    functional="HF"
  elif functional == str(4):
    functional="MP2"
  elif functional == str(5):
    functional="CCSD"
  elif functional == str(6):
    functional="PBE"
  elif functional == str(7):
    functional="revPBE"
  elif functional == str(8):
    functional="PBE0"
  elif functional == str(9):
    functional="B97-3C"
  elif functional == str(10):
    functional="M06L Grid6"
  elif functional == str(11):
    functional="XTB"
    basis= ''
  elif functional == str(14):
    functional="RHF PM3"
    basis= ''
  elif functional == str(13):
    keylist =\
      yasara.ShowWin("Custom","ORCA-kEYWORDS",400,250,
      "TextInput", 20, 48,"Please insert the functional keyword",150,150,   
      "TextInput", 20, 110,"Please insert the basis keyword",150,150,
      "Button",      150,200," O K")
    key=open(macrotarget+'/'+'keyword.txt','w+')
    key.write((str(keylist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    key.close()
    if os.path.getsize(macrotarget+'/'+'keyword.txt') == 0:
      yasara.ShowMessage("QM calculation failed, please insert a correct functional and basis set information. Restart the process") 
      os.remove(macrotarget+'/'+'keyword.txt')
      yasara.plugin.end() 
    else:
      print('ok')   
    fkey = open(macrotarget+'/'+'keyword.txt', "r")
    keyword= fkey.readlines()
    functional= str((keyword[0]).strip('\n'))
    basis=str((keyword[1]).strip('\n'))
    print(functional)
    print(basis)   
  
  else:
    functional="wB97X-D3"

  print(functional)
  print(basis)

else:
  print('qui')
#####QM/QM2###functional and basis set for qm atoms
if method == 'ORCA' and methodology == str(9) :
  resultlist =\
    yasara.ShowWin("Custom","QM atoms",600,400,
    "Text", 20, 48, "Functional set:",
    "RadioButtons",14,1,
                   20, 65,"B3LYP",
                   20, 105,"BLYP",
                   20, 155,"HF",
                   20, 205,"MP2",
                   20, 255,"CCSD",
                   20, 305,"PBE",
                   140, 65,"revPBE",
                   140, 105,"PBE0",
                   140, 155,"B97-3C",
                   140, 205,"M06L Grid6",
                   140, 255,"XTB",
                   140, 305,"wB97X-D3",
                   20, 350,"None",
                   140, 350,"PM3",
    "List",        360,70,"Basis set",190,128,"No",                 
                   16,    "DEF2-SVP",
                          "DEF2-TZVP",
                          "DEF2-QZVP",
                          "DEF2-TZVPP",
                          "DEF2-QZVPP",
                          "DEF2-TZVPPD",
                          "ma-def2-SVP",
                          "ma-def2-TZVP",
                          "6-31G(d)",
                          "cc-pVDZ",
                          "cc-pVTZ",
                          "cc-pVQZ",
                          "aug-cc-pVDZ",
                          "aug-cc-pVTZ",
                          "aug-cc-pVQZ",
                          "none",
    "Button",      542,348," O K")

  pathYasara = os.getcwd()
  temp= open((pathYasara)+'/'+'ytempo.ini', 'w+')
  temp.write((str(resultlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
  temp.write('\n')
  temp.close()

  ycalcline= open((pathYasara)+'/'+'ytempo.ini')
  for line in ycalcline:
      if "0" in line:
         yasara.ShowMessage("GUIDE must need a specific functional and basis set information for ORCA")
         yasara.plugin.end()
      else :
         print('ok')
#the tempo.ini contains the input file information
  if os.path.getsize((pathYasara)+'/'+'ytempo.ini') == 1:
    yasara.ShowMessage("QM calculation failed, please insert a correct functional and basis set information. Restart the process") 
    os.remove((pathYasara)+'/'+'ytempo.ini')
    yasara.plugin.end() 
  else:
    print('ok')  

  f = open(pathYasara+'/'+'ytempo.ini', "r")
  content= f.readlines()
  functional= str((content[0]).strip('\n'))
  nothing=str((content[1]).strip('\n'))
  basis=str((content[2]).strip('\n'))      

    
     
  if functional == str(1):
    functional="B3LYP"
  elif functional == str(2):
    functional="BLYP"
  elif functional == str(3):
    functional="HF"
  elif functional == str(4):
    functional="MP2"
  elif functional == str(5):
    functional="CCSD"
  elif functional == str(6):
    functional="PBE"
  elif functional == str(7):
    functional="revPBE"
  elif functional == str(8):
    functional="PBE0"
  elif functional == str(9):
    functional="B97-3C"
  elif functional == str(10):
    functional="M06L Grid6"
  elif functional == str(11):
    functional="XTB"
    basis= ''
  elif functional == str(14):
    functional="RHF PM3"
    basis= ''
  elif functional == str(13):
    keylist =\
      yasara.ShowWin("Custom","ORCA-kEYWORDS",400,250,
      "TextInput", 20, 48,"Please insert the functional keyword",150,150,   
      "TextInput", 20, 110,"Please insert the basis keyword",150,150,
      "Button",      150,200," O K")
    key=open(macrotarget+'/'+'keyword.txt','w+')
    key.write((str(keylist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    key.close()
    if os.path.getsize(macrotarget+'/'+'keyword.txt') == 0:
      yasara.ShowMessage("QM calculation failed, please insert a correct functional and basis set information. Restart the process") 
      os.remove(macrotarget+'/'+'keyword.txt')
      yasara.plugin.end() 
    else:
      print('ok')  

    fkey = open(macrotarget+'/'+'keyword.txt', "r")
    keyword= fkey.readlines()
    functional= str((keyword[0]).strip('\n'))
    basis=str((keyword[1]).strip('\n'))
    print(functional)
    print(basis)   
  
  else:
    functional="wB97X-D3"

  print(functional)
  print(basis)
###functional and basis set for other atoms 
  qm2resultlist =\
    yasara.ShowWin("Custom","QM2 atoms",600,400,
    "Text", 20, 48, "Functional set:",
    "RadioButtons",14,1,
                   20, 65,"B3LYP",
                   20, 105,"BLYP",
                   20, 155,"HF",
                   20, 205,"MP2",
                   20, 255,"CCSD",
                   20, 305,"PBE",
                   140, 65,"revPBE",
                   140, 105,"PBE0",
                   140, 155,"B97-3C",
                   140, 205,"M06L Grid6",
                   140, 255,"XTB",
                   140, 305,"wB97X-D3",
                   20, 350,"None",
                   140, 350,"PM3",
    "List",        360,70,"Basis set",190,128,"No",                 
                   16,    "DEF2-SVP",
                          "DEF2-TZVP",
                          "DEF2-QZVP",
                          "DEF2-TZVPP",
                          "DEF2-QZVPP",
                          "DEF2-TZVPPD",
                          "ma-def2-SVP",
                          "ma-def2-TZVP",
                          "6-31G(d)",
                          "cc-pVDZ",
                          "cc-pVTZ",
                          "cc-pVQZ",
                          "aug-cc-pVDZ",
                          "aug-cc-pVTZ",
                          "aug-cc-pVQZ",
                          "none",
    "Button",      542,348," O K")

  pathYasara = os.getcwd()
  tempqm2= open((pathYasara)+'/'+'tempo_qm2.ini', 'w+')
  tempqm2.write((str(qm2resultlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
  tempqm2.write('\n')
  tempqm2.close()
  ycalcline= open((pathYasara)+'/'+'tempo_qm2.ini')
  for line in ycalcline:
      if "0" in line:
         yasara.ShowMessage("GUIDE must need a specific functional and basis set information for ORCA")
         yasara.plugin.end()
      else:
         print('ok')

  if os.path.getsize((pathYasara)+'/'+'tempo_qm2.ini') == 1:
    yasara.ShowMessage("QM calculation failed, please insert a correct functional and basis set information. Restart the process") 
    os.remove((pathYasara)+'/'+'tempo_qm2.ini')
    yasara.plugin.end() 
  else:
    print('ok')  

#the tempo.ini contains the input file information
  fqm2 = open(pathYasara+'/'+'tempo_qm2.ini', "r")
  contentqm2= fqm2.readlines()
  functionalqm2= str((contentqm2[0]).strip('\n'))
  nothingqm2=str((contentqm2[1]).strip('\n'))
  basisqm2=str((contentqm2[2]).strip('\n'))      

    
     
  if functionalqm2 == str(1):
    functionalqm2="B3LYP"
  elif functionalqm2 == str(2):
    functionalqm2="BLYP"
  elif functionalqm2 == str(3):
    functionalqm2="HF"
  elif functionalqm2 == str(4):
    functionalqm2="MP2"
  elif functionalqm2 == str(5):
    functionalqm2="CCSD"
  elif functionalqm2 == str(6):
    functionalqm2="PBE"
  elif functionalqm2 == str(7):
    functionalqm2="revPBE"
  elif functionalqm2 == str(8):
    functionalqm2="PBE0"
  elif functionalqm2 == str(9):
    functionalqm2="B97-3C"
  elif functionalqm2 == str(10):
    functionalqm2="M06L Grid6"
  elif functionalqm2 == str(11):
    functionalqm2="XTB"
    basisqm2= ''
  elif functionalqm2 == str(14):
    functionalqm2="RHF PM3"
    basisqm2= ''
  elif functionalqm2 == str(13):
    qmkeylist =\
      yasara.ShowWin("Custom","ORCA-kEYWORDS",400,250,
      "TextInput", 20, 48,"Please insert the functional keyword",150,150,   
      "TextInput", 20, 110,"Please insert the basis keyword",150,150,
      "Button",      150,200," O K")
    keyqm2=open(macrotarget+'/'+'keywordqm2.txt','w+')
    keyqm2.write((str(qmkeylist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    keyqm2.close()
    if os.path.getsize(macrotarget+'/'+'keywordqm2.txt') == 0:
      yasara.ShowMessage("QM calculation failed, please insert a correct functional and basis set information. Restart the process") 
      os.remove(macrotarget+'/'+'keywordqm2.txt')
      yasara.plugin.end() 
    else:
      print('ok')  

    qm2fkey = open(macrotarget+'/'+'keywordqm2.txt', "r")
    qm2keyword= qm2fkey.readlines()
    functionalqm2= str((qm2keyword[0]).strip('\n'))
    basisqm2=str((qm2keyword[1]).strip('\n'))
    print(functionalqm2)
    print(basisqm2)   
  
  else:
    functionalqm2="wB97X-D3"

  print(functionalqm2)
  print(basisqm2)  
##################for transition state calculation
if method == 'ORCA' and methodology == str(3) or methodology == str(8)  or methodology == str(9):  
  #orca='/home/picasso/Documents/orca/orca_4_1_2_linux_x86-64_openmpi313/orca'
  if methodology == str(3):
    imgalllist =\
        yasara.ShowWin("Custom","No of points",400,250,
        "Text",        50, 50,"*Select the  total number of reaction point",
        "NumberInput", 20, 85,"points",8,8,100,
        "Button",      150,200," O K")  
##counting the object present in the yasara window
    rimg=open(macrotarget+'/'+str(nameobj)+'images.log','w+')
    rimg.write((str(imgalllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    rimg.close()
    if os.path.getsize(macrotarget+'/'+str(nameobj)+'images.log') == 0:
      yasara.ShowMessage("QM calculation failed. Must need the number of reaction points. Please restart the process") 
      os.remove(macrotarget+'/'+str(nameobj)+'procharge.log')
      yasara.plugin.end() 

    img = open(macrotarget+'/'+str(nameobj)+'images.log', "r")
    noimg= img.readlines()
    numeroimg= str((noimg[0]).strip('\n'))    


  if methodology == str(3):
    orcareactinp=open((macrotarget)+'/'+'reactant.txt')
    reactdata=orcareactinp.read()
    orcareactinp.close()
    orca_geo_react=open((macrotarget)+'/'+'reactant.inp','w+')
    orca_geo_react.write("!")
    orca_geo_react.write(str(functional))
    orca_geo_react.write(" ")
    orca_geo_react.write(str(basis))
    orca_geo_react.write(" ")
    orca_geo_react.write("OPT")
    #orca_geo_react.write("\n%pal\n   nprocs ")
    #orca_geo_react.write(str(processor))
    #orca_geo_react.write('\nend')
    orca_geo_react.write("\n\n*xyz ")
    orca_geo_react.write(str(reactcharge))
    orca_geo_react.write(" ")
    orca_geo_react.write(str(reactmultiplicity))
    orca_geo_react.write("\n")
    orca_geo_react.write(str(reactdata))
    orca_geo_react.write("\n")
    orca_geo_react.write("*")
    orca_geo_react.close()
    yasara.ShowMessage("orca is optimizing the geometry of reactant")
  #os.rename(macrotarget+'/'+'reactant.xyz', macrotarget+'/'+'prev_reactant.xyz')
    if mod == str(1) or mod == str(2):
      os.chdir(macrotarget)
      os.system(str(orca)+' reactant.inp > reactant.out') 
    else:
      os.system('orca '+macrotarget+'/'+'reactant.inp > '+macrotarget+'/'+'reactant.out')  


###############################################################################
    os.remove((macrotarget)+'/'+'bfactor.txt')
    yasara.run("Clear")
    yasara.run('Loadxyz '+macrotarget+'/'+'reactant.xyz')
    yasara.run("DuplicateAll")
    yasara.run("DelObj 1")
    yasara.run('BFactorAtom all,0')
    cnoatom=yasara.run("CountAtom all")
    catomtext= open(macrotarget+'/'+'catomnotext.txt','w')
    catomtext.write(str(cnoatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
    catomtext.close()
    ca = open((macrotarget)+'/'+'catomnotext.txt', 'r')
    catomcontent = ca.readlines()
    catom=str((catomcontent[0]).strip('\n'))
    catom=int(catom)
    ca.close()
    os.remove((macrotarget)+'/'+'catomnotext.txt')
    ci=0
    for ci in range (0,catom):
      
        yasara.run("BFactorAtom "+str(ci+1)+","+str((ci+1)))
        
    ci=ci+1
    yasara.run("LabelAll 'Do not update hydrogen after bond modification',Height=1.9,Color=Yellow,X=0,Y=19,Z=65")
    yasara.ShowMessage("Please modify the reactant to build product molecule and then click continue")
    yasara.run("wait continuebutton")
    energy_minimization()
    #yasara.ExperimentMinimization()
    #yasara.Experiment("On")
    #yasara.Wait("ExpEnd")
    #yasara.run('DelObj simcell')

##Calculating the charge of the product
    prochargeinfo=charge_calculation()#yasara.run('ChargeObj all')
    promod=open(macrotarget+'/'+str(nameobj)+'procharge.log','w')
    promod.write(str(prochargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']',''))
    promod.close()
    prochargef= open(macrotarget+'/'+str(nameobj)+'procharge.log','r')
    prochargeall=prochargef.readlines()
    procharge=float((prochargeall[0]).strip('\n'))
    procharge=round(procharge)
    print(procharge)

    proalllist =\
      yasara.ShowWin("Custom","INFORMATION",400,250,
      "NumberInput", 20, 88,"Charge",str(procharge),-1000,1000,
      "NumberInput", 180, 88,"Multiplicity",1,1,1000,
      "Button",      150,200," O K")  
##counting the object present in the yasara window
    pcharge=open(macrotarget+'/'+str(nameobj)+'procharge.log','w+')
    pcharge.write((str(proalllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    pcharge.close()

    if os.path.getsize(macrotarget+'/'+str(nameobj)+'procharge.log') == 0:
      yasara.ShowMessage("Charge calculation failed, restart the process") 
      os.remove(macrotarget+'/'+str(nameobj)+'procharge.log')
      yasara.plugin.end() 
    else:
      print('ok')   
    pro_charge = open(macrotarget+'/'+str(nameobj)+'procharge.log', "r")
    productinfo= pro_charge.readlines()
    productcharge= str((productinfo[0]).strip('\n'))    
    productmultiplicity= str((productinfo[1]).strip('\n')) 


  ##counting the atom of product present in the yasara window
    proatom=yasara.run("Countatom all")
    prodeltext= open(macrotarget+'/'+'prodeltext.txt','w')
    prodeltext.write(str(proatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
    prodeltext.close()
    p = open((macrotarget)+'/'+'prodeltext.txt', "r")
    pcontent = p.readlines()
    nopro=str((pcontent[0]).strip('\n').strip('[').strip(']'))
    p.close()
    atom=str(atom)
    os.remove((macrotarget)+'/'+'prodeltext.txt')
##checking the number of atom in product and reactant are same or not

    if nopro == atom :
    #yasara.run('JoinObj all,1')
      j=0
      nopro=int(nopro)
      for j in range (0,nopro):
          bfactor=yasara.run("BFactorAtom "+str(j+1))
          if j == 0:
            val= open(macrotarget+'/'+'product_bfactor.txt','w')
            val.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
            val.close()
          else:
            valread=open(macrotarget+'/'+'product_bfactor.txt','r')
            value=valread.readlines()
            valread.close()
            rewrite=open(macrotarget+'/'+'product_bfactor.txt','w')
            rewrite.writelines(value)
            rewrite.write('\n')
            rewrite.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
            rewrite.close()
        
          j=j+1 
    else:
     yasara.ShowMessage("WARNING! please see the terminal")
     print(nopro)
     print(atom)
     print("No. of atoms must be same for reactant and product")
     yasara.plugin.end()        


##Saving the xyz file of the product
    yasara.run("SaveXYZ all,"+str(macrotarget)+'/'+"product.xyz,transform=Yes") 
##modifying the reactant.xyz file without hamparing the main file
    prodeltexttxt=os.path.join(macrotarget,'prodeltext.txt')
    productbfactortxt=os.path.join(macrotarget,'product_bfactor.txt')
    productxyz=os.path.join(macrotarget,'product.xyz')
    producttxt=os.path.join(macrotarget,'product.txt')
    productfiltertxt=os.path.join(macrotarget,'product_filter.txt')
    productfinaltxt=os.path.join(macrotarget,'product_final.txt')
    os.chdir(macrotarget)
    time.sleep(3)
    with open(productxyz, 'r') as fin:
        data = fin.read().splitlines(True)
    with open(producttxt, 'w') as fout:
        fout.writelines(data[2:]) 
        fout.close()
   
##concatination of reactant xyz info with its b-factor value   
    procombine =[]

    with open(producttxt) as xh:
      with open(productbfactortxt) as yh:
        with open(productfiltertxt,"w") as zh:
       #Read first file
           xlines = xh.readlines()
         #Read second file
           ylines = yh.readlines()
         #Combine content of both lists
         #combine = list(zip(ylines,xlines))
         #Write to third file
           for i in range(len(xlines)):
              line = ylines[i].strip('\n') + '    ' + xlines[i]
              zh.write(line)
    os.remove(producttxt)
    os.remove(productbfactortxt)
    os.remove((macrotarget)+'/'+'reactant_filter.txt')
    yasara.run("clear")
    yasara.run("DelObj all")
    yasara.run('Loadxyz '+macrotarget+'/'+'reactant.xyz')
    yasara.run('Loadxyz '+macrotarget+'/'+'product.xyz')
    radius=yasara.run('RadiusObj 1')
    rd=open(macrotarget+'/'+'radius.txt','w+')
    rd.write(str(radius).replace('[','').replace(']','').replace('Object  1 (reactant) has a VdW radius of ','').replace('A from its geometric center',''))
    rd.close()
    fk=open(macrotarget+'/'+'radius.txt','r')
    r=fk.readline()
    r=str(r)
    r=float(r)
    len= 15
    y= r+len
    y=str(y)
    z=-r-len
    z=str(z)
#yasara.run('r=RadiusObj 1')
#yasara.run('len=15')
    yasara.run('MoveObj !1,X='+str(y))
    yasara.run('MoveObj 1,X='+str(z))
    yasara.run('ShowArrow Start=Point,X=-15,Y=0,Z=50,End=Point,X=15,Y=0,Z=50,Radius=1,Color=Yellow')
    yasara.run('ZoomAll Steps=0')
    yasara.run('Move Z=20')
    yasara.run('LabelObj 1,reactant,Color=Yellow,Y=5,Z=-5')
    yasara.run('LabelObj 2,product,Color=Yellow,Y=5,Z=-5')

    def sortLinesByColumn(readable, column, columnt_type):
        """Returns a list of strings (lines in readable file) in sorted order (based on column)"""
        lines = []

        for line in readable:
          # get the element in column based on which the lines are to be sorted
            column_element= columnt_type(line.split(' ')[column-1])
            lines.append((column_element, line))

        lines.sort()

        return [x[1] for x in lines]


    with open(productfiltertxt) as f:
      # sort the lines based on column 1, and column 1 is type int
        sorted_lines = sortLinesByColumn(f, 1, int)
        k= open(productfinaltxt,"w")
        k.writelines(sorted_lines)
        k.close()

    os.remove(productfiltertxt)
    proedit = open(productfinaltxt, "r")
    editfile = open(productfiltertxt, "w")
    for line in proedit:
        if line.strip():
            editfile.write("\t".join(line.split()[1:]) + "\n")    
    proedit.close()
    editfile.close()
    os.remove(productfinaltxt)
#######################################################
    orcaproinp=open(productfiltertxt)
    prodata=orcaproinp.read()
    orcaproinp.close()
    print(prodata)
    orca_geo_pro=open((macrotarget)+'/'+'product.inp','w+')
    orca_geo_pro.write("!")
    orca_geo_pro.write(str(functional))
    orca_geo_pro.write(" ")
    orca_geo_pro.write(str(basis))
    orca_geo_pro.write(" ")
    orca_geo_pro.write("OPT")
    #orca_geo_pro.write("\n%pal\n   nprocs ")
    #orca_geo_pro.write(str(processor))
    #orca_geo_pro.write('\nend')
    orca_geo_pro.write("\n\n*xyz ")
    orca_geo_pro.write(str(productcharge))
    orca_geo_pro.write(" ")
    orca_geo_pro.write(str(productmultiplicity))
    orca_geo_pro.write("\n")
  #orca_geo_pro.write(str(reactdata))
    orca_geo_pro.write(str(prodata))
    orca_geo_pro.write("\n")
    orca_geo_pro.write("*")
    orca_geo_pro.close()

    yasara.ShowMessage("orca is optimizing the geometry of product")
    if mod == str(1) or mod == str(2):
      os.chdir(macrotarget)
      os.system(str(orca)+' product.inp > product.out')
    else:
      os.system('orca '+macrotarget+'/'+'product.inp > '+macrotarget+'/'+'product.out')
  
    yasara.ShowMessage("Geometry optimization is complete")
    tsinp=open((macrotarget)+'/'+'ts.inp','w+')
    tsinp.write('!')
    tsinp.write(str(functional))
    tsinp.write(' ')
    tsinp.write(str(basis))
    tsinp.write(' NEB-TS FREQ ')
    #tsinp.write("\n%pal\n   nprocs ")
    #tsinp.write(str(processor))
    #tsinp.write('\nend')    
    tsinp.write('\n%geom ReducePrint false end\n%neb\n\nNEB_End_XYZFile "product.xyz"\n\nNImages ')
    tsinp.write(str(numeroimg))
    tsinp.write('\n\nend\n\n*xyzfile ')
    tsinp.write(str(reactcharge))
    tsinp.write(' ')
    tsinp.write(str(reactmultiplicity))
    tsinp.write(' reactant.xyz\n\n')
    tsinp.close()
    yasara.ShowMessage("Transition state calculation is in process..")
    os.chdir(pathYasara)
    os.chdir(macrotarget)
    time.sleep(5)
    if mod == str(1) or mod == str(2): 
      os.system(orca+' ts.inp >ts.out')
    else:
      os.system('orca ts.inp >ts.out')

    if os.path.isfile(macrotarget+'/'+'ts_MEP_trj.xyz') :
      trjlist =\
        yasara.ShowWin("Custom","Trjectory view",400,250,
         "Text", 20, 50, "Do you want to visualize trajectory?",
         "RadioButtons",2,1,
                        20, 100,"yes",
                        200,100,"no",
         "Button",      150,200," O K")
      attach= open((macrotarget)+'/'+'trjectory.txt','w+')
      attach.write((str(trjlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
      attach.close()  
      f = open((macrotarget)+'/'+'trjectory.txt', "r")
      content= f.readlines()
      a = str((content[0]).strip('\n'))   
      if a == str(1):
        if mod == str(1):
          os.rename(macrotarget+'/'+'ts_MEP_trj.xyz', macrotarget+'/'+'ts_MEP_final.xyz' )
        else:
           os.rename(macrotarget+'/'+'ts_MEP_trj.xyz', macrotarget+'/'+'ts_MEP_final.xyz' )     
    
        yasara.run('DelObj all')  
        yasara.run('Loadxyz '+macrotarget+'/'+'ts_MEP_final.xyz')
        yasara.run('BallStickObj all')
        obj=yasara.run("CountObj all")
        deltext= open(macrotarget+'/'+'deltext.txt','w')
        deltext.write(str(obj).replace('object(s) match the selection.','').replace('[','').replace(']',''))
        deltext.close()
        g = open((macrotarget)+'/'+'deltext.txt', "r")
        content = g.readlines()
        noobj=str((content[0]).strip('\n'))
        g.close()
        noobj=int(noobj)
        k=0
        yasara.run('ZoomAll Steps=20')
        yasara.run('HideObj all')
        for k in range(0,noobj):
            yasara.run('ShowObj '+str(k+1))
            yasara.run('BallStickObj all')
            yasara.run("wait continuebutton")
            if int(k+1) == noobj :
              print('done')
            else:
              yasara.run('DelObj '+str(k+1))
            k=k+1
        yasara.ShowMessage("Transition state calculation is complete and results are saved in: "+ macrotarget)
  
    else:
      yasara.ShowMessage("Transition state calculation is complete and results are saved in: "+ macrotarget)    



#######QM-QM2 region########################################################## 
  elif methodology == str(9):
    #processorllist =\
        #yasara.ShowWin("Custom","No of Processor",400,250,
        #"NumberInput", 20, 88,"Processor",8,8,16,
        #"Button",      150,200," O K")  
##counting the object present in the yasara window
   # numeroprocessor=open(macrotarget+'/'+'processor.log','w+')
    #numeroprocessor.write((str(processorllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    #numeroprocessor.close()
    #process = open(macrotarget+'/'+'processor.log', "r")
    #processornumber= process.readlines()
    #processor= str((processornumber[0]).strip('\n'))    
   
    yasara.ShowMessage("Please load Your structure")
    print(functional)
    print(basis)
    print(functionalqm2)
    print(basisqm2)
    if functionalqm2 == "RHF PM3":
      functionalqm2= "PM3"
    else:
      print(functional)
      print(functionalqm2)     
    
    print(functional)
    print(basis)
    print(functionalqm2)
    print(basisqm2)
    yasara.run("wait continuebutton")
    yasara.run("JoinObj all,1")
    
    yasara.run("SavePDB 1,"+str(macrotarget)+"/"+"MM.pdb")
    yasara.ShowMessage("Please select QM object(s) and then click continue")
    yasara.run("wait continuebutton")
    #yasara.run("JoinRes Selected")
    ####have to check
    yasara.run("NameAtom Selected, L")
    #yasara.run("NameAtom all and not selected, con")
    yasara.ShowMessage("Please additionally select QM2 atoms")
    yasara.run("wait continuebutton")
    #yasara.run("UnselectAll")
    #yasara.run("SelectAtom all with distance < 1 from L")
    ####have to check
    yasara.ShowMessage("Calculation is in progress...")
    yasara.run("DelAtom all !selected")
    yasara.run("UnselectAll")
    yasara.run("SelectAtom all and not L")
    yasara.run("NameRes selected,con")
    #yasara.run("NameAtom selected, con")
    #yasara.run("AddHydRes con")
    print('check###')
    yasara.run('BFactorAtom all,0')
    #yasara.run("wait continuebutton")
    countobj=yasara.run('CountObj all')

    #yasara.run("wait continuebutton")
    #yasara.run('joinObj all,1')    
    yasara.run("SavePDB all,"+str(macrotarget)+'/'+"QM.pdb,transform=Yes") 
    #yasara.run("SaveXYZ 1,"+str(macrotarget)+'/'+"QM.xyz,transform=Yes") 
    yasara.run('BFactorAtom all,0')
    cnoatom=yasara.run("CountAtom all")
    catomtext= open(macrotarget+'/'+'catomnotext.txt','w')
    catomtext.write(str(cnoatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
    catomtext.close()
    ca = open((macrotarget)+'/'+'catomnotext.txt', 'r')
    catomcontent = ca.readlines()
    catom=str((catomcontent[0]).strip('\n'))
    catom=int(catom)
    ca.close()
    os.remove((macrotarget)+'/'+'catomnotext.txt')
    ci=0
    for ci in range (0,catom):
      
        yasara.run("BFactorAtom "+str(ci+1)+","+str((ci+1)-1))
        
    ci=ci+1
    yasara.run("DelAtom all and not L")

     
    bfactor=yasara.run("BFactorAtom all")
    
    yasara.ShowMessage("Charge calculation is in progress..")
    resnoatom=yasara.run("CountAtom all")
    resatomtext= open(macrotarget+'/'+'resatomnotext.txt','w')
    resatomtext.write(str(resnoatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
    resatomtext.close()
    resa = open((macrotarget)+'/'+'resatomnotext.txt', 'r')
    resatomcontent = resa.readlines()
    resatom=str((resatomcontent[0]).strip('\n'))
    resatom=int(resatom)
    resa.close()
    os.remove((macrotarget)+'/'+'resatomnotext.txt')
    resi=0
    for i in range (0,resatom):
      
        #yasara.run("BFactorAtom "+str(resi+1)+","+str(resi+1))
        resbfactor=yasara.run("BFactorAtom "+str(resi+1))
        if i == 0:
          val= open(macrotarget+'/'+'check.inp','w')
          #val.write("{C ")
          val.write(str(resbfactor).replace('[','').replace(']','').replace('.0',''))
          #val.write(" C}")
          val.close()
        else:
          valread=open(macrotarget+'/'+'check.inp','r')
          value=valread.readlines()
          valread.close()
          rewrite=open(macrotarget+'/'+'check.inp','w')
          rewrite.writelines(value)
          rewrite.write(' ')
          #rewrite.write('{C ')
          rewrite.write(str(resbfactor).replace('[','').replace(']','').replace('.0',''))
          #rewrite.write(' C}')
          rewrite.close()
        
        resi=resi+1
    yasara.run("DelObj all")

    yasara.run('LoadPDB '+macrotarget+'/'+'QM.pdb')
    yasara.run('BFactorAtom all,0')
    noatom=yasara.run("CountAtom all")
    atomtext= open(macrotarget+'/'+'atomnotext.txt','w')
    atomtext.write(str(noatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
    atomtext.close()
    a = open((macrotarget)+'/'+'atomnotext.txt', 'r')
    atomcontent = a.readlines()
    atom=str((atomcontent[0]).strip('\n'))
    atom=int(atom)
    a.close()
    os.remove((macrotarget)+'/'+'atomnotext.txt')
    i=0
    for i in range (0,atom):
      
        yasara.run("BFactorAtom "+str(i+1)+","+str(i+1))
        bfactor=yasara.run("BFactorAtom "+str(i+1))
        if i == 0:
          val= open(macrotarget+'/'+'bfactor.txt','w')
          val.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
          val.close()
        else:
          valread=open(macrotarget+'/'+'bfactor.txt','r')
          value=valread.readlines()
          valread.close()
          rewrite=open(macrotarget+'/'+'bfactor.txt','w')
          rewrite.writelines(value)
          rewrite.write('\n')
          rewrite.write(str(bfactor).replace('[','').replace(']',''))
          rewrite.close()
        
        i=i+1

    yasara.run("SaveXYZ 1,"+str(macrotarget)+'/'+"QM.xyz,transform=Yes") 


    yasara.run('ForceField AMBER03,SetPar=Yes')
###charge of the reactant molecule
    chargeinfo=charge_calculation()#yasara.run('ChargeObj all')
    cfmod=open(macrotarget+'/'+str(nameobj)+'charge.log','w')
    cfmod.write(str(chargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']','').replace(',','\n'))
    cfmod.close()
    chargef= open(macrotarget+'/'+str(nameobj)+'charge.log','r')
    chargeall=chargef.readlines()
    charge=float((chargeall[0]).strip('\n'))
    charge=round(charge)
    print(charge)
    alllist =\
      yasara.ShowWin("Custom","INFORMATION",400,250,
      "NumberInput", 20, 88,"Charge",str(charge),-1000,1000,
      "NumberInput", 180, 88,"Multiplicity",1,1,1000,
      "Button",      150,200," O K")  
##counting the object present in the yasara window
    rcharge=open(macrotarget+'/'+str(nameobj)+'charge.log','w+')
    rcharge.write((str(alllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    rcharge.close()
    if os.path.getsize(macrotarget+'/'+str(nameobj)+'charge.log') == 0:
      yasara.ShowMessage("Charge calculation failed, restart the process") 
      os.remove(macrotarget+'/'+str(nameobj)+'charge.log')
      yasara.plugin.end() 
    else:
      print('ok')   

    react_charge = open(macrotarget+'/'+str(nameobj)+'charge.log', "r")
    reactinfo= react_charge.readlines()
    reactcharge= str((reactinfo[0]).strip('\n'))    
    reactmultiplicity= str((reactinfo[1]).strip('\n')) 

    #f= open(macrotarget+'/'+'QM_res.xyz','r')
    #content= f.readlines()
    #conregion= str(content[0].strip('\n'))
    #print(conregion)
    #x=int(conregion)
    #i=0
    #g= open (macrotarget+'/'+'check.inp','w')
   # for i in range (0, x):
      # g.write('{C ')
      # g.write(str(i))
      # g.write(' C}\n')
      # i=i+1
   # g.close()
  
    with open(str(macrotarget)+'/'+'QM.xyz', 'r') as fin:
        data = fin.read().splitlines(True)
    with open(str(macrotarget)+'/'+'qm.txt', 'w') as fout:
        fout.writelines(data[2:]) 
        fout.close()
     
    orcaproinp=open((macrotarget)+'/'+'qm.txt')
    prodata=orcaproinp.read()
    orcaproinp.close()

    con=open((macrotarget)+'/'+'check.inp')
    condata=con.read()
    con.close()
    if functionalqm2 == 'XTB' or functionalqm2== 'PM3':
      k= open(macrotarget+'/'+'QM_reactant.inp','w')
      k.write('! QM/')
      k.write(str(functionalqm2))
      k.write(' ')
      k.write(str(basisqm2))
      k.write(' ')
      k.write(str(functional))
      k.write(' ')
      k.write(str(basis))
      k.write(' Opt\n')
      k.write('%QMMM QMATOMS {')
      k.write(str(condata))
      k.write('} END END')
      k.write('\n%maxcore 101376\n%geom')    
      k.write('\nend')
      #k.write("\n%pal\n   nprocs ")
     # k.write(str(processor))
      #k.write('\nend\n')
      k.write('\n*xyz ')
      k.write(str(reactcharge))
      k.write(' ')
      k.write(str(reactmultiplicity))
      k.write('\n')
      k.write(str(prodata))
      k.write('\n*')
      k.close()
    else:
      k= open(macrotarget+'/'+'QM_reactant.inp','w')
      k.write('! QM/QM2 ')
      k.write(str(functional))
      k.write(' ')
      k.write(str(basis))
      k.write(' Opt\n')
      k.write('%QMMM QM2CUSTOMMETHOD "')
      k.write(str(functionalqm2))
      k.write(' ')
      k.write(str(basisqm2))
      k.write('"\n      QMATOMS {')
      k.write(str(condata))
      k.write('} END END')
      k.write('\n%maxcore 101376\n%geom')    
      k.write('\nend')
      #k.write("\n%pal\n   nprocs ")
      #k.write(str(processor))
      #k.write('\nend\n')
      k.write('\n*xyz ')
      k.write(str(reactcharge))
      k.write(' ')
      k.write(str(reactmultiplicity))
      k.write('\n')
      k.write(str(prodata))
      k.write('\n*')
      k.close()        

    os.chdir(pathYasara)
    os.chdir(macrotarget)  
    yasara.ShowMessage("Geometry optimization is in progress..")  
    if mod == str(1) or mod == str(2): 
      print('check')
      os.system(orca+' QM_reactant.inp >QM_reactant.out')
    else:
      os.system('orca QM_reactant.inp >QM_reactant.out')


    yasara.run('DelObj all')
    if os.path.isfile(macrotarget+'/'+'QM_reactant.xyz'):
      yasara.run('LoadXYZ '+macrotarget+'/'+'QM_reactant.xyz')
    else:
      yasara.ShowMessage("Geometry optimization failed") 

    transitionlist =\
      yasara.ShowWin("Custom","Transition state",400,250,
       "Text", 20, 50, "Do you want to perform transition state?",
       "RadioButtons",2,1,
                      20, 100,"yes",
                      200,100,"no",
       "Button",      150,200," O K")
    tsattach= open((macrotarget)+'/'+'ts_ini.txt','w+')
    tsattach.write((str(transitionlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    tsattach.close()  
    fts = open((macrotarget)+'/'+'ts_ini.txt', "r")
    contentts= fts.readlines()
    ats = str((contentts[0]).strip('\n'))    
    if ats == str(2) or mod==str(2):
       yasara.ShowMessage("Geometry optimization is complete. For ONIOM TS calculation, XTB tool is required.")
       print('XTB is currently available only for linux system..in absent of XTB, GUIDE can not perform ONIOM TS calculation.')
       yasara.plugin.end()
    yasara.ShowMessage("Make sure XTB is installed and otool_xtb is present in Orca directory")
    print('XTB is currently available only for linux system..in absent of XTB, GUIDE can not perform ONIOM TS calculation.')
    yasara.run("wait continuebutton")

    imgalllist =\
        yasara.ShowWin("Custom","No of points",400,250,
       "Text",        50, 50,"*Select the  total number of reaction point",
       "NumberInput", 20, 80,"points",8,8,100,
        "Button",      150,200," O K")  
##counting the object present in the yasara window
    rimg=open(macrotarget+'/'+str(nameobj)+'images.log','w+')
    rimg.write((str(imgalllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    rimg.close()
    if os.path.getsize(macrotarget+'/'+str(nameobj)+'images.log') == 0:
      yasara.ShowMessage("QM calculation failed. Must need the number of reaction points. Please restart the process") 
      os.remove(macrotarget+'/'+str(nameobj)+'procharge.log')
      yasara.plugin.end() 

    img = open(macrotarget+'/'+str(nameobj)+'images.log', "r")
    noimg= img.readlines()
    numeroimg= str((noimg[0]).strip('\n')) 

    i=0
    for i in range (0,atom):
      
        yasara.run("BFactorAtom "+str(i+1)+","+str(i+1))
        bfactor=yasara.run("BFactorAtom "+str(i+1))
        if i == 0:
          val= open(macrotarget+'/'+'bfactor.txt','w')
          val.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
          val.close()
        else:
          valread=open(macrotarget+'/'+'bfactor.txt','r')
          value=valread.readlines()
          valread.close()
          rewrite=open(macrotarget+'/'+'bfactor.txt','w')
          rewrite.writelines(value)
          rewrite.write('\n')
          rewrite.write(str(bfactor).replace('[','').replace(']',''))
          rewrite.close()
        
        i=i+1
   
##concatination of reactant xyz info with its b-factor value   
    combine =[]

    with open((macrotarget)+'/'+'bfactor.txt') as xh:
      with open((macrotarget)+'/'+'qm.txt') as yh:
        with open((macrotarget)+'/'+'QM_filter.txt',"w") as zh:
         #Read first file
           xlines = xh.readlines()
         #Read second file
           ylines = yh.readlines()
         #Combine content of both lists
         #combine = list(zip(ylines,xlines))
         #Write to third file
           for i in range(len(xlines)):
              line = ylines[i].strip('\n') + '    ' + xlines[i]
              zh.write(line)
#os.remove((macrotarget)+'/'+'reactant.txt')
    #os.remove((macrotarget)+'/'+'bfactor.txt')
    #yasara.run("DuplicateAll")
    #yasara.run("DelObj 1")
    yasara.run('BallStickObj all')
    yasara.run("LabelAll 'Do not update hydrogen after bond modification',Height=1.9,Color=Yellow,X=0,Y=19,Z=65")
    yasara.ShowMessage("Please modify the reactant to build product molecule and then click continue")
    yasara.run("wait continuebutton")
    yasara.run('SelectAtom L')
    #yasara.run('FixAtom selected')
    yasara.ShowMessage("Geometry optimization is in progress..") 
    #yasara.run('UnselectAll')
    #yasara.run('Cell Auto,Shape=Cube,selected')
    yasara.run('UnselectAll')
    energy_minimization()
    #yasara.ExperimentMinimization()
    #yasara.Experiment("On")
    #yasara.Wait("ExpEnd")
    #yasara.run('DelObj simcell')
    yasara.ShowMessage("Charge calculation is in progress..")
##Calculating the charge of the product
    prochargeinfo=charge_calculation()#yasara.run('ChargeObj all')
    promod=open(macrotarget+'/'+str(nameobj)+'procharge.log','w')
    promod.write(str(prochargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']',''))
    promod.close()
    prochargef= open(macrotarget+'/'+str(nameobj)+'procharge.log','r')
    prochargeall=prochargef.readlines()
    procharge=float((prochargeall[0]).strip('\n'))
    procharge=round(procharge)
    print(procharge)

    proalllist =\
      yasara.ShowWin("Custom","INFORMATION",400,250,
      "NumberInput", 20, 88,"Charge",str(procharge),-1000,1000,
      "NumberInput", 180, 88,"Multiplicity",1,1,1000,
      "Button",      150,200," O K")  
##counting the object present in the yasara window
    pcharge=open(macrotarget+'/'+str(nameobj)+'procharge.log','w+')
    pcharge.write((str(proalllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    pcharge.close()

    if os.path.getsize(macrotarget+'/'+str(nameobj)+'procharge.log') == 0:
      yasara.ShowMessage("Charge calculation failed, restart the process") 
      os.remove(macrotarget+'/'+str(nameobj)+'procharge.log')
      yasara.plugin.end() 
    else:
      print('ok')   
    pro_charge = open(macrotarget+'/'+str(nameobj)+'procharge.log', "r")
    productinfo= pro_charge.readlines()
    productcharge= str((productinfo[0]).strip('\n'))    
    productmultiplicity= str((productinfo[1]).strip('\n')) 


  ##counting the atom of product present in the yasara window
    proatom=yasara.run("Countatom all")
    prodeltext= open(macrotarget+'/'+'prodeltext.txt','w')
    prodeltext.write(str(proatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
    prodeltext.close()
    p = open((macrotarget)+'/'+'prodeltext.txt', "r")
    pcontent = p.readlines()
    nopro=str((pcontent[0]).strip('\n').strip('[').strip(']'))
    p.close()
    atom=str(atom)
    os.remove((macrotarget)+'/'+'prodeltext.txt')
##checking the number of atom in product and reactant are same or not

    if nopro == atom :
      #yasara.run('JoinObj all,1')
      j=0
      nopro=int(nopro)
      for j in range (0,nopro):
          bfactor=yasara.run("BFactorAtom "+str(j+1))
          if j == 0:
            val= open(macrotarget+'/'+'product_bfactor.txt','w')
            val.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
            val.close()
          else:
            valread=open(macrotarget+'/'+'product_bfactor.txt','r')
            value=valread.readlines()
            valread.close()
            rewrite=open(macrotarget+'/'+'product_bfactor.txt','w')
            rewrite.writelines(value)
            rewrite.write('\n')
            rewrite.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
            rewrite.close()
        
          j=j+1 
    else:
     yasara.ShowMessage("WARNING! please see the terminal")
     print(nopro)
     print(atom)
     print("No. of atoms must be same for reactant and product")
     yasara.plugin.end()        


##Saving the xyz file of the product
    yasara.run("SaveXYZ all,"+str(macrotarget)+'/'+"QM_product.xyz,transform=Yes") 
##modifying the reactant.xyz file without hamparing the main file
    with open(str(macrotarget)+'/'+'QM_product.xyz', 'r') as fin:
        data = fin.read().splitlines(True)
    with open(str(macrotarget)+'/'+'QM_product.txt', 'w') as fout:
        fout.writelines(data[2:]) 
        fout.close()
   
##concatination of reactant xyz info with its b-factor value   
    procombine =[]

    with open((macrotarget)+'/'+'QM_product.txt') as xh:
      with open((macrotarget)+'/'+'product_bfactor.txt') as yh:
        with open((macrotarget)+'/'+'QM_product_filter.txt',"w") as zh:
       #Read first file
           xlines = xh.readlines()
         #Read second file
           ylines = yh.readlines()
         #Combine content of both lists
         #combine = list(zip(ylines,xlines))
         #Write to third file
           for i in range(len(xlines)):
              line = ylines[i].strip('\n') + '    ' + xlines[i]
              zh.write(line)

    yasara.run("clear")
    yasara.run("DelObj all")
    yasara.run('Loadxyz '+macrotarget+'/'+'QM.xyz')
    yasara.run('BallStickObj all')
    yasara.run('Loadxyz '+macrotarget+'/'+'QM_product.xyz')
    yasara.run('BallStickObj all')
    radius=yasara.run('RadiusObj 1')
    rd=open(macrotarget+'/'+'radius.txt','w+')
    rd.write(str(radius).replace('[','').replace(']','').replace('Object  1 (reactant) has a VdW radius of ','').replace('A from its geometric center',''))
    rd.close()
    fk=open(macrotarget+'/'+'radius.txt','r')
    r=fk.readline()
    r=str(r)
    r=float(r)
    len= 15
    y= r+len
    y=str(y)
    z=-r-len
    z=str(z)
#yasara.run('r=RadiusObj 1')
#yasara.run('len=15')
    yasara.run('MoveObj !1,X='+str(y))
    yasara.run('MoveObj 1,X='+str(z))
    yasara.run('ShowArrow Start=Point,X=-15,Y=0,Z=50,End=Point,X=15,Y=0,Z=50,Radius=1,Color=Yellow')
    yasara.run('ZoomAll Steps=0')
    yasara.run('Move Z=20')
    yasara.run('LabelObj 1,reactant,Color=Yellow,Y=5,Z=-5')
    yasara.run('LabelObj 2,product,Color=Yellow,Y=5,Z=-5')

    def sortLinesByColumn(readable, column, columnt_type):
        """Returns a list of strings (lines in readable file) in sorted order (based on column)"""
        lines = []

        for line in readable:
            # get the element in column based on which the lines are to be sorted
            column_element= columnt_type(line.split(' ')[column-1])
            lines.append((column_element, line))

        lines.sort()

        return [x[1] for x in lines]


    with open((macrotarget)+'/'+'QM_product_filter.txt') as f:
        # sort the lines based on column 1, and column 1 is type int
        sorted_lines = sortLinesByColumn(f, 1, int)
        k= open((macrotarget)+'/'+'QM_product_final.txt',"w")
        k.writelines(sorted_lines)
        k.close()

  #os.remove((macrotarget)+'/'+'product_filter.txt')
    proedit = open((macrotarget)+'/'+'QM_product_final.txt', "r")
    editfile = open((macrotarget)+'/'+'QM_product_filter.txt', "w")
    for line in proedit:
        if line.strip():
            editfile.write("\t".join(line.split()[1:]) + "\n")    
    proedit.close()
    editfile.close()
    os.remove((macrotarget)+'/'+'QM_product_final.txt')


    qmorcaproinp=open((macrotarget)+'/'+'QM_product_filter.txt')
    qmprodata=qmorcaproinp.read()
    qmorcaproinp.close()
    print(prodata)
    if functionalqm2 == 'XTB' or functionalqm2== 'PM3':
      orca_geo_pro=open((macrotarget)+'/'+'QM_product.inp','w+')
      orca_geo_pro.write("! QM/")
      orca_geo_pro.write(str(functionalqm2))
      orca_geo_pro.write(' ')
      orca_geo_pro.write(str(basisqm2))
      orca_geo_pro.write(' ')
      orca_geo_pro.write(str(functional))
      orca_geo_pro.write(" ")
      orca_geo_pro.write(str(basis))
      orca_geo_pro.write(' Opt\n')
    #orca_geo_pro.write("\n%pal\n   nprocs ")
    #orca_geo_pro.write(str(processor))
    #orca_geo_pro.write('\nend')
      orca_geo_pro.write('%QMMM QMATOMS {')
      orca_geo_pro.write(str(condata))
      orca_geo_pro.write('} END END')
      orca_geo_pro.write('\n%maxcore 101376\n%geom')
      orca_geo_pro.write('\nend')
      #orca_geo_pro.write("\n%pal\n   nprocs ")
      #orca_geo_pro.write(str(processor))
      #orca_geo_pro.write('\nend\n')
      orca_geo_pro.write('\n*xyz ')    
      orca_geo_pro.write(str(productcharge))
      orca_geo_pro.write(" ")
      orca_geo_pro.write(str(productmultiplicity))
      orca_geo_pro.write("\n")
  #orca_geo_pro.write(str(reactdata))
      orca_geo_pro.write(str(qmprodata))
      orca_geo_pro.write("\n*")
      orca_geo_pro.close()
    else:
      orca_geo_pro=open((macrotarget)+'/'+'QM_product.inp','w+')
      orca_geo_pro.write("! QM/QM2 ")
      #orca_geo_pro.write(str(functionalqm2))
      #orca_geo_pro.write(' ')
      #orca_geo_pro.write(str(basisqm2))
      #orca_geo_pro.write(' ')
      orca_geo_pro.write(str(functional))
      orca_geo_pro.write(" ")
      orca_geo_pro.write(str(basis))
      orca_geo_pro.write(' Opt\n')
    #orca_geo_pro.write("\n%pal\n   nprocs ")
    #orca_geo_pro.write(str(processor))
    #orca_geo_pro.write('\nend')
      orca_geo_pro.write('%QMMM QM2CUSTOMMETHOD "')
      orca_geo_pro.write(str(functionalqm2))
      orca_geo_pro.write(' ')
      orca_geo_pro.write(str(basisqm2))  
      orca_geo_pro.write('"\n      QMATOMS {')
      orca_geo_pro.write(str(condata))
      orca_geo_pro.write('} END END')
      orca_geo_pro.write('\n%maxcore 101376\n%geom')
      orca_geo_pro.write('\nend')
      #orca_geo_pro.write("\n%pal\n   nprocs ")
      #orca_geo_pro.write(str(processor))
      #orca_geo_pro.write('\nend\n')
      orca_geo_pro.write('\n*xyz ')    
      orca_geo_pro.write(str(productcharge))
      orca_geo_pro.write(" ")
      orca_geo_pro.write(str(productmultiplicity))
      orca_geo_pro.write("\n")
  #orca_geo_pro.write(str(reactdata))
      orca_geo_pro.write(str(qmprodata))
      orca_geo_pro.write("\n*")
      orca_geo_pro.close()      



    yasara.ShowMessage("Geometry optimization is in progress..")  
    if mod == str(1) or mod == str(2): 
      print('check')
      os.system(orca+' QM_product.inp >QM_product.out')
    else:
      os.system('orca QM_product.inp >QM_product.out')




    yasara.ShowMessage("Geometry optimization is complete")
    if functionalqm2 == 'XTB' or functionalqm2== 'PM3':
      tsinp=open((macrotarget)+'/'+'ts.inp','w+')
      tsinp.write('!QM/')
      tsinp.write(str(functionalqm2))
      tsinp.write(' ')
      tsinp.write(str(basisqm2))
      tsinp.write(' ')
      tsinp.write(str(functional))
      tsinp.write(' ')
      tsinp.write(str(basis))
      tsinp.write(' NEB-TS NUMFREQ \n')#FREQ')
      tsinp.write('%QMMM QMATOMS {')
      tsinp.write(str(condata))
      tsinp.write('} END END')    
      tsinp.write('\n%NEB PREOPT TRUE PRODUCT "QM_product.xyz" \n')   
      tsinp.write('\nNImages ')
      tsinp.write(str(numeroimg))
      tsinp.write('\n\nend ')
      #tsinp.write("\n\n%pal\n   nprocs ")
      #tsinp.write(str(processor))
      #tsinp.write('\nend')         
      tsinp.write('\n*XYZFILE ')
      tsinp.write(str(reactcharge))
      tsinp.write(' ')
      tsinp.write(str(reactmultiplicity))
      tsinp.write(' QM_reactant.xyz\n\n')
      tsinp.close()
    else:
      tsinp=open((macrotarget)+'/'+'ts.inp','w+')
      tsinp.write('!QM/QM2 ')
      #tsinp.write(str(functionalqm2))
      #tsinp.write(' ')
      #tsinp.write(str(basisqm2))
      #tsinp.write(' ')
      tsinp.write(str(functional))
      tsinp.write(' ')
      tsinp.write(str(basis))
      tsinp.write(' NEB-TS  NUMFREQ\n')#FREQ')
      tsinp.write('%QMMM QM2CUSTOMMETHOD "')
      tsinp.write(str(functionalqm2))
      tsinp.write(' ')
      tsinp.write(str(basisqm2))      
      tsinp.write('"\n      QMATOMS {')
      tsinp.write(str(condata))
      tsinp.write('} END END')    
      tsinp.write('\n%NEB PREOPT TRUE PRODUCT "QM_product.xyz" \n')   
      tsinp.write('\nNImages ')
      tsinp.write(str(numeroimg))
      tsinp.write('\n\nend ')
      #tsinp.write("\n\n%pal\n   nprocs ")
      #tsinp.write(str(processor))
      #tsinp.write('\nend')         
      tsinp.write('\n*XYZFILE ')
      tsinp.write(str(reactcharge))
      tsinp.write(' ')
      tsinp.write(str(reactmultiplicity))
      tsinp.write(' QM_reactant.xyz\n\n')
      tsinp.close()      
    yasara.ShowMessage("Transition state calculation is in process..")
    os.chdir(pathYasara)
    os.chdir(macrotarget)
    time.sleep(5)
    if mod == str(1) or mod == str(2): 
      os.system(orca+' ts.inp >ts.out')
    else:
      os.system('orca ts.inp >ts.out')

    if os.path.isfile(macrotarget+'/'+'ts_MEP_trj.xyz') :
      trjlist =\
        yasara.ShowWin("Custom","Trjectory view",400,250,
         "Text", 20, 50, "Do you want to visualize trajectory?",
         "RadioButtons",2,1,
                        20, 100,"yes",
                        200,100,"no",
         "Button",      150,200," O K")
      attach= open((macrotarget)+'/'+'trjectory.txt','w+')
      attach.write((str(trjlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
      attach.close()  
      f = open((macrotarget)+'/'+'trjectory.txt', "r")
      content= f.readlines()
      a = str((content[0]).strip('\n'))   
      if a == str(1):
        if mod == str(1):
          os.rename(macrotarget+'/'+'ts_MEP_trj.xyz', macrotarget+'/'+'ts_MEP_final.xyz' )
        else:
           os.rename(macrotarget+'/'+'ts_MEP_trj.xyz', macrotarget+'/'+'ts_MEP_final.xyz' )     
    
        yasara.run('DelObj all')  
        yasara.run('Loadxyz '+macrotarget+'/'+'ts_MEP_final.xyz')
        yasara.run('BallStickObj all')
        obj=yasara.run("CountObj all")
        deltext= open(macrotarget+'/'+'deltext.txt','w')
        deltext.write(str(obj).replace('object(s) match the selection.','').replace('[','').replace(']',''))
        deltext.close()
        g = open((macrotarget)+'/'+'deltext.txt', "r")
        content = g.readlines()
        noobj=str((content[0]).strip('\n'))
        g.close()
        noobj=int(noobj)
        k=0
        yasara.run('ZoomAll Steps=20')
        yasara.run('HideObj all')
        for k in range(0,noobj):
            yasara.run('ShowObj '+str(k+1))
            yasara.run('BallStickObj all')
            yasara.run("wait continuebutton")
            if int(k+1) == noobj :
              print('done')
            else:
              yasara.run('DelObj '+str(k+1))
            k=k+1
        yasara.ShowMessage("Transition state calculation is complete and results are saved in: "+ macrotarget)
  
    else:
      yasara.ShowMessage("Transition state calculation is complete and results are saved in: "+ macrotarget)    




###QM-MM region########################################################## 
  else :
    yasara.ShowMessage("Please load Your structure")
    print(functional)
    print(basis)
    yasara.run("wait continuebutton")
    yasara.run("JoinObj all,1")
    
    yasara.run("SavePDB 1,"+str(macrotarget)+"/"+"MM.pdb")
    yasara.ShowMessage("Please select QM object(s) and then click continue")
    yasara.run("wait continuebutton")
    #yasara.run("JoinRes Selected")
    ####have to check
    yasara.run("NameAtom Selected,L")
    #yasara.run("NameAtom all and not selected, con")
    yasara.ShowMessage("Please additionally select atoms for constraining")
    yasara.run("wait continuebutton")
    #yasara.run("UnselectAll")
    #yasara.run("SelectAtom all with distance < 1 from L")
    ####have to check
    yasara.run("DelAtom all !selected")
    yasara.run("UnselectAll")
    yasara.run("SelectAtom all and not L")
    yasara.run("NameRes selected,con")
    yasara.run("AddHydRes con")
    print('check###')
    yasara.run('BFactorAtom all,0')
    #yasara.run("wait continuebutton")
    countobj=yasara.run('CountObj all')

    #yasara.run("wait continuebutton")
    #yasara.run('joinObj all,1')    
    yasara.run("SavePDB all,"+str(macrotarget)+'/'+"QM.pdb,transform=Yes") 
    #yasara.run("SaveXYZ 1,"+str(macrotarget)+'/'+"QM.xyz,transform=Yes") 
    yasara.run('BFactorAtom all,0')
    cnoatom=yasara.run("CountAtom all")
    catomtext= open(macrotarget+'/'+'catomnotext.txt','w')
    catomtext.write(str(cnoatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
    catomtext.close()
    ca = open((macrotarget)+'/'+'catomnotext.txt', 'r')
    catomcontent = ca.readlines()
    catom=str((catomcontent[0]).strip('\n'))
    catom=int(catom)
    ca.close()
    os.remove((macrotarget)+'/'+'catomnotext.txt')
    ci=0
    for ci in range (0,catom):
      
        yasara.run("BFactorAtom "+str(ci+1)+","+str((ci+1)-1))
        
    ci=ci+1
    yasara.run("DelAtom L")

     
    bfactor=yasara.run("BFactorAtom all")
    
    yasara.ShowMessage("Charge calculation is in progress..")
    resnoatom=yasara.run("CountAtom all")
    resatomtext= open(macrotarget+'/'+'resatomnotext.txt','w')
    resatomtext.write(str(resnoatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
    resatomtext.close()
    resa = open((macrotarget)+'/'+'resatomnotext.txt', 'r')
    resatomcontent = resa.readlines()
    resatom=str((resatomcontent[0]).strip('\n'))
    resatom=int(resatom)
    resa.close()
    os.remove((macrotarget)+'/'+'resatomnotext.txt')
    resi=0
    for i in range (0,resatom):
      
        #yasara.run("BFactorAtom "+str(resi+1)+","+str(resi+1))
        resbfactor=yasara.run("BFactorAtom "+str(resi+1))
        if i == 0:
          val= open(macrotarget+'/'+'check.inp','w')
          val.write("{C ")
          val.write(str(resbfactor).replace('[','').replace(']','').replace('.0',''))
          val.write(" C}")
          val.close()
        else:
          valread=open(macrotarget+'/'+'check.inp','r')
          value=valread.readlines()
          valread.close()
          rewrite=open(macrotarget+'/'+'check.inp','w')
          rewrite.writelines(value)
          rewrite.write('\n')
          rewrite.write('{C ')
          rewrite.write(str(resbfactor).replace('[','').replace(']','').replace('.0',''))
          rewrite.write(' C}')
          rewrite.close()
        
        resi=resi+1

    #yasara.run('joinAtom all,1') 
    yasara.run("SaveXYZ all,"+str(macrotarget)+'/'+"QM_res.xyz,transform=Yes")  
    yasara.run("DelObj all")
    yasara.run('LoadPDB '+macrotarget+'/'+'QM.pdb')
    yasara.run('BFactorAtom all,0')
    noatom=yasara.run("CountAtom all")
    atomtext= open(macrotarget+'/'+'atomnotext.txt','w')
    atomtext.write(str(noatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
    atomtext.close()
    a = open((macrotarget)+'/'+'atomnotext.txt', 'r')
    atomcontent = a.readlines()
    atom=str((atomcontent[0]).strip('\n'))
    atom=int(atom)
    a.close()
    os.remove((macrotarget)+'/'+'atomnotext.txt')
    i=0
    for i in range (0,atom):
      
        yasara.run("BFactorAtom "+str(i+1)+","+str(i+1))
        bfactor=yasara.run("BFactorAtom "+str(i+1))
        if i == 0:
          val= open(macrotarget+'/'+'bfactor.txt','w')
          val.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
          val.close()
        else:
          valread=open(macrotarget+'/'+'bfactor.txt','r')
          value=valread.readlines()
          valread.close()
          rewrite=open(macrotarget+'/'+'bfactor.txt','w')
          rewrite.writelines(value)
          rewrite.write('\n')
          rewrite.write(str(bfactor).replace('[','').replace(']',''))
          rewrite.close()
        
        i=i+1

    yasara.run("SaveXYZ 1,"+str(macrotarget)+'/'+"QM.xyz,transform=Yes") 


    yasara.run('ForceField AMBER03,SetPar=Yes')
###charge of the reactant molecule
    chargeinfo=charge_calculation()#yasara.run('ChargeObj all')
    cfmod=open(macrotarget+'/'+str(nameobj)+'charge.log','w')
    cfmod.write(str(chargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']','').replace(',','\n'))
    cfmod.close()
    chargef= open(macrotarget+'/'+str(nameobj)+'charge.log','r')
    chargeall=chargef.readlines()
    charge=float((chargeall[0]).strip('\n'))
    charge=round(charge)
    print(charge)
    alllist =\
      yasara.ShowWin("Custom","INFORMATION",400,250,
      "NumberInput", 20, 88,"Charge",str(charge),-1000,1000,
      "NumberInput", 180, 88,"Multiplicity",1,1,1000,
      "Button",      150,200," O K")  
##counting the object present in the yasara window
    rcharge=open(macrotarget+'/'+str(nameobj)+'charge.log','w+')
    rcharge.write((str(alllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    rcharge.close()
    if os.path.getsize(macrotarget+'/'+str(nameobj)+'charge.log') == 0:
      yasara.ShowMessage("Charge calculation failed, restart the process") 
      os.remove(macrotarget+'/'+str(nameobj)+'charge.log')
      yasara.plugin.end() 
    else:
      print('ok')   

    react_charge = open(macrotarget+'/'+str(nameobj)+'charge.log', "r")
    reactinfo= react_charge.readlines()
    reactcharge= str((reactinfo[0]).strip('\n'))    
    reactmultiplicity= str((reactinfo[1]).strip('\n')) 

    f= open(macrotarget+'/'+'QM_res.xyz','r')
    content= f.readlines()
    conregion= str(content[0].strip('\n'))
    print(conregion)
    x=int(conregion)
    #i=0
    #g= open (macrotarget+'/'+'check.inp','w')
   # for i in range (0, x):
      # g.write('{C ')
      # g.write(str(i))
      # g.write(' C}\n')
      # i=i+1
   # g.close()
  
    with open(str(macrotarget)+'/'+'QM.xyz', 'r') as fin:
        data = fin.read().splitlines(True)
    with open(str(macrotarget)+'/'+'qm.txt', 'w') as fout:
        fout.writelines(data[2:]) 
        fout.close()
     
    orcaproinp=open((macrotarget)+'/'+'qm.txt')
    prodata=orcaproinp.read()
    orcaproinp.close()

    con=open((macrotarget)+'/'+'check.inp')
    condata=con.read()
    con.close()
    k= open(macrotarget+'/'+'QM_reactant.inp','w')
    k.write('! SP ')
    k.write(str(functional))
    k.write(' ')
    k.write(str(basis))
    k.write(' Opt Hirshfeld')
   # k.write("\n%pal\n   nprocs ")
  #  k.write(str(processor))
   # k.write('\nend')
    k.write('\n%maxcore 101376\n%geom \nConstraints\n')
    k.write(str(condata))
    k.write('\nend\nend\n*xyz ')
    k.write(str(reactcharge))
    k.write(' ')
    k.write(str(reactmultiplicity))
    k.write('\n')
    k.write(str(prodata))
    k.write('\n*')
    k.close()
    os.chdir(pathYasara)
    os.chdir(macrotarget)  
    yasara.ShowMessage("Geometry optimization is in progress..")  
    if mod == str(1) or mod == str(2): 
      print('check')
      os.chdir(macrotarget)
      os.system(orca+' QM_reactant.inp >QM_reactant.out')
    else:
      os.system('orca QM_reactant.inp >QM_reactant.out')



    yasara.run('DelObj all')
    if os.path.isfile(macrotarget+'/'+'QM_reactant.xyz'):
      yasara.run('LoadXYZ '+macrotarget+'/'+'QM_reactant.xyz')
    else:
      yasara.ShowMessage("Geometry optimization failed") 
    transitionlist =\
      yasara.ShowWin("Custom","Calculation",400,250,
       "Text", 20, 50, "Do you want to perform other calculations?",
       "RadioButtons",2,1,
                      20, 100,"yes",
                      200,100,"no",
       "Button",      150,200," O K")
    tsattach= open((macrotarget)+'/'+'ts_ini.txt','w+')
    tsattach.write((str(transitionlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    tsattach.close()  
    fts = open((macrotarget)+'/'+'ts_ini.txt', "r")
    contentts= fts.readlines()
    ats = str((contentts[0]).strip('\n'))    
    if ats == str(2):
       yasara.ShowMessage("Geometry optimization is complete")
       yasara.plugin.end()


###########################################
    recalculationlist=\
      yasara.ShowWin("Custom","CALCULATION",400,250,
      "Text", 20, 48, "Calculation type",
      "RadioButtons",3,1,
                     20, 65,"Transition state",
                     20, 105,"HOMO-LUMO energy gap",
                     20, 155,"Fukui function",
      "Button",      150,200," O K")    


    recal=open(macrotarget+'/'+'recalculation.txt','w+')
    recal.write((str(recalculationlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    recal.close()
    methos_recal = open(macrotarget+'/'+'recalculation.txt', "r")
    recaltype= methos_recal.readlines()
    if os.path.getsize(macrotarget+'/'+'recalculation.txt') == 0:
      yasara.ShowMessage("QM calculation failed, select a specific method") 
      os.remove(macrotarget+'/'+'recalculation.txt')
      yasara.plugin.end() 
    else:
      print('ok') 

    remethodology= str((recaltype[0]).strip('\n')) 


############################
    if remethodology == str(1):
      imgalllist =\
          yasara.ShowWin("Custom","No of point",400,250,
          "Text",        50, 50,"*Select the  total number of reaction point",
          "NumberInput", 20, 80,"points",8,8,100,
          "Button",      150,200," O K")  
##counting the object present in the yasara window
      rimg=open(macrotarget+'/'+str(nameobj)+'images.log','w+')
      rimg.write((str(imgalllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
      rimg.close()
      if os.path.getsize(macrotarget+'/'+str(nameobj)+'images.log') == 0:
        yasara.ShowMessage("QM calculation failed. Must need the number of reaction points. Please restart the process") 
        os.remove(macrotarget+'/'+str(nameobj)+'procharge.log')
        yasara.plugin.end() 

      img = open(macrotarget+'/'+str(nameobj)+'images.log', "r")
      noimg= img.readlines()
      numeroimg= str((noimg[0]).strip('\n')) 

      i=0
      for i in range (0,atom):
      
          yasara.run("BFactorAtom "+str(i+1)+","+str(i+1))
          bfactor=yasara.run("BFactorAtom "+str(i+1))
          if i == 0:
            val= open(macrotarget+'/'+'bfactor.txt','w')
            val.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
            val.close()
          else:
            valread=open(macrotarget+'/'+'bfactor.txt','r')
            value=valread.readlines()
            valread.close()
            rewrite=open(macrotarget+'/'+'bfactor.txt','w')
            rewrite.writelines(value)
            rewrite.write('\n')
            rewrite.write(str(bfactor).replace('[','').replace(']',''))
            rewrite.close()
        
          i=i+1



##concatination of reactant xyz info with its b-factor value   
      combine =[]

      with open((macrotarget)+'/'+'bfactor.txt') as xh:
        with open((macrotarget)+'/'+'qm.txt') as yh:
          with open((macrotarget)+'/'+'QM_filter.txt',"w") as zh:
         #Read first file
             xlines = xh.readlines()
         #Read second file
             ylines = yh.readlines()
         #Combine content of both lists
         #combine = list(zip(ylines,xlines))
         #Write to third file
             for i in range(len(xlines)):
                line = ylines[i].strip('\n') + '    ' + xlines[i]
                zh.write(line)
#os.remove((macrotarget)+'/'+'reactant.txt')
    #os.remove((macrotarget)+'/'+'bfactor.txt')
    #yasara.run("DuplicateAll")
    #yasara.run("DelObj 1")
      yasara.run('BallStickObj all')
      yasara.run("LabelAll 'Do not update hydrogen after bond modification',Height=1.9,Color=Yellow,X=0,Y=19,Z=65")
    #yasara.ShowMessage("First select the atoms in the structure for modification")
    #yasara.run("wait continuebutton")
   # yasara.run('FixAtom all and not selected')
      yasara.ShowMessage("Please modify the atoms to build product molecule and then click continue")
      yasara.run("wait continuebutton")
      conopen=open(macrotarget+'/'+'check.inp','r')
      conopenread=conopen.read()
      conmodi=open(macrotarget+'/'+'constraint_atoms.inp','w+')
      conmodi.write(str(conopenread).replace('{C ','').replace(' C}',''))
      conmodi.close()
      with open(macrotarget+'/'+'constraint_atoms.inp', 'r') as fcon:
          for count, line in enumerate(fcon):
              pass
      icon=0
      countcon= (count+1)
    #f=(loop)
      for icon in range(0,countcon):
          connumero= open(macrotarget+'/'+'constraint_atoms.inp','r')
          consatom=connumero.readlines()
          consatom=str((consatom[icon]).strip('\n'))
          consatom=int(consatom)
          consatom=consatom+1
          consatom=str(consatom)
          yasara.run('FixAtom '+str(consatom))
          yasara.ShowMessage(str(consatom)+" atom will be fixed")
          icon=icon+1
      yasara.run('SelectRes con')
      yasara.run('FixAtom selected')
      yasara.ShowMessage("Geometry optimization is in progress..") 
    #yasara.run('UnselectAll')
    #yasara.run('MinStep 0.05')
      energy_minimization()
      #yasara.ExperimentMinimization()
      #yasara.Experiment("On")
      #yasara.Wait("ExpEnd")
      #yasara.run('DelObj simcell')
      yasara.ShowMessage("Charge calculation is in progress..")
##Calculating the charge of the product
      prochargeinfo=charge_calculation()#yasara.run('ChargeObj all')
      promod=open(macrotarget+'/'+str(nameobj)+'procharge.log','w')
      promod.write(str(prochargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']',''))
      promod.close()
      prochargef= open(macrotarget+'/'+str(nameobj)+'procharge.log','r')
      prochargeall=prochargef.readlines()
      procharge=float((prochargeall[0]).strip('\n'))
      procharge=round(procharge)
      print(procharge)

      proalllist =\
        yasara.ShowWin("Custom","INFORMATION",400,250,
        "NumberInput", 20, 88,"Charge",str(procharge),-1000,1000,
        "NumberInput", 180, 88,"Multiplicity",1,1,1000,
        "Button",      150,200," O K")  
##counting the object present in the yasara window
      pcharge=open(macrotarget+'/'+str(nameobj)+'procharge.log','w+')
      pcharge.write((str(proalllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
      pcharge.close()
      if os.path.getsize(macrotarget+'/'+str(nameobj)+'procharge.log') == 0:
        yasara.ShowMessage("Charge calculation failed, restart the process") 
        os.remove(macrotarget+'/'+str(nameobj)+'procharge.log')
        yasara.plugin.end() 
      else:
        print('ok')   

      pro_charge = open(macrotarget+'/'+str(nameobj)+'procharge.log', "r")
      productinfo= pro_charge.readlines()
      productcharge= str((productinfo[0]).strip('\n'))    
      productmultiplicity= str((productinfo[1]).strip('\n')) 


  ##counting the atom of product present in the yasara window
      proatom=yasara.run("Countatom all")
      prodeltext= open(macrotarget+'/'+'prodeltext.txt','w')
      prodeltext.write(str(proatom).replace('atom(s) match the selection.','').replace('[','').replace(']',''))
      prodeltext.close()
      p = open((macrotarget)+'/'+'prodeltext.txt', "r")
      pcontent = p.readlines()
      nopro=str((pcontent[0]).strip('\n').strip('[').strip(']'))
      p.close()
      atom=str(atom)
      os.remove((macrotarget)+'/'+'prodeltext.txt')
##checking the number of atom in product and reactant are same or not

      if nopro == atom :
      #yasara.run('JoinObj all,1')
        j=0
        nopro=int(nopro)
        for j in range (0,nopro):
            bfactor=yasara.run("BFactorAtom "+str(j+1))
            if j == 0:
              val= open(macrotarget+'/'+'product_bfactor.txt','w')
              val.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
              val.close()
            else:
              valread=open(macrotarget+'/'+'product_bfactor.txt','r')
              value=valread.readlines()
              valread.close()
              rewrite=open(macrotarget+'/'+'product_bfactor.txt','w')
              rewrite.writelines(value)
              rewrite.write('\n')
              rewrite.write(str(bfactor).replace('[','').replace(']','').replace('.0',''))
              rewrite.close()
        
            j=j+1 
      else:
       yasara.ShowMessage("WARNING! please see the terminal")
       print(nopro)
       print(atom)
       print("No. of atoms must be same for reactant and product")
       yasara.plugin.end()        


##Saving the xyz file of the product
      yasara.run("SaveXYZ all,"+str(macrotarget)+'/'+"QM_product.xyz,transform=Yes") 
##modifying the reactant.xyz file without hamparing the main file
      qmproductxyz=os.path.join(macrotarget,'QM_product.xyz')
      qmproducttxt=os.path.join(macrotarget,'QM_product.txt')
      with open(qmproductxyz, 'r') as fin:
          data = fin.read().splitlines(True)
      with open(qmproducttxt, 'w') as fout:
          fout.writelines(data[2:]) 
          fout.close()
   
##concatination of reactant xyz info with its b-factor value   
      procombine =[]
      
      with open(qmproducttxt) as xh:
        with open((macrotarget)+'/'+'product_bfactor.txt') as yh:
          with open((macrotarget)+'/'+'QM_product_filter.txt',"w") as zh:
       #Read first file
             xlines = xh.readlines()
         #Read second file
             ylines = yh.readlines()
         #Combine content of both lists
         #combine = list(zip(ylines,xlines))
         #Write to third file
             for i in range(len(xlines)):
                line = ylines[i].strip('\n') + '    ' + xlines[i]
                zh.write(line)

      yasara.run("clear")
      yasara.run("DelObj all")
      yasara.run('Loadxyz '+macrotarget+'/'+'QM.xyz')
      yasara.run('BallStickObj all')
      yasara.run('Loadxyz '+macrotarget+'/'+'QM_product.xyz')
      yasara.run('BallStickObj all')
      radius=yasara.run('RadiusObj 1')
      rd=open(macrotarget+'/'+'radius.txt','w+')
      rd.write(str(radius).replace('[','').replace(']','').replace('Object  1 (reactant) has a VdW radius of ','').replace('A from its geometric center',''))
      rd.close()
      fk=open(macrotarget+'/'+'radius.txt','r')
      r=fk.readline()
      r=str(r)
      r=float(r)
      len= 15
      y= r+len
      y=str(y)
      z=-r-len
      z=str(z)
#yasara.run('r=RadiusObj 1')
#yasara.run('len=15')
      yasara.run('MoveObj !1,X='+str(y))
      yasara.run('MoveObj 1,X='+str(z))
      yasara.run('ShowArrow Start=Point,X=-15,Y=0,Z=50,End=Point,X=15,Y=0,Z=50,Radius=1,Color=Yellow')
      yasara.run('ZoomAll Steps=0')
      yasara.run('Move Z=20')
      yasara.run('LabelObj 1,reactant,Color=Yellow,Y=5,Z=-5')
      yasara.run('LabelObj 2,product,Color=Yellow,Y=5,Z=-5')

      def sortLinesByColumn(readable, column, columnt_type):
          """Returns a list of strings (lines in readable file) in sorted order (based on column)"""
          lines = []

          for line in readable:
            # get the element in column based on which the lines are to be sorted
              column_element= columnt_type(line.split(' ')[column-1])
              lines.append((column_element, line))

          lines.sort()

          return [x[1] for x in lines]


      with open((macrotarget)+'/'+'QM_product_filter.txt') as f:
        # sort the lines based on column 1, and column 1 is type int
          sorted_lines = sortLinesByColumn(f, 1, int)
          k= open((macrotarget)+'/'+'QM_product_final.txt',"w")
          k.writelines(sorted_lines)
          k.close()

  #os.remove((macrotarget)+'/'+'product_filter.txt')
      proedit = open((macrotarget)+'/'+'QM_product_final.txt', "r")
      editfile = open((macrotarget)+'/'+'QM_product_filter.txt', "w")
      for line in proedit:
          if line.strip():
              editfile.write("\t".join(line.split()[1:]) + "\n")    
      proedit.close()
      editfile.close()
      os.remove((macrotarget)+'/'+'QM_product_final.txt')


      qmorcaproinp=open((macrotarget)+'/'+'QM_product_filter.txt')
      qmprodata=qmorcaproinp.read()
      qmorcaproinp.close()
      print(prodata)
      orca_geo_pro=open((macrotarget)+'/'+'QM_product.inp','w+')
      orca_geo_pro.write("!")
      orca_geo_pro.write(str(functional))
      orca_geo_pro.write(" ")
      orca_geo_pro.write(str(basis))
      orca_geo_pro.write(' Opt')
    #orca_geo_pro.write("\n%pal\n   nprocs ")
    #orca_geo_pro.write(str(processor))
    #orca_geo_pro.write('\nend')
      orca_geo_pro.write('\n%maxcore 101376\n%geom \nConstraints\n')
      orca_geo_pro.write(str(condata))
      orca_geo_pro.write('\nend\nend\n*xyz ')
      orca_geo_pro.write(str(productcharge))
      orca_geo_pro.write(" ")
      orca_geo_pro.write(str(productmultiplicity))
      orca_geo_pro.write("\n")
  #orca_geo_pro.write(str(reactdata))
      orca_geo_pro.write(str(qmprodata))
      orca_geo_pro.write("\n*")
      orca_geo_pro.close()
  


      yasara.ShowMessage("Geometry optimization is in progress..")  
      if mod == str(1) or mod == str(2): 
        print('check')
        os.system(orca+' QM_product.inp >QM_product.out')
      else:
        os.system('orca QM_product.inp >QM_product.out')




      yasara.ShowMessage("Geometry optimization is complete")
      tsinp=open((macrotarget)+'/'+'ts.inp','w+')
      tsinp.write('!')
      tsinp.write(str(functional))
      tsinp.write(' ')
      tsinp.write(str(basis))
      tsinp.write(' NEB-TS ')#FREQ')
    #tsinp.write("\n\n%pal\n   nprocs ")
    #tsinp.write(str(processor))
    #tsinp.write('\nend')
      tsinp.write('\n\n%neb\n\nNEB_End_XYZFile "QM_product.xyz"\n\nNImages ')
      tsinp.write(str(numeroimg))
      tsinp.write('\n\nend\n%geom \nConstraints\n')
      tsinp.write(str(condata))
      tsinp.write('\nend\nend\n*xyzfile ')
      tsinp.write(str(reactcharge))
      tsinp.write(' ')
      tsinp.write(str(reactmultiplicity))
      tsinp.write(' QM_reactant.xyz\n\n')
      tsinp.close()
      yasara.ShowMessage("Transition state calculation is in process..")
      os.chdir(pathYasara)
      os.chdir(macrotarget)
      time.sleep(5)
      if mod == str(1)or mod == str(2): 
        print('check')
        os.system(orca+' ts.inp >ts.out')
      else:
        os.system('orca ts.inp >ts.out')

    if os.path.isfile(macrotarget+'/'+'ts_MEP_trj.xyz') :
      trjlist =\
        yasara.ShowWin("Custom","Trjectory view",400,250,
         "Text", 20, 50, "Do you want to visualize trajectory?",
         "RadioButtons",2,1,
                        20, 100,"yes",
                        200,100,"no",
         "Button",      150,200," O K")
      attach= open((macrotarget)+'/'+'trjectory.txt','w+')
      attach.write((str(trjlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
      attach.close()  
      f = open((macrotarget)+'/'+'trjectory.txt', "r")
      content= f.readlines()
      a = str((content[0]).strip('\n'))   
      if a == str(1):
        if mod == str(1):
          os.rename(macrotarget+'/'+'ts_MEP_trj.xyz', macrotarget+'/'+'ts_MEP_final.xyz' )
        else:
           os.rename(macrotarget+'/'+'ts_MEP_trj.xyz', macrotarget+'/'+'ts_MEP_final.xyz' )     
    
        yasara.run('DelObj all')  
        yasara.run('Loadxyz '+macrotarget+'/'+'ts_MEP_final.xyz')
        yasara.run('BallStickObj all')
        obj=yasara.run("CountObj all")
        deltext= open(macrotarget+'/'+'deltext.txt','w')
        deltext.write(str(obj).replace('object(s) match the selection.','').replace('[','').replace(']',''))
        deltext.close()
        g = open((macrotarget)+'/'+'deltext.txt', "r")
        content = g.readlines()
        noobj=str((content[0]).strip('\n'))
        g.close()
        noobj=int(noobj)
        k=0
        yasara.run('ZoomAll Steps=20')
        yasara.run('HideObj all')
        for k in range(0,noobj):
            yasara.run('ShowObj '+str(k+1))
            yasara.run('BallStickObj all')
            yasara.run("wait continuebutton")
            if int(k+1) == noobj :
              print('done')
            else:
              yasara.run('DelObj '+str(k+1))
            k=k+1
        yasara.ShowMessage("Transition state calculation is complete and results are saved in: "+ macrotarget)
  
      else:
        yasara.ShowMessage("Transition state calculation is complete and results are saved in: "+ macrotarget)    

    elif remethodology == str(2):
      nameobj='QM_reactant'
      qmreactantout=os.path.join(macrotarget,"QM_reactant.out")
      qmorbital_energy=os.path.join(macrotarget,"QM_reactant_orbital_energy.txt")
      qmorbital_energy_finetxt= os.path.join(macrotarget,"QM_reactant_orbital_energy_fine.txt")
      qmorbital_energy_filtertxt= os.path.join(macrotarget,"QM_reactant_orbital_energy_filter.txt")
      qmorbital_energy_finaltxt= os.path.join(macrotarget,"QM_reactant_orbital_energy_final.txt")
      with open(qmreactantout,"r") as fin, open(qmorbital_energy,"w") as fout:
          string = 'ORBITAL ENERGIES'
          for line in fin:
              if string in line:
                  fout.write(line)
                  try: 
                      while '* MULLIKEN POPULATION ANALYSIS *' not in line:
                          line = next(fin)
                          fout.write((line).replace('--','').replace('*','').replace('MULLIKEN POPULATION ANALYSIS','').replace('ORBITAL ENERGIES',''))
                  except StopIteration:
                      pass  # ran out of file to read
      redit= open(qmorbital_energy,'r')
      reditdata=redit.read()
      rewrite=open(qmorbital_energy_finetxt,'w+')
      rewrite.write('check')
      rewrite.write(str(reditdata))
      rewrite.write('\n end')
      rewrite.close()
      with open(qmorbital_energy_finetxt, 'r') as ffin:
          fdata = ffin.read().splitlines(True)
      with open(qmorbital_energy_filtertxt,"w") as ffout:
         ffout.write("checkanion\n")
         ffout.writelines(fdata[1:])

      with open(qmorbital_energy_filtertxt,"r") as gfin, open(qmorbital_energy_finaltxt,"w") as gfout:
           string = 'ORBITAL ENERGIES'
           for line in gfin:
               if string in line:
                  gfout.write(line)
                  try: 
                     while ' end' not in line:
                         line = next(gfin)
                         gfout.write((line).replace('ORBITAL ENERGIES\n\n\n','').replace('  NO   OCC          E(Eh)            E(eV) ','').replace(' end',''))
                  except StopIteration:
                      pass  # ran out of file to read

      final= open (qmorbital_energy_finaltxt,"r+")
      finallines= final.readlines()[4:]
      final.seek(0)
      final.truncate()
      final.writelines(finallines)
      final.close()
      f = open(qmorbital_energy_finaltxt, "r")
      g = open(macrotarget+'/'+str(nameobj)+'_orbital_energy_dat.txt', "w")
      for line in f:
        if line.strip():
            g.write("\t".join(line.split()[1:]) + "\n")

      f.close()
      g.close()
        #os.remove(macrotarget+'/'+'orbital_energy.txt')
      bad_words = ['0.0000']
      with open(macrotarget+'/'+str(nameobj)+'_orbital_energy_dat.txt') as oldfile, open(macrotarget+'/'+str(nameobj)+'_HOMO_dat.txt', 'w') as newfile:
           for line in oldfile:
               if not any(bad_word in line for bad_word in bad_words):
                   newfile.write(line)

      fh = open(macrotarget+'/'+str(nameobj)+'_HOMO_dat.txt', "r")
      gh = open(macrotarget+'/'+str(nameobj)+'_HOMO_ev.txt', "w")
      for line in fh:
        if line.strip():
            gh.write("\t".join(line.split()[2:]) + "\n")

      fh.close()
      gh.close()
      if os.path.getsize(macrotarget+'/'+str(nameobj)+'_HOMO_ev.txt')== 0:
         yasara.ShowMessage("ORCA calculation failed. Please see the output file (.out) for more information.")
         yasara.plugin.end()
      else:
         print('ok')
      with open(macrotarget+'/'+str(nameobj)+'_HOMO_ev.txt', 'r') as fp:
          for count, line in enumerate(fp):
              pass
      count=count+1
      homoline=int(count-1)
      lumoline=int(count)
      f=open(macrotarget+'/'+str(nameobj)+'_orbital_energy_dat.txt')
      lines=f.readlines()
      homo=(lines[homoline])
      lumo=(lines[lumoline])
      energy=open(macrotarget+'/'+str(nameobj)+'_HOMO_lumo_dat.txt', "w")
      energy.write(str(homo))
      energy.write('\n')
      energy.write(str(lumo))
      energy.close()
      fe = open(macrotarget+'/'+str(nameobj)+'_HOMO_lumo_dat.txt', "r")
      ge = open(macrotarget+'/'+str(nameobj)+'_HOMO_lumo_ev.txt', "w")
      for line in fe:
        if line.strip():
            ge.write("\t".join(line.split()[2:]) + "\n")

      fe.close()
      ge.close() 
      with open(macrotarget+'/'+str(nameobj)+'_HOMO_lumo_ev.txt') as g:
          allenergy=g.readlines()
          homoenegy=float((allenergy[0]).strip('\n'))
          lumoenergy=float((allenergy[1]).strip('\n'))
      hlgap=lumoenergy-homoenegy  
      hlgap=round(hlgap,2)
      hlgap=str(hlgap)
      #os.remove(macrotarget+'/'+str(nameobj)+'_HOMO_lumo_dat.txt')
        #os.remove(macrotarget+'/'+'orbital_energy_dat.txt')
      #os.remove(macrotarget+'/'+str(nameobj)+'_HOMO_dat.txt')
      #os.remove(macrotarget+'/'+str(nameobj)+'_HOMO_ev.txt')
      #os.remove(macrotarget+'/'+str(nameobj)+'_orbital_energy.txt')
      #os.remove(macrotarget+'/'+str(nameobj)+'_orbital_energy_fine.txt')
      yasara.ShowMessage("HOMO LUMO energy difference is "+ str(hlgap)+" Eh") 
      yasara.plugin.end()

    elif remethodology == str(3):      
      if functional == 'RHF PM3':
         yasara.ShowMessage("PM3 method can not compute Hirshfeld charge population. Please use another basis set.") 
         yasara.plugin.end()     
      atomcharge=int(reactcharge)
      reactmultiplicity=int(reactmultiplicity)
      newmultiplicity=reactmultiplicity+1
      newmultiplicity=str(newmultiplicity)
      #cation chrage
      cationcharge=(atomcharge+1)
      cationcharge=str(cationcharge)
      anioncharge=(atomcharge-1)
      anioncharge=str(anioncharge)
      print(cationcharge)
      print(anioncharge)
      print(newmultiplicity)
      with open(str(macrotarget)+'/'+'QM_reactant.xyz', 'r') as fin:
          data = fin.read().splitlines(True)
      with open(str(macrotarget)+'/'+'QM_reactant.txt', 'w') as fout:
          fout.writelines(data[2:]) 
          fout.close()  
      orcamolinp=open((macrotarget)+'/'+'QM_reactant.txt')
      moldata=orcamolinp.read()
      orcamolinp.close()
      k= open(macrotarget+'/'+'QM_reactant_cation.inp','w')
      k.write('! ')
      k.write(str(functional))
      k.write(' ')
      k.write(str(basis))
      k.write(' Opt Hirshfeld')
      k.write('\n%maxcore 101376\n%geom \nConstraints\n')
      k.write(str(condata))
      k.write('\nend\nend\n*xyz ')
      k.write(str(cationcharge))
      k.write(' ')
      k.write(str(newmultiplicity))
      k.write('\n')
      k.write(str(moldata))
      k.write('\n*')
      k.close()
      os.chdir(pathYasara)
      os.chdir(macrotarget)  
      yasara.ShowMessage("orca is optimizing cation")  
      if mod == str(1) or mod == str(2): 
        print('check')
        os.system(orca+' QM_reactant_cation.inp >QM_reactant_cation.out')
      else:
        os.system('orca QM_reactant_cation.inp >QM_reactant_cation.out')
      
      
      orca_anion=open((macrotarget)+'/'+'QM_reactant_anion.inp','w+')
      orca_anion.write("! ")
      orca_anion.write(str(functional))
      orca_anion.write(" ")
      orca_anion.write(str(basis))
      orca_anion.write(' OPT Hirshfeld')
      orca_anion.write('\n%maxcore 101376\n%geom \nConstraints\n')
      orca_anion.write(str(condata))
      orca_anion.write('\nend\nend\n*xyz ')
      orca_anion.write(str(anioncharge))
      orca_anion.write(" ")
      orca_anion.write(str(newmultiplicity))
      orca_anion.write("\n")
      orca_anion.write(str(moldata))
      orca_anion.write('\n*')
      orca_anion.close()
      yasara.ShowMessage("orca is optimizing anion")
      nameobj= 'QM_reactant'
      if mod == str(1) or mod == str(2):
        os.chdir(macrotarget)
        os.system(orca+' QM_reactant_anion.inp >QM_reactant_anion.out')
      else:
        os.system('orca '+macrotarget+'/'+str(nameobj)+'_anion.inp >  '+macrotarget+'/'+str(nameobj)+'_anion.out')

      ###file defining
      qmreactantout=os.path.join(macrotarget,"QM_reactant.out")
      qmreactantanionout=os.path.join(macrotarget,"QM_reactant_anion.out")
      qmreactantcationout=os.path.join(macrotarget,"QM_reactant_cation.out")
      
      qmhirshfeld_charge_initialtxt=os.path.join(macrotarget,((nameobj)+'_hirshfeld_charge_initial.txt'))
      qmhirshfeld_charge_inital_filtertxt= os.path.join(macrotarget,((nameobj)+'hirshfeld_charge_inital_filter.txt'))
      qmhirshfeld_charge_inital_finaltxt= os.path.join(macrotarget,((nameobj)+'hirshfeld_charge_inital_final.txt'))
      qmhirshfeld_charge_aniontxt=os.path.join(macrotarget,((nameobj)+'hirshfeld_charge_anion.txt'))
      qmhirshfeld_charge_anion_filtertxt= os.path.join(macrotarget,((nameobj)+'hirshfeld_charge_anion_filter.txt'))
      qmhirshfeld_charge_anion_finaltxt= os.path.join(macrotarget,((nameobj)+'hirshfeld_charge_anion_final.txt'))
      qmhirshfeld_charge_cationtxt=os.path.join(macrotarget,((nameobj)+'hirshfeld_charge_cation.txt'))
      qmhirshfeld_charge_cation_filtertxt= os.path.join(macrotarget,((nameobj)+'hirshfeld_charge_cation_filter.txt'))
      qmhirshfeld_charge_cation_finaltxt= os.path.join(macrotarget,((nameobj)+'hirshfeld_charge_cation_final.txt'))      
      with open(qmreactantout,"r") as infin, open(qmhirshfeld_charge_initialtxt,"w") as infout:
           string = 'HIRSHFELD ANALYSIS'
           for line in infin:
               if string in line:
                  infout.write(line)
                  try: 
                     while 'TIMINGS' not in line:
                         line = next(infin)
                         infout.write(line)
                  except StopIteration:
                      pass  # ran out of file to read
        
      with open(qmreactantanionout,"r") as fin, open(qmhirshfeld_charge_aniontxt,"w") as fout:
           string = 'HIRSHFELD ANALYSIS'
           for line in fin:
               if string in line:
                  fout.write(line)
                  try: 
                     while 'TIMINGS' not in line:
                         line = next(fin)
                         fout.write(line)
                  except StopIteration:
                      pass  # ran out of file to read


      with open(qmreactantcationout,"r") as fin, open(qmhirshfeld_charge_cationtxt,"w") as fout:
           string = 'HIRSHFELD ANALYSIS'
           for line in fin:
               if string in line:
                  fout.write(line)
                  try: 
                     while 'TIMINGS' not in line:
                         line = next(fin)
                         fout.write(line)
                  except StopIteration:
                      pass  # ran out of file to read

      countfini= open(qmhirshfeld_charge_initialtxt, 'r')
      countdataini = countfini.read()
      inianoccurrences = countdataini.count("HIRSHFELD ANALYSIS")
      print(inianoccurrences)
      if inianoccurrences ==(2):
        with open(qmhirshfeld_charge_initialtxt, 'r') as fini:
            inidata = fini.read().splitlines(True)
        with open(qmhirshfeld_charge_inital_filtertxt,"w") as foutini:
           foutini.write("checkanion\n")
           foutini.writelines(inidata[1:])

        with open(qmhirshfeld_charge_inital_filtertxt,"r") as inifin, open(qmhirshfeld_charge_inital_finaltxt,"w") as inifout:
             string = 'HIRSHFELD ANALYSIS'
             for line in inifin:
                 if string in line:
                    inifout.write(line)
                    try: 
                       while 'TIMINGS' not in line:
                           line = next(inifin)
                           inifout.write(line)
                    except StopIteration:
                        pass  # ran out of file to read
        os.remove(qmhirshfeld_charge_inital_filtertxt)
      else:
        os.rename(macrotarget+'/'+str(nameobj)+'_hirshfeld_charge_initial.txt', macrotarget+'/'+str(nameobj)+'_hirshfeld_charge_initial_final.txt')

      countfanion= open(qmhirshfeld_charge_aniontxt, 'r')
      countdataanion = countfanion.read()
      anoccurrences = countdataanion.count("HIRSHFELD ANALYSIS")
      print(anoccurrences)
      if anoccurrences == (2):
        print('hello')
        with open(qmhirshfeld_charge_aniontxt, 'r') as fin:
            data = fin.read().splitlines(True)
        with open(qmhirshfeld_charge_anion_filtertxt,"w") as fout:
           fout.write("checkanion\n")
           fout.writelines(data[1:])

        with open(qmhirshfeld_charge_anion_filtertxt,"r") as fin, open(qmhirshfeld_charge_anion_finaltxt,"w") as fout:
             string = 'HIRSHFELD ANALYSIS'
             for line in fin:
                 if string in line:
                    fout.write(line)
                    try: 
                       while 'TIMINGS' not in line:
                           line = next(fin)
                           fout.write(line)
                    except StopIteration:
                        pass  # ran out of file to read
        os.remove(qmhirshfeld_charge_anion_filtertxt)
      else:
        print('failed')
        yasara.plugin.end()

      countfcat= open(macrotarget+'/'+str(nameobj)+'_hirshfeld_charge_cation.txt', 'r')
      countdatacat = countfcat.read()
      catoccurrences = countdatacat.count("HIRSHFELD ANALYSIS")
      print(catoccurrences)
      if catoccurrences == (2):
        print('hello')
        with open(qmhirshfeld_charge_cationtxt, 'r') as fin:
            data = fin.read().splitlines(True)
        with open(qmhirshfeld_charge_cation_filtertxt,"w") as fout:
           fout.write("checkcation\n")
           fout.writelines(data[1:])

        with open(qmhirshfeld_charge_cation_filtertxt,"r") as fin, open(qmhirshfeld_charge_cation_finaltxt,"w") as fout:
             string = 'HIRSHFELD ANALYSIS'
             for line in fin:
                 if string in line:
                    fout.write(line)
                    try: 
                       while 'TIMINGS' not in line:
                           line = next(fin)
                           fout.write(line)
                    except StopIteration:
                        pass  # ran out of file to read
        os.remove(qmhirshfeld_charge_cation_filtertxt)
      else:
        print('failed')
        yasara.plugin.end()
        #os.rename(qmhirshfeld_charge_cationtxt, qmhirshfeld_charge_cation_finaltxt)

      with open(qmhirshfeld_charge_cation_finaltxt, 'r') as fin:
          data = fin.read().splitlines(True)
      with open(macrotarget+'/'+str(nameobj)+'_cation_charge.txt',"w") as fout:
         fout.writelines(data[7:-5])
      with open(qmhirshfeld_charge_anion_finaltxt, 'r') as fin:
          data = fin.read().splitlines(True)
      with open(macrotarget+'/'+str(nameobj)+'_anion_charge.txt',"w") as fout:
         fout.writelines(data[7:-5])
      with open(qmhirshfeld_charge_inital_finaltxt, 'r') as initialfin:
          alldata = initialfin.read().splitlines(True)
      with open(macrotarget+'/'+str(nameobj)+'_initial_charge.txt',"w") as initialfout:
         initialfout.writelines(alldata[7:-5])

      #os.remove(macrotarget+'/'+str(nameobj)+'_hirshfeld_charge_cation_final.txt')
      #os.remove(macrotarget+'/'+str(nameobj)+'_hirshfeld_charge_anion_final.txt')
      #os.remove(macrotarget+'/'+str(nameobj)+'_hirshfeld_charge_anion.txt')
      #os.remove(macrotarget+'/'+str(nameobj)+'_hirshfeld_charge_cation.txt')



      a = open(macrotarget+'/'+str(nameobj)+'_initial_charge.txt', "r")
      b = open(macrotarget+'/'+str(nameobj)+'_initial_hirshfeld_charge.txt', "w")
      for line in a:
          if line.strip():
              b.write("\t".join(line.split()[2:-1]) + "\n")

      a.close()
      b.close()

      f = open(macrotarget+'/'+str(nameobj)+'_anion_charge.txt', "r")
      g = open(macrotarget+'/'+str(nameobj)+'_anion_hirshfeld_charge.txt', "w")
      for line in f:
          if line.strip():
              g.write("\t".join(line.split()[2:-1]) + "\n")

      f.close()
      g.close()

      k = open(macrotarget+'/'+str(nameobj)+'_cation_charge.txt', "r")
      l = open(macrotarget+'/'+str(nameobj)+'_cation_hirshfeld_charge.txt', "w")
      for line in k:
          if line.strip():
              l.write("\t".join(line.split()[2:-1]) + "\n")

      k.close()
      l.close()
      
      m = open(macrotarget+'/'+str(nameobj)+'_anion_charge.txt', "r")
      n = open(macrotarget+'/'+str(nameobj)+'_atomname.txt', "w")
      for line in m:
          if line.strip():
              n.write("\t".join(line.split()[0:-2]) + "\n")

      m.close()
      n.close()
      if os.path.getsize(macrotarget+'/'+str(nameobj)+'_cation_hirshfeld_charge.txt') == 0 or os.path.getsize(macrotarget+'/'+str(nameobj)+'_anion_hirshfeld_charge.txt') == 0:
         yasara.ShowMessage("ORCA failed to compute. Please see the output files (.out) for more information")
         yasara.plugin.end()
      else:
         print('ok')
      with open(macrotarget+'/'+str(nameobj)+'_cation_hirshfeld_charge.txt', 'r') as fp:
          for fcount, line in enumerate(fp):
              pass
      
      fcount= (fcount+1)
      i=0
      #f=(loop)
      for i in range(0,fcount):
         iniread=open(macrotarget+'/'+str(nameobj)+'_initial_hirshfeld_charge.txt','r')
         hirshfeldinicharge= iniread.readlines()
         atomhirshfeldinicharge=str(((hirshfeldinicharge[i]).strip('\n'))) 
         atomhirshfeldinicharge=float(atomhirshfeldinicharge)

         read=open(macrotarget+'/'+str(nameobj)+'_cation_hirshfeld_charge.txt','r')
         hirshfeldcationcharge= read.readlines()
         atomhirshfeldcationcharge=str(((hirshfeldcationcharge[i]).strip('\n'))) 
         atomhirshfeldcationcharge=float(atomhirshfeldcationcharge)
         readanion=open(macrotarget+'/'+str(nameobj)+'_anion_hirshfeld_charge.txt','r')
         hirshfeldanionchargeanion= readanion.readlines()
         atomhirshfeldanioncharge=str(((hirshfeldanionchargeanion[i]).strip('\n'))) 
         atomhirshfeldanioncharge=float(atomhirshfeldanioncharge)
         #fukuifunction=float(((atomhirshfeldanioncharge)+(atomhirshfeldcationcharge)))
         ele=float((atomhirshfeldcationcharge)-(atomhirshfeldinicharge))
         nucl=float((atomhirshfeldinicharge)-(atomhirshfeldanioncharge))
         #fukuifunction=float((ele-nucl))
         fukuifunction=float(((atomhirshfeldanioncharge)-(atomhirshfeldcationcharge))/2)
         #fukuifunction=float((atomhirshfeldcationcharge)-(atomhirshfeldinicharge))
         #fukuifunction=float((atomhirshfeldinicharge)-(atomhirshfeldanioncharge))
         #fukuifunction=str(fukuifunction)
         fukuifunction=round(fukuifunction,3)
         fukuifunction=str(fukuifunction)
         yasara.run('ZoomAll Steps=10')
         yasara.run('LabelAtom '+str(i+1)+',Format='+str(fukuifunction)+',Height=0.2,Color=Black     ,X=0.0,Y=0.0,Z=0.0')
         yasara.run("BFactorAtom "+str(i+1)+","+str(fukuifunction))
         if i == 0:
           val= open(macrotarget+'/'+str(nameobj)+'_condensed_fukui.txt','w')
           val.write(str(fukuifunction).replace('[','').replace(']',''))
           val.close()
         else:
           valread=open(macrotarget+'/'+str(nameobj)+'_condensed_fukui.txt','r')
           value=valread.readlines()
           valread.close()
           rewrite=open(macrotarget+'/'+str(nameobj)+'_condensed_fukui.txt','w')
           rewrite.writelines(value)
           rewrite.write('\n')
           rewrite.write(str(fukuifunction).replace('[','').replace(']',''))
           rewrite.close()
    
      procombine =[]

      with open((macrotarget)+'/'+str(nameobj)+'_condensed_fukui.txt') as xh:
        with open((macrotarget)+'/'+str(nameobj)+'_atomname.txt') as yh:
          with open((macrotarget)+'/'+str(nameobj)+'_fukuifunction_results.txt',"w") as zh:
       #Read first file
             xlines = xh.readlines()
         #Read second file
             ylines = yh.readlines()
         #Combine content of both lists
         #combine = list(zip(ylines,xlines))
         #Write to third file
             for i in range(len(xlines)):
                line = ylines[i].strip('\n') + '    ' + xlines[i]
                zh.write(line)

      os.remove(macrotarget+'/'+str(nameobj)+'_condensed_fukui.txt')
      os.remove((macrotarget)+'/'+str(nameobj)+'_atomname.txt')
      yasara.ShowMessage("Fukui function calculation is complete")
      yasara.run("saveYOB all,"+macrotarget+"/"+str(nameobj)+".yob")
    else:
      #yasara.ShowMessage("check your structure")
      print('check your structure') 


    #else : 
      #yasara.ShowMessage("QM calculation failed. Please check output(.out) file for more information ") 
######## for single point calculation
elif method == 'ORCA' and methodology == str(1) or methodology == str(2) or methodology == str(4) or methodology == str(5) or methodology ==str(6) or methodology ==str(7) or methodology ==str(10):
  obj=yasara.run("CountObj all")
  deltext= open(macrotarget+'/'+'deltext.txt','w')
  deltext.write(str(obj).replace('object(s) match the selection.','').replace('[','').replace(']',''))
  deltext.close()
  g = open((macrotarget)+'/'+'deltext.txt', "r")
  content = g.readlines()
  noobj=str((content[0]).strip('\n'))
  g.close()


  if noobj== str(0):
    
    yasara.ShowMessage("Please build your molecule and then click continue")
    yasara.run("wait continuebutton")
    # reobj=yasara.run("CountObj all")
    # redeltext= open(macrotarget+'/'+'redeltext.txt','w')
    # redeltext.write(str(reobj).replace('object(s) match the selection.','').replace('[','').replace(']',''))
    # redeltext.close()
    # reg = open((macrotarget)+'/'+'redeltext.txt', "r")
    # recontent = reg.readlines()
    # renoobj=str((recontent[0]).strip('\n'))
    # reg.close()
    # if renoobj== 0 :
      # yasara.ShowMessage("QM calculation will be failed. Please load a structure")
      # os.remove(macrotarget+'/'+'redeltext.txt')
      # yasara.run("wait continuebutton")
    # else:
      # print('ok')
 
    yasara.run('ForceField AMBER03,SetPar=Yes')
  ###charge of the  molecule
    chargeinfo=charge_calculation()#yasara.run('ChargeObj all')
    yasara.run("SaveXYZ all,"+str(macrotarget)+'/'+str(nameobj)+".xyz,transform=Yes")
    cmod=open(macrotarget+'/'+str(nameobj)+'charge.log','w')
    cmod.write(str(chargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']',''))
    cmod.close()
    if os.path.getsize(macrotarget+'/'+str(nameobj)+'charge.log')== 0:
      yasara.ShowMessage("QM calculation will be failed. Please load a structure")
      os.remove(macrotarget+'/'+'redeltext.txt')
      yasara.run("wait continuebutton")
      yasara.run('ForceField AMBER03,SetPar=Yes')
  ###charge of the  molecule
      chargeinfo=charge_calculation()#yasara.run('ChargeObj all')
      yasara.run("SaveXYZ all,"+str(macrotarget)+'/'+str(nameobj)+".xyz,transform=Yes")
      cmod=open(macrotarget+'/'+str(nameobj)+'charge.log','w')
      cmod.write(str(chargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']',''))
      cmod.close()
    else:
      print('ok')  
    chargef= open(macrotarget+'/'+str(nameobj)+'charge.log','r')
    chargeall=chargef.readlines()
    charge=float((chargeall[0]).strip('\n'))
    charge=round(charge)
    print(charge)
####################################tempo section

        
####temposection

    
  else:
    yasara.ShowMessage("Please select your molecule by selectbox or join object all and then select all atoms")
    yasara.run("wait continuebutton")
    counts=yasara.run('CountAtom selected')
    countselect= open(macrotarget+'/'+'checkselect.txt','w')
    countselect.write(str(counts).replace('object(s) match the selection.','').replace('[','').replace(']','').replace("'",""))
    countselect.close()
    ck=os.path.getsize(macrotarget+'/'+'checkselect.txt')
    print(ck)
    if ck== 1:
       yasara.ShowMessage("Make sure that you have selected the object")
       yasara.run("wait continuebutton")      
    else:
       print('OK')

    nome=yasara.run('NameObj selected') 
    redeltext= open(macrotarget+'/'+'nome.txt','w')
    redeltext.write(str(nome).replace('object(s) match the selection.','').replace('[','').replace(']','').replace("'","").replace(', ','_'))
    redeltext.close()
    reg = open((macrotarget)+'/'+'nome.txt', "r")
    recontent = reg.readlines()
    nome=str((recontent[0]).strip('\n'))
    reg.close()
    print(nome)
    nameobj=str(nameobj)+"_"+str(nome)
    yasara.run("SaveSce "+str(macrotarget)+'/'+str(nameobj)+"_ini.sce")
    yasara.run('NumberObj selected,1')
    yasara.run('JoinObj all,1')
    yasara.run('Delatom all and not selected')
    yasara.run("SaveSce "+str(macrotarget)+'/'+str(nameobj)+"_ini.sce")
    chargeinfo=charge_calculation()#yasara.run('ChargeObj all')
    yasara.run("LoadSce "+str(macrotarget)+'/'+str(nameobj)+"_ini.sce")
    yasara.run("SaveSce "+str(macrotarget)+'/'+str(nameobj)+"_select.sce")
    yasara.run("SaveXYZ all,"+str(macrotarget)+'/'+str(nameobj)+".xyz,transform=Yes")
    yasara.run("SaveXYZ all,"+str(macrotarget)+'/'+str(nameobj)+"_ini.xyz,transform=Yes")
    #yasara.run('Clear')
    #yasara.run('Loadxyz '+(macrotarget)+'/'+str(nameobj)+'.xyz')
    #yasara.run('JoinObj all,1')
    #yasara.run("SaveXYZ Selected,"+str(macrotarget)+'/'+str(nameobj)+".xyz,transform=Yes")

    yasara.run('Clear')
    yasara.run('LoadSce '+str(macrotarget)+'/'+str(nameobj)+'_ini.sce,Settings=No')    
    
    
    #yasara.ShowMessage("Please select your molecule by selectbox or join object all and then select all atoms")
    #yasara.run("wait continuebutton")
    yasara.run('ForceField AMBER03,SetPar=Yes')
  ###charge of the  molecule
    
   # yasara.run("SaveXYZ Selected,"+str(macrotarget)+'/'+str(nameobj)+".xyz,transform=Yes")
    cmod=open(macrotarget+'/'+str(nameobj)+'charge.log','w')
    cmod.write(str(chargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']',''))
    cmod.close()
    if os.path.getsize(macrotarget+'/'+str(nameobj)+'charge.log')== 0:
      yasara.ShowMessage("QM calculation  will be failed. Please select a structure.")
      #os.remove(macrotarget+'/'+'redeltext.txt')
      yasara.run("wait continuebutton")
      nome=yasara.run('NameObj selected')
      print('ok')    
      redeltext= open(macrotarget+'/'+'nome.txt','w')
      redeltext.write(str(nome).replace('object(s) match the selection.','').replace('[','').replace(']','').replace("'","").replace(', ','_'))
      redeltext.close()
      reg = open((macrotarget)+'/'+'nome.txt', "r")
      recontent = reg.readlines()
      nome=str((recontent[0]).strip('\n'))
      reg.close()
      print(nome)
      nameobj=str(nameobj)+"_"+str(nome)    
      yasara.run("SaveSce "+str(macrotarget)+'/'+str(nameobj)+"_ini.sce")
      yasara.run('NumberObj selected,1')
      yasara.run('JoinObj all,1')
      yasara.run('Delatom all and not selected')
      chargeinfo=charge_calculation()#yasara.run('ChargeObj all')
      yasara.run("SaveSce "+str(macrotarget)+'/'+str(nameobj)+"_select.sce")
      yasara.run("SaveXYZ all,"+str(macrotarget)+'/'+str(nameobj)+".xyz,transform=Yes")
      yasara.run("SaveXYZ all,"+str(macrotarget)+'/'+str(nameobj)+"_ini.xyz,transform=Yes")

      yasara.run('Clear')
      yasara.run('LoadSce '+str(macrotarget)+'/'+str(nameobj)+'_ini.sce,Settings=No')    
    
    
    #yasara.ShowMessage("Please select your molecule by selectbox or join object all and then select all atoms")
    #yasara.run("wait continuebutton")
      yasara.run('ForceField AMBER03,SetPar=Yes')
  ###charge of the  molecule
      cmod=open(macrotarget+'/'+str(nameobj)+'charge.log','w')
      cmod.write(str(chargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']',''))
      cmod.close()
     
    chargef= open(macrotarget+'/'+str(nameobj)+'charge.log','r')
    chargeall=chargef.readlines()
    charge=float((chargeall[0]).strip('\n'))
    charge=round(charge)
    print(charge)    
  
  alllist =\
    yasara.ShowWin("Custom","INFORMATION",400,250,
    "NumberInput", 20, 88,"Charge",str(charge),-1000,1000,
    "NumberInput", 180, 88,"Multiplicity",1,1,1000,
    "Button",      150,200," O K")  
##counting the object present in the yasara window
  charge=open(macrotarget+'/'+str(nameobj)+'charge.log','w+')
  charge.write((str(alllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
  charge.close()
  if os.path.getsize(macrotarget+'/'+str(nameobj)+'charge.log') == 0:
    yasara.ShowMessage("Charge calculation failed, restart the process") 
    os.remove(macrotarget+'/'+str(nameobj)+'charge.log')
    yasara.plugin.end() 
  else:
    print('ok')   

  react_charge = open(macrotarget+'/'+str(nameobj)+'charge.log', "r")
  reactinfo= react_charge.readlines()
  reactcharge= str((reactinfo[0]).strip('\n'))    
  reactmultiplicity= str((reactinfo[1]).strip('\n'))
##modifying the reactant.xyz file without hamparing the main file
  with open(str(macrotarget)+'/'+str(nameobj)+'.xyz', 'r') as fin:
      data = fin.read().splitlines(True)
  with open(str(macrotarget)+'/'+str(nameobj)+'.txt', 'w') as fout:
      fout.writelines(data[2:]) 
      fout.close()  
##for methodology single point charge and homo-lumo difference calculation
  if methodology == str(1) or  methodology ==str(6):
    orcamolinp=open((macrotarget)+'/'+str(nameobj)+'.txt')
    moldata=orcamolinp.read()
    orcamolinp.close()
    orca_sp=open((macrotarget)+'/'+str(nameobj)+'.inp','w+')
    orca_sp.write("! SP ")
    orca_sp.write(str(functional))
    orca_sp.write(" ")
    orca_sp.write(str(basis))
    orca_sp.write(" ")
   # orca_sp.write("\n%pal\n   nprocs ")
    #orca_sp.write(str(processor))
   # orca_sp.write('\nend')
    orca_sp.write("\n\n%maxcore 20480\n\n* xyz  ")
    orca_sp.write(str(reactcharge))
    orca_sp.write(" ")
    orca_sp.write(str(reactmultiplicity))
    orca_sp.write("\n")
    orca_sp.write(str(moldata))
    orca_sp.write('\n*')
    orca_sp.close()
    yasara.ShowMessage("orca is optimizing single point energies")
    if mod == str(1) or mod == str(2):
      os.chdir(macrotarget)
      os.system(orca+' '+str(nameobj)+'.inp >  '+str(nameobj)+'.out')
    else:
      
      os.system('orca '+macrotarget+'/'+str(nameobj)+'.inp >  '+macrotarget+'/'+str(nameobj)+'.out')
      
    #yasara.ShowMessage("Single point energy calculation is complete and results are saved in: "+ macrotarget)
    if os.path.isfile ((macrotarget+'/'+str(nameobj)+'_property.txt')):
      yasara.ShowMessage("Single point energy calculation is complete and results are saved in: "+ macrotarget)
      
    else:
      yasara.ShowMessage("Single point energy calculation failed") 
      yasara.plugin.end()
    if methodology == str(1):
      scfline= open(macrotarget+'/'+str(nameobj)+'_property.txt')
      for line in scfline:
          if "SCF Energy:" in line:
             print(line)
             line=str(line).strip("\n").strip("  ")
             yasara.ShowMessage(str(line)+' Eh')
             ####temposection
             gi=open(str(macrotarget)+'/'+str(nameobj)+'.xyz', 'r') 
             gidata=gi.readlines()
             fline=(((gidata[0]).strip('\n'))) 
             secine=(((gidata[1]).strip('\n'))) 
             gi.close()
             with open(str(macrotarget)+'/'+str(nameobj)+'.xyz', 'r') as fin:
                 data = fin.read().splitlines(True)
    
             with open(str(macrotarget)+'/'+str(nameobj)+'.txt', 'w') as fout:
                 fout.writelines(data[2:]) 
                 fout.close() 
             fi=open(str(macrotarget)+'/'+str(nameobj)+'.txt')
             fidata=fi.read()
             fo=open(str(macrotarget)+'/'+str(nameobj)+'_finalstructure.xyz','w+')
             fo.write(str(fline))
             fo.write('\n')
             fo.write(str(secine))
             fo.write(' ')
             fo.write((str(line)).replace('SCF Energy:      ',''))
             fo.write('\n')
             fo.write(fidata)
             fo.close()
              ####temposection
    else:
        print('check')
        orbitalenergytxt= os.path.join(macrotarget,((nameobj)+'_orbital_energy.txt'))
        with open(macrotarget+"/"+str(nameobj)+'.out',"r") as fin, open(orbitalenergytxt,"w") as fout:
            string = 'ORBITAL ENERGIES'
            for line in fin:
                if string in line:
                    fout.write(line)
                    try: 
                        while '* MULLIKEN POPULATION ANALYSIS *' not in line:
                            line = next(fin)
                            fout.write((line).replace('--','').replace('*','').replace('MULLIKEN POPULATION ANALYSIS','').replace('ORBITAL ENERGIES',''))
                    except StopIteration:
                        pass  # ran out of file to read
        final= open (orbitalenergytxt,"r+")
        finallines= final.readlines()[4:]
        final.seek(0)
        final.truncate()
        final.writelines(finallines)
        final.close()
        f = open(orbitalenergytxt, "r")
        g = open(macrotarget+'/'+str(nameobj)+'_orbital_energy_dat.txt', "w")
        for line in f:
          if line.strip():
              g.write("\t".join(line.split()[1:]) + "\n")

        f.close()
        g.close()
        #os.remove(macrotarget+'/'+'orbital_energy.txt')
        bad_words = ['0.0000']
        with open(macrotarget+'/'+str(nameobj)+'_orbital_energy_dat.txt') as oldfile, open(macrotarget+'/'+str(nameobj)+'_HOMO_dat.txt', 'w') as newfile:
             for line in oldfile:
                 if not any(bad_word in line for bad_word in bad_words):
                     newfile.write(line)

        fh = open(macrotarget+'/'+str(nameobj)+'_HOMO_dat.txt', "r")
        gh = open(macrotarget+'/'+str(nameobj)+'_HOMO_ev.txt', "w")
        for line in fh:
          if line.strip():
              gh.write("\t".join(line.split()[2:]) + "\n")

        fh.close()
        gh.close()
        if os.path.getsize(macrotarget+'/'+str(nameobj)+'_HOMO_ev.txt')== 0:
           yasara.ShowMessage("ORCA calculation failed. Please see the output file (.out) for more information.")
           yasara.plugin.end()
        else:
           print('ok')
        with open(macrotarget+'/'+str(nameobj)+'_HOMO_ev.txt', 'r') as fp:
            for count, line in enumerate(fp):
                pass
        count=count+1
        homoline=int(count-1)
        lumoline=int(count)
        f=open(macrotarget+'/'+str(nameobj)+'_orbital_energy_dat.txt')
        lines=f.readlines()
        homo=(lines[homoline])
        lumo=(lines[lumoline])
        energy=open(macrotarget+'/'+str(nameobj)+'_HOMO_lumo_dat.txt', "w")
        energy.write(str(homo))
        energy.write('\n')
        energy.write(str(lumo))
        energy.close()
        fe = open(macrotarget+'/'+str(nameobj)+'_HOMO_lumo_dat.txt', "r")
        ge = open(macrotarget+'/'+str(nameobj)+'_HOMO_lumo_ev.txt', "w")
        for line in fe:
          if line.strip():
              ge.write("\t".join(line.split()[2:]) + "\n")

        fe.close()
        ge.close() 
        with open(macrotarget+'/'+str(nameobj)+'_HOMO_lumo_ev.txt') as g:
            allenergy=g.readlines()
            homoenegy=float((allenergy[0]).strip('\n'))
            lumoenergy=float((allenergy[1]).strip('\n'))
        hlgap=lumoenergy-homoenegy  
        hlgap=round(hlgap,2)
        hlgap=str(hlgap)
        os.remove(macrotarget+'/'+str(nameobj)+'_HOMO_lumo_dat.txt')
        #os.remove(macrotarget+'/'+'orbital_energy_dat.txt')
        os.remove(macrotarget+'/'+str(nameobj)+'_HOMO_dat.txt')
        os.remove(macrotarget+'/'+str(nameobj)+'_HOMO_ev.txt')
        os.remove(macrotarget+'/'+str(nameobj)+'_orbital_energy.txt')
        yasara.ShowMessage("HOMO LUMO energy difference is "+ str(hlgap)+" Eh") 
##for methodology geometry optimization
  elif methodology == str(2) or methodology == str(10):  
    orcamolinp=open((macrotarget)+'/'+str(nameobj)+'.txt')
    moldata=orcamolinp.read()
    orcamolinp.close()
    orca_geo=open((macrotarget)+'/'+str(nameobj)+'.inp','w+')
    orca_geo.write("! ")
    orca_geo.write(str(functional))
    orca_geo.write(" ")
    orca_geo.write(str(basis))
    orca_geo.write(" ")
    orca_geo.write('OPT Hirshfeld')
    #orca_geo.write("\n%pal\n   nprocs ")
    #orca_geo.write(str(processor))
    #orca_geo.write('\nend')
    orca_geo.write("\n\n* xyz  ")
    orca_geo.write(str(reactcharge))
    orca_geo.write(" ")
    orca_geo.write(str(reactmultiplicity))
    orca_geo.write("\n")
    orca_geo.write(str(moldata))
    orca_geo.write('\n*')
    orca_geo.close()
    yasara.ShowMessage("orca is optimizing the geometry")
    
    if mod == str(1) or mod == str(2):
      os.chdir(macrotarget)
      os.system(orca+' '+str(nameobj)+'.inp >  '+str(nameobj)+'.out')
    else:
      os.system('orca '+macrotarget+'/'+str(nameobj)+'.inp >  '+macrotarget+'/'+str(nameobj)+'.out')
    
    yasara.run('Clear')
    yasara.run('Loadxyz '+macrotarget+'/'+str(nameobj)+'.xyz')
    yasara.ShowMessage("Geometry optimization is complete and results are saved in: "+ macrotarget)
##########fukui function calculation####
    if methodology == str(10):
      #yasara.run("Delobj all and not selected")
      atomcharge=int(reactcharge)
      reactmultiplicity=int(reactmultiplicity)
      newmultiplicity=reactmultiplicity+1
      newmultiplicity=str(newmultiplicity)
      #cation chrage
      cationcharge=(atomcharge+1)
      cationcharge=str(cationcharge)
      anioncharge=(atomcharge-1)
      anioncharge=str(anioncharge)
      print(cationcharge)
      print(anioncharge)
      print(newmultiplicity)

##geometry optimixation of cation
      orca_cat=open((macrotarget)+'/'+str(nameobj)+'_cation.inp','w+')
      orca_cat.write("! ")
      orca_cat.write(str(functional))
      orca_cat.write("  ")
      orca_cat.write(str(basis))
      orca_cat.write(' OPT Hirshfeld')
      orca_cat.write("\n\n* xyz  ")
      orca_cat.write(str(cationcharge))
      orca_cat.write(" ")
      orca_cat.write(str(newmultiplicity))
      orca_cat.write("\n")
      orca_cat.write(str(moldata))
      orca_cat.write('\n*')
      orca_cat.close()
      yasara.ShowMessage("orca is optimizing cation")
    
      if mod == str(1) or mod == str(2):
        os.chdir(macrotarget)
        os.system(orca+' '+str(nameobj)+'_cation.inp >  '+str(nameobj)+'_cation.out')
      else:
        os.system('orca '+macrotarget+'/'+str(nameobj)+'_cation.inp >  '+macrotarget+'/'+str(nameobj)+'_cation.out')

##geometry optimixation of anion
      orca_anion=open((macrotarget)+'/'+str(nameobj)+'_anion.inp','w+')
      orca_anion.write("! ")
      orca_anion.write(str(functional))
      orca_anion.write(" ")
      orca_anion.write(str(basis))
      orca_anion.write(' OPT Hirshfeld')
      orca_anion.write("\n\n* xyz  ")
      orca_anion.write(str(anioncharge))
      orca_anion.write(" ")
      orca_anion.write(str(newmultiplicity))
      orca_anion.write("\n")
      orca_anion.write(str(moldata))
      orca_anion.write('\n*')
      orca_anion.close()
      yasara.ShowMessage("orca is optimizing anion")
    
      if mod == str(1) or mod == str(2):
        os.chdir(macrotarget)
        os.system(orca+' '+str(nameobj)+'_anion.inp >  '+str(nameobj)+'_anion.out')
      else:
        os.system('orca '+macrotarget+'/'+str(nameobj)+'_anion.inp >  '+macrotarget+'/'+str(nameobj)+'_anion.out')
      
      hirshfeld_charge_initialtxt=os.path.join(macrotarget,((nameobj)+'_hirshfeld_charge_initial.txt'))
      nameobjout=os.path.join(macrotarget,((nameobj)+".out"))
      nameobjanionout=os.path.join(macrotarget,((nameobj)+"_anion.out"))
      nameobjcationout=os.path.join(macrotarget,((nameobj)+"_cation.out"))
      hirshfeld_charge_aniontxt=os.path.join(macrotarget,((nameobj)+'_hirshfeld_charge_anion.txt'))
      hirshfeld_charge_anion_filtertxt= os.path.join(macrotarget,((nameobj)+'_hirshfeld_charge_anion_filter.txt'))
      hirshfeld_charge_anion_finaltxt= os.path.join(macrotarget,((nameobj)+'_hirshfeld_charge_anion_final.txt'))      
      hirshfeld_charge_cationtxt=os.path.join(macrotarget,((nameobj)+'_hirshfeld_charge_cation.txt'))
      hirshfeld_charge_cation_filtertxt= os.path.join(macrotarget,((nameobj)+'_hirshfeld_charge_cation_filter.txt'))
      hirshfeld_charge_cation_finaltxt= os.path.join(macrotarget,((nameobj)+'_hirshfeld_charge_cation_final.txt'))
      hirshfeld_charge_inital_filtertxt= os.path.join(macrotarget,((nameobj)+'_hirshfeld_charge_inital_filter.txt'))
      hirshfeld_charge_initial_finaltxt=os.path.join(macrotarget,((nameobj)+'_hirshfeld_charge_initial_final.txt'))
      
      
      with open(nameobjout,"r") as infin, open(hirshfeld_charge_initialtxt,"w") as infout:
           string = 'HIRSHFELD ANALYSIS'
           for line in infin:
               if string in line:
                  infout.write(line)
                  try: 
                     while 'TIMINGS' not in line:
                         line = next(infin)
                         infout.write(line)
                  except StopIteration:
                      pass  # ran out of file to read        
      with open(nameobjanionout,"r") as fin, open(hirshfeld_charge_aniontxt,"w") as fout:
           string = 'HIRSHFELD ANALYSIS'
           for line in fin:
               if string in line:
                  fout.write(line)
                  try: 
                     while 'TIMINGS' not in line:
                         line = next(fin)
                         fout.write(line)
                  except StopIteration:
                      pass  # ran out of file to read


      with open(nameobjcationout,"r") as fin, open(hirshfeld_charge_cationtxt,"w") as fout:
           string = 'HIRSHFELD ANALYSIS'
           for line in fin:
               if string in line:
                  fout.write(line)
                  try: 
                     while 'TIMINGS' not in line:
                         line = next(fin)
                         fout.write(line)
                  except StopIteration:
                      pass  # ran out of file to read



      with open(hirshfeld_charge_aniontxt, 'r') as fin:
          data = fin.read().splitlines(True)
      with open(hirshfeld_charge_anion_filtertxt,"w") as fout:
         fout.write("checkanion\n")
         fout.writelines(data[1:])

      with open(hirshfeld_charge_anion_filtertxt,"r") as fin, open(hirshfeld_charge_anion_finaltxt,"w") as fout:
           string = 'HIRSHFELD ANALYSIS'
           for line in fin:
               if string in line:
                  fout.write(line)
                  try: 
                     while 'TIMINGS' not in line:
                         line = next(fin)
                         fout.write(line)
                  except StopIteration:
                      pass  # ran out of file to read
      os.remove(macrotarget+'/'+str(nameobj)+'_hirshfeld_charge_anion_filter.txt')
      countfini= open(macrotarget+'/'+str(nameobj)+'_hirshfeld_charge_initial.txt', 'r')
      countdataini = countfini.read()
      inianoccurrences = countdataini.count("HIRSHFELD ANALYSIS")
      print(inianoccurrences)
      if inianoccurrences == (2):        
        
        with open(hirshfeld_charge_initialtxt, 'r') as fini:
            inidata = fini.read().splitlines(True)
        with open(hirshfeld_charge_inital_filtertxt,"w") as foutini:
           foutini.write("checkanion\n")
           foutini.writelines(inidata[1:])

        with open(hirshfeld_charge_inital_filtertxt,"r") as inifin, open(hirshfeld_charge_initial_finaltxt,"w") as inifout:
             string = 'HIRSHFELD ANALYSIS'
             for line in inifin:
                 if string in line:
                    inifout.write(line)
                    try: 
                       while 'TIMINGS' not in line:
                           line = next(inifin)
                           inifout.write(line)
                    except StopIteration:
                        pass  # ran out of file to read
        os.remove(hirshfeld_charge_inital_filtertxt)
      else:
        os.rename(hirshfeld_charge_initialtxt, hirshfeld_charge_initial_finaltxt)

      with open(hirshfeld_charge_cationtxt, 'r') as fin:
          data = fin.read().splitlines(True)
      with open(hirshfeld_charge_cation_filtertxt,"w") as fout:
         fout.write("checkcation\n")
         fout.writelines(data[1:])

      with open(hirshfeld_charge_cation_filtertxt,"r") as fin, open(hirshfeld_charge_cation_finaltxt,"w") as fout:
           string = 'HIRSHFELD ANALYSIS'
           for line in fin:
               if string in line:
                  fout.write(line)
                  try: 
                     while 'TIMINGS' not in line:
                         line = next(fin)
                         fout.write(line)
                  except StopIteration:
                      pass  # ran out of file to read
      os.remove(hirshfeld_charge_cation_filtertxt)
      with open(hirshfeld_charge_cation_finaltxt, 'r') as fin:
          data = fin.read().splitlines(True)
      with open(macrotarget+'/'+str(nameobj)+'_cation_charge.txt',"w") as fout:
         fout.writelines(data[7:-5])
      with open(hirshfeld_charge_anion_finaltxt, 'r') as fin:
          data = fin.read().splitlines(True)
      with open(macrotarget+'/'+str(nameobj)+'_anion_charge.txt',"w") as fout:
         fout.writelines(data[7:-5])
      with open(hirshfeld_charge_initial_finaltxt, 'r') as initialfin:
          alldata = initialfin.read().splitlines(True)
      with open(macrotarget+'/'+str(nameobj)+'_initial_charge.txt',"w") as initialfout:
         initialfout.writelines(alldata[7:-5])
      
      a = open(macrotarget+'/'+str(nameobj)+'_initial_charge.txt', "r")
      b = open(macrotarget+'/'+str(nameobj)+'_initial_hirshfeld_charge.txt', "w")
      for line in a:
          if line.strip():
              b.write("\t".join(line.split()[2:-1]) + "\n")

      a.close()
      b.close()    
      

      os.remove(macrotarget+'/'+str(nameobj)+'_hirshfeld_charge_cation_final.txt')
      os.remove(macrotarget+'/'+str(nameobj)+'_hirshfeld_charge_anion_final.txt')
      os.remove(macrotarget+'/'+str(nameobj)+'_hirshfeld_charge_anion.txt')
      os.remove(macrotarget+'/'+str(nameobj)+'_hirshfeld_charge_cation.txt')

      f = open(macrotarget+'/'+str(nameobj)+'_anion_charge.txt', "r")
      g = open(macrotarget+'/'+str(nameobj)+'_anion_hirshfeld_charge.txt', "w")
      for line in f:
          if line.strip():
              g.write("\t".join(line.split()[2:-1]) + "\n")

      f.close()
      g.close()

      k = open(macrotarget+'/'+str(nameobj)+'_cation_charge.txt', "r")
      l = open(macrotarget+'/'+str(nameobj)+'_cation_hirshfeld_charge.txt', "w")
      for line in k:
          if line.strip():
              l.write("\t".join(line.split()[2:-1]) + "\n")

      k.close()
      l.close()
      
      m = open(macrotarget+'/'+str(nameobj)+'_anion_charge.txt', "r")
      n = open(macrotarget+'/'+str(nameobj)+'_atomname.txt', "w")
      for line in m:
          if line.strip():
              n.write("\t".join(line.split()[0:-2]) + "\n")

      m.close()
      n.close()
      if os.path.getsize(macrotarget+'/'+str(nameobj)+'_cation_hirshfeld_charge.txt') == 0 or os.path.getsize(macrotarget+'/'+str(nameobj)+'_anion_hirshfeld_charge.txt') == 0:
         yasara.ShowMessage("ORCA failed to compute. Please see the output files (.out) for more information")
         yasara.plugin.end()
      else:
         print('ok')
      with open(macrotarget+'/'+str(nameobj)+'_cation_hirshfeld_charge.txt', 'r') as fp:
          for fcount, line in enumerate(fp):
              pass
      
      fcount= (fcount+1)
      i=0
      #f=(loop)
      for i in range(0,fcount):
         iniread=open(macrotarget+'/'+str(nameobj)+'_initial_hirshfeld_charge.txt','r')
         hirshfeldinicharge= iniread.readlines()
         atomhirshfeldinicharge=str(((hirshfeldinicharge[i]).strip('\n'))) 
         atomhirshfeldinicharge=float(atomhirshfeldinicharge)  
         read=open(macrotarget+'/'+str(nameobj)+'_cation_hirshfeld_charge.txt','r')
         hirshfeldcationcharge= read.readlines()
         atomhirshfeldcationcharge=str(((hirshfeldcationcharge[i]).strip('\n'))) 
         atomhirshfeldcationcharge=float(atomhirshfeldcationcharge)
         readanion=open(macrotarget+'/'+str(nameobj)+'_anion_hirshfeld_charge.txt','r')
         hirshfeldanionchargeanion= readanion.readlines()
         atomhirshfeldanioncharge=str(((hirshfeldanionchargeanion[i]).strip('\n'))) 
         atomhirshfeldanioncharge=float(atomhirshfeldanioncharge)
         fukuifunction=float(((atomhirshfeldanioncharge)-(atomhirshfeldcationcharge))/2)
         #fukuifunction=str(fukuifunction)
         fukuifunction=round(fukuifunction,3)
         fukuifunction=str(fukuifunction)
         yasara.run('ZoomAll Steps=10')
         yasara.run('LabelAtom '+str(i+1)+',Format='+str(fukuifunction)+',Height=0.2,Color=Black     ,X=0.0,Y=0.0,Z=0.0')
         yasara.run("BFactorAtom "+str(i+1)+","+str(fukuifunction))
         if i == 0:
           val= open(macrotarget+'/'+str(nameobj)+'_condensed_fukui.txt','w')
           val.write(str(fukuifunction).replace('[','').replace(']',''))
           val.close()
         else:
           valread=open(macrotarget+'/'+str(nameobj)+'_condensed_fukui.txt','r')
           value=valread.readlines()
           valread.close()
           rewrite=open(macrotarget+'/'+str(nameobj)+'_condensed_fukui.txt','w')
           rewrite.writelines(value)
           rewrite.write('\n')
           rewrite.write(str(fukuifunction).replace('[','').replace(']',''))
           rewrite.close()
    
      procombine =[]

      with open((macrotarget)+'/'+str(nameobj)+'_condensed_fukui.txt') as xh:
        with open((macrotarget)+'/'+str(nameobj)+'_atomname.txt') as yh:
          with open((macrotarget)+'/'+str(nameobj)+'_fukuifunction_results.txt',"w") as zh:
       #Read first file
             xlines = xh.readlines()
         #Read second file
             ylines = yh.readlines()
         #Combine content of both lists
         #combine = list(zip(ylines,xlines))
         #Write to third file
             for i in range(len(xlines)):
                line = ylines[i].strip('\n') + '    ' + xlines[i]
                zh.write(line)

      os.remove(macrotarget+'/'+str(nameobj)+'_condensed_fukui.txt')
      os.remove((macrotarget)+'/'+str(nameobj)+'_atomname.txt')
      yasara.ShowMessage("Fukui function calculation is complete")
      yasara.run("saveYOB all,"+macrotarget+"/"+str(nameobj)+".yob")
    else:
      #yasara.ShowMessage("check your structure")
      print('check your structure') 

  
###for methodology of user's choice
  elif methodology == str(7):  
    orcamolinp=open((macrotarget)+'/'+str(nameobj)+'.txt')
    moldata=orcamolinp.read()
    orcamolinp.close()
    orca_geo=open((macrotarget)+'/'+str(nameobj)+'.inp','w+')
    orca_geo.write("! ")
    orca_geo.write(str(functional))
    orca_geo.write(" ")
    orca_geo.write(str(basis))
    #orca_geo.write("\n%pal\n   nprocs ")
   # orca_geo.write(str(processor))
    #orca_geo.write('\nend')
    orca_geo.write("\n\n* xyz  ")
    orca_geo.write(str(reactcharge))
    orca_geo.write(" ")
    orca_geo.write(str(reactmultiplicity))
    orca_geo.write("\n")
    orca_geo.write(str(moldata))
    orca_geo.write('\n*')
    orca_geo.close()
    yasara.ShowMessage("orca is optimizing the molecule")
    
    if mod == str(1) or mod == str(2):     
     os.chdir(macrotarget)
     os.system(orca+' '+(nameobj)+'.inp >  '+(nameobj)+'.out')
      
    else:
      os.system('orca '+macrotarget+'/'+str(nameobj)+'.inp >  '+macrotarget+'/'+str(nameobj)+'.out')
    
    yasara.ShowMessage("ORCA calculation is complete and results are saved in: "+ macrotarget)


##for meethodology vibrational frequency
  elif methodology == str(4):  
    orcamolinp=open((macrotarget)+'/'+str(nameobj)+'.txt')
    moldata=orcamolinp.read()
    orcamolinp.close()
    orca_geo=open((macrotarget)+'/'+str(nameobj)+'.inp','w+')
    orca_geo.write("! ")
    orca_geo.write(str(functional))
    orca_geo.write(" ")
    orca_geo.write(str(basis))
    orca_geo.write(" ")
    orca_geo.write('OPT FREQ')
    #orca_geo.write("\n%pal\n   nprocs ")
    #orca_geo.write(str(processor))
    #orca_geo.write('\nend')
    orca_geo.write("\n\n* xyz  ")
    orca_geo.write(str(reactcharge))
    orca_geo.write(" ")
    orca_geo.write(str(reactmultiplicity))
    orca_geo.write("\n")
    orca_geo.write(str(moldata))
    orca_geo.write('\n*')
    orca_geo.close()
    yasara.ShowMessage("orca is optimizing the Vibrational frequencies")
    if mod == str(1) or mod == str(2):
      os.chdir(macrotarget)
      os.system(orca+' '+str(nameobj)+'.inp >  '+str(nameobj)+'.out')
      
    else: 
      os.system('orca '+macrotarget+'/'+str(nameobj)+'.inp >  '+macrotarget+'/'+str(nameobj)+'.out')
    
    if os.path.isfile(macrotarget+'/'+str(nameobj)+'.hess'):
      yasara.ShowMessage("Vibrational frequencies optimization is complete and results are saved in: "+ macrotarget)
      trjlist =\
        yasara.ShowWin("Custom","Trjectory view",400,250,
         "Text", 20, 50, "Do you want to visualize trajectory?",
         "RadioButtons",2,1,
                        20, 100,"yes",
                        200,100,"no",
         "Button",      150,200," O K")
      attach= open((macrotarget)+'/'+str(nameobj)+'_trjectory.txt','w+')
      attach.write((str(trjlist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
      attach.close()  
      f = open((macrotarget)+'/'+str(nameobj)+'_trjectory.txt', "r")
      content= f.readlines()
      a = str((content[0]).strip('\n'))   
      if a == str(1):
        if mod == str(1):
          os.rename(macrotarget+'/'+str(nameobj)+'_trj.xyz', macrotarget+'/'+str(nameobj)+'_trajectory.xyz' )
        else:
          os.rename(macrotarget+'/'+str(nameobj)+'_trj.xyz', macrotarget+'/'+str(nameobj)+'_trajectory.xyz' )
        yasara.run('DelObj all')  
        yasara.run('Loadxyz '+macrotarget+'/'+str(nameobj)+'_trajectory.xyz')
        yasara.run('ZoomAll Steps=20')
        obj=yasara.run("CountObj all")
        deltext= open(macrotarget+'/'+'deltext.txt','w')
        deltext.write(str(obj).replace('object(s) match the selection.','').replace('[','').replace(']',''))
        deltext.close()
        g = open((macrotarget)+'/'+'deltext.txt', "r")
        content = g.readlines()
        noobj=str((content[0]).strip('\n'))
        g.close()
        noobj=int(noobj)
        k=0
      
        yasara.run('HideObj all')
        for k in range(0,noobj):
            yasara.run('ZoomAll Steps=20')
            yasara.run('ShowObj '+str(k+1))
          #time.sleep(1)
            if int(k+1) == noobj :
              print('done')
            else:
              yasara.run('DelObj '+str(k+1))
            k=k+1

    else:
      yasara.ShowMessage("Vibrational frequencies calculation failed with error")
      print('please see the inputmolecule.out file for more information')


###for methodology uv spectroscopy
  else:
    if mod == str(1) or mod == str(2):    
      if mod == str(1):
        src=orcap+'/'+'orca_mapspc'
        dst=macrotarget+'/'+'orca_mapspc'
        shutil.copy(src, dst)
      else:
        src=orcap+'\orca_mapspc.exe'
        dst=macrotarget+'\orca_mapspc.exe'
        shutil.copy(src, dst)        
    else:
       print("###")
    resultlist =\
      yasara.ShowWin("Custom","SOLVENT SELECTION",600,400,
      "List",        20,70,"Solvent",250,250,"No",                 
                     15,   "None(gas)",
                           "Water",
                           "Acetonitrile",
                           "Acetone",
                           "Ethanol",
                           "Methanol",
                           "CCl4",
                           "CH2Cl2",
                           "Chloroform",
                           "DMSO",
                           "DMF",
                           "Hexane",
                           "Toluene",
                           "Pyridine",
                           "THF",
      "Button",      542,348," O K")


    solv= open((macrotarget)+'/'+'solvent.txt', 'w+')
    solv.write((str(resultlist)).replace("'","").replace(" ", "\n").replace("[1","").replace("]","").replace(",",""))
    solv.write('\n')
    solv.close()    
    f = open((macrotarget)+'/'+'solvent.txt', "r")
    content= f.readlines()
    solvent= str((content[1]).strip('\n'))
    print(content)
    print(solvent)
    if solvent == "None(gas)":
      solvent= ' '
    else:
      solvent = 'CPCM('+str(solvent)+')'
 
    print(solvent)
    
    orcamolinp=open((macrotarget)+'/'+str(nameobj)+'.txt')
    moldata=orcamolinp.read()
    orcamolinp.close()
    orca_uv=open((macrotarget)+'/'+str(nameobj)+'.inp','w+')
    orca_uv.write("! ")
    orca_uv.write(str(functional))
    orca_uv.write(" ")
    orca_uv.write(str(basis))
    orca_uv.write(" ")
    orca_uv.write(str(solvent))
    #orca_uv.write("\n%pal\n   nprocs ")
    #orca_uv.write(str(processor))
    #orca_uv.write('\nend')
    orca_uv.write("\n\n%TDDFT\n\n   NROOTS   40\n\nEND\n\n*xyz  ")
    orca_uv.write(str(reactcharge))
    orca_uv.write(" ")
    orca_uv.write(str(reactmultiplicity))
    orca_uv.write("\n")
    orca_uv.write(str(moldata))
    orca_uv.write('\n*')
    #orca_uv.write("inputmolecule.xyz")
    orca_uv.close()
    #orca_geo.write("\n")
    #orca_geo.write(str(moldata))
    #orca_geo.write('\n*')
    #orca_geo.close()
    #os.remove((macrotarget)+'/'+'solvent.txt')
    yasara.ShowMessage("orca is calculating the UV-Vis spectroscopy")
    if mod == str(1) or mod == str(2):
      os.chdir(macrotarget)
      os.system(orca+' '+str(nameobj)+'.inp >  '+str(nameobj)+'.out')  
      yasara.ShowMessage("done") 
      os.chdir(macrotarget)
      if mod == str(1):
        os.system('./orca_mapspc '+macrotarget+'/'+str(nameobj)+'.out ABS -W1000' )
      else:
        os.system('orca_mapspc.exe '+str(nameobj)+'.out ABS -W1000' )      
    else:
      os.system('orca '+macrotarget+'/'+str(nameobj)+'.inp >  '+macrotarget+'/'+str(nameobj)+'.out')  
      yasara.ShowMessage("done") 
      os.chdir(macrotarget)
      os.system('orca_mapspc '+macrotarget+'/'+str(nameobj)+'.out ABS -W1000' )      
    print('++++++')
    
    file_path = macrotarget+'/'+str(nameobj)+'.out.abs.dat'
    dataframe1 = pd.read_csv(file_path, delim_whitespace=True)
    objcsv=os.path.join((macrotarget),((nameobj)+'.csv'))
    uvdatacsv=os.path.join((macrotarget),'uvdata.csv')
    dataframe1.to_csv(objcsv, index = None)
    df = pd.read_csv(objcsv, header=None)
    df.rename(columns={0: 'name', 1: 'id'}, inplace=True)
    df.to_csv(uvdatacsv, index=False)
    hr= pd.read_csv(uvdatacsv)
    hr=pd.DataFrame(hr)
    hr['wavelength'] = ((1/hr['name']*10000000).round(0))
    dr=pd.DataFrame(hr)
    dr.to_csv((macrotarget)+'/'+str(nameobj)+'_uvdata.csv', index = None)




    with open((macrotarget)+'/'+str(nameobj)+'_uvdata.csv', 'r+') as f:
      headers = f.readline()
      firstData = f.readline()
      f.seek(0)
      firstData = firstData[:-1] + ' ' * len(headers) + '\n'
      f.write(firstData)
    with open((macrotarget)+'/'+str(nameobj)+'_uvdata.csv', 'r+') as fd:
        lines = fd.readlines()
        fd.seek(0)
        fd.writelines(line for line in lines if line.strip())
        fd.truncate()
    
    x = []
    y = []
    
    with open((macrotarget)+'/'+str(nameobj)+'_uvdata.csv','r') as csvfile:
        plots = csv.reader(csvfile, delimiter = ',')
      
        for row in plots:
            x.append(float(row[5]))
            y.append(float(row[1]))
  
    plt.plot(x, y, color = 'red', linestyle = 'dashed')
    plt.xlim(150,800)
    plt.ylim(-1)
    plt.xlabel('Wavelength(nm)')
    plt.ylabel('Absorbance')
    plt.title('UV-Vis Spectroscopy analysis')
#plt.grid()
    plt.savefig((macrotarget)+'/'+str(nameobj)+'_uvdata.png')     
    thirdpng='LoadPNG '+(macrotarget)+'/'+str(nameobj)+'_uvdata.png'
    yasara.run(thirdpng)
    yasara.run("ShowImage 1,Alpha=100,Priority=0")
    yasara.ShowMessage("UV-Vis spectroscopy analysis is complete")

else :
  print("++++")

########### MOPAC calculation
#### MOPAC INPUT FILE FORMATION ###################################################################################################
if method == 'MOPAC' : 
###object selection  
  obj=yasara.run("CountObj all")
  deltext= open(macrotarget+'/'+'deltext.txt','w')
  deltext.write(str(obj).replace('object(s) match the selection.','').replace('[','').replace(']',''))
  deltext.close()
  g = open((macrotarget)+'/'+'deltext.txt', "r")
  content = g.readlines()
  noobj=str((content[0]).strip('\n'))
  g.close()
  if noobj== str(0):
    if methodology == 'Import-job' and os.path.isfile(macrotarget+'/'+ownfile):
      print("ownfile is present") 
    else:
      yasara.ShowMessage("Please build your molecule and then click continue")
      yasara.run("wait continuebutton") 
      reobj=yasara.run("CountObj all")
      redeltext= open(macrotarget+'/'+'redeltext.txt','w')
      redeltext.write(str(reobj).replace('object(s) match the selection.','').replace('[','').replace(']',''))
      redeltext.close()
      reg = open((macrotarget)+'/'+'redeltext.txt', "r")
      recontent = reg.readlines()
      renoobj=str((recontent[0]).strip('\n'))
      reg.close()
      if renoobj== 0:
        yasara.ShowMessage("QM calculation failed. Please load a structure and restart the process")
        os.remove(macrotarget+'/'+'redeltext.txt')
        yasara.plugin.end()
      yasara.run('joinObj all,1')
      yasara.run("SaveXYZ 1,"+str(macrotarget)+'/'+str(nameobj)+".xyz,transform=Yes")
      yasara.run('DelObj all')  
      yasara.run('Loadxyz '+(macrotarget)+'/'+str(nameobj)+'.xyz')
    ###charge and multiplicity calculation
      yasara.run('ForceField AMBER03,SetPar=Yes')
###charge of the reactant molecule
      chargeinfo=charge_calculation()#yasara.run('ChargeObj all')
      cfmod=open(macrotarget+'/'+str(nameobj)+'charge.log','w')
      cfmod.write(str(chargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']','').replace(',','\n'))
      cfmod.close()
      chargef= open(macrotarget+'/'+str(nameobj)+'charge.log','r')
      chargeall=chargef.readlines()
      charge=float((chargeall[0]).strip('\n'))
      charge=round(charge)
      print(charge)
      alllist =\
        yasara.ShowWin("Custom","INFORMATION",400,250,
        "NumberInput", 20, 88,"Charge",str(charge),-1000,1000,
        "NumberInput", 180, 88,"Multiplicity",1,1,6,
        "Button",      150,200," O K")  
  ##counting the object present in the yasara window
      rcharge=open(macrotarget+'/'+str(nameobj)+'charge.log','w+')
      rcharge.write((str(alllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
      rcharge.close()
      if os.path.getsize(macrotarget+'/'+str(nameobj)+'charge.log') == 0:
        yasara.ShowMessage("Charge calculation failed, restart the process") 
        os.remove(macrotarget+'/'+str(nameobj)+'charge.log')
        yasara.plugin.end() 
      else:
        print('ok')   

      react_charge = open(macrotarget+'/'+str(nameobj)+'charge.log', "r")
      reactinfo= react_charge.readlines()
      reactcharge= str((reactinfo[0]).strip('\n'))    
      reactmultiplicity= str((reactinfo[1]).strip('\n')) 
      if reactmultiplicity == str(1):
        reactmultiplicity= 'SINGLET'
      elif reactmultiplicity == str(2):
        reactmultiplicity= 'DOUBLET'
      elif reactmultiplicity == str(3):
        reactmultiplicity= 'TRIPLET'
      elif reactmultiplicity == str(4):
        reactmultiplicity= 'QUARTET'
      elif reactmultiplicity == str(5):
        reactmultiplicity= 'QUINTET'
      else:
        reactmultiplicity= 'SEXTET'

  else:    
    
    yasara.ShowMessage("Please select your molecule by selectbox or join object all and then select all atoms")
    yasara.run("wait continuebutton")
    counts=yasara.run('CountAtom selected')
    countselect= open(macrotarget+'/'+'checkselect.txt','w')
    countselect.write(str(counts).replace('object(s) match the selection.','').replace('[','').replace(']','').replace("'",""))
    countselect.close()
    ck=os.path.getsize(macrotarget+'/'+'checkselect.txt')
    print(ck)
    if ck== 1:
       yasara.ShowMessage("Make sure that you have selected the object")
       yasara.run("wait continuebutton")      
    else:
       print('OK')
    nome=yasara.run('NameObj selected')
    print('ok')    
    redeltext= open(macrotarget+'/'+'nome.txt','w')
    redeltext.write(str(nome).replace('object(s) match the selection.','').replace('[','').replace(']','').replace("'","").replace(', ','_'))
    redeltext.close()
    reg = open((macrotarget)+'/'+'nome.txt', "r")
    recontent = reg.readlines()
    nome=str((recontent[0]).strip('\n'))
    reg.close()
    print(nome)
    nameobj=str(nameobj)+"_"+str(nome)
    yasara.run("SaveSce "+str(macrotarget)+'/'+str(nameobj)+"_ini.sce")
    yasara.run('NumberObj selected,1')
    yasara.run('JoinObj all,1')
    yasara.run('Delatom all and not selected')
    yasara.run("SaveSce "+str(macrotarget)+'/'+str(nameobj)+"_select.sce")
    yasara.run("SaveXYZ Selected,"+str(macrotarget)+'/'+str(nameobj)+".xyz,transform=Yes")
    #yasara.run('Clear')
    #yasara.run('Loadxyz '+(macrotarget)+'/'+str(nameobj)+'.xyz')
    #yasara.run('JoinObj all,1')
    #yasara.run("SaveXYZ Selected,"+str(macrotarget)+'/'+str(nameobj)+".xyz,transform=Yes")

    yasara.run('Clear')
    yasara.run('LoadSce '+str(macrotarget)+'/'+str(nameobj)+'_ini.sce,Settings=No')
    
    #yasara.run('DelObj all and not selected')
    #yasara.run('RemoveObj all and not selected')
    #yasara.run('DelObj all')  
    #yasara.run('Loadxyz '+(macrotarget)+'/'+str(nameobj)+'.xyz')
    ###charge and multiplicity calculation
    yasara.run('ForceField AMBER03,SetPar=Yes')
###charge of the reactant molecule
    chargeinfo=charge_calculation()#yasara.run('ChargeObj selected')
    cfmod=open(macrotarget+'/'+str(nameobj)+'charge.log','w')
    cfmod.write(str(chargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']','').replace(',','\n'))
    cfmod.close()
    if os.path.getsize(macrotarget+'/'+str(nameobj)+'charge.log')== 0:
      yasara.ShowMessage("QM calculation  will be failed. Please select a structure.")
      #os.remove(macrotarget+'/'+'redeltext.txt')
      yasara.run("wait continuebutton")
      nome=yasara.run('NameObj selected')
      print('ok')    
      redeltext= open(macrotarget+'/'+'nome.txt','w')
      redeltext.write(str(nome).replace('object(s) match the selection.','').replace('[','').replace(']','').replace("'","").replace(', ','_'))
      redeltext.close()
      reg = open((macrotarget)+'/'+'nome.txt', "r")
      recontent = reg.readlines()
      nome=str((recontent[0]).strip('\n'))
      reg.close()
      print(nome)
      nameobj=str(nameobj)+"_"+str(nome)
      yasara.run("SaveSce "+str(macrotarget)+'/'+str(nameobj)+"_ini.sce")
      yasara.run('NumberObj selected,1')
      yasara.run('JoinObj all,1')
      yasara.run('Delatom all and not selected')
      chargeinfo=charge_calculation()#yasara.run('ChargeObj all')
      yasara.run("SaveSce "+str(macrotarget)+'/'+str(nameobj)+"_select.sce")
      yasara.run("SaveXYZ all,"+str(macrotarget)+'/'+str(nameobj)+".xyz,transform=Yes")
      yasara.run("SaveXYZ all,"+str(macrotarget)+'/'+str(nameobj)+"_ini.xyz,transform=Yes")

      yasara.run('Clear')
      yasara.run('LoadSce '+str(macrotarget)+'/'+str(nameobj)+'_ini.sce,Settings=No')    
    
    
    #yasara.ShowMessage("Please select your molecule by selectbox or join object all and then select all atoms")
    #yasara.run("wait continuebutton")
      yasara.run('ForceField AMBER03,SetPar=Yes')
  ###charge of the  molecule
      cmod=open(macrotarget+'/'+str(nameobj)+'charge.log','w')
      cmod.write(str(chargeinfo).replace('Summed up net charge is ','').replace('[','').replace(']',''))
      cmod.close() 

    chargef= open(macrotarget+'/'+str(nameobj)+'charge.log','r')
    chargeall=chargef.readlines()
    charge=float((chargeall[0]).strip('\n'))
    charge=round(charge)
    print(charge)
    alllist =\
      yasara.ShowWin("Custom","INFORMATION",400,250,
      "NumberInput", 20, 88,"Charge",str(charge),-1000,1000,
      "NumberInput", 180, 88,"Multiplicity",1,1,6,
      "Button",      150,200," O K")  
##counting the object present in the yasara window
    rcharge=open(macrotarget+'/'+str(nameobj)+'charge.log','w+')
    rcharge.write((str(alllist)).replace("'","").replace(" ", "\n").replace("[","").replace("]","").replace(",",""))
    rcharge.close()
    if os.path.getsize(macrotarget+'/'+str(nameobj)+'charge.log') == 0:
      yasara.ShowMessage("Charge calculation failed, restart the process") 
      os.remove(macrotarget+'/'+str(nameobj)+'charge.log')
      yasara.plugin.end() 
    else:
      print('ok')   

    react_charge = open(macrotarget+'/'+str(nameobj)+'charge.log', "r")
    reactinfo= react_charge.readlines()
    reactcharge= str((reactinfo[0]).strip('\n'))    
    reactmultiplicity= str((reactinfo[1]).strip('\n')) 
    if reactmultiplicity == str(1):
      reactmultiplicity= 'SINGLET'
    elif reactmultiplicity == str(2):
      reactmultiplicity= 'DOUBLET'
    elif reactmultiplicity == str(3):
      reactmultiplicity= 'TRIPLET'
    elif reactmultiplicity == str(4):
      reactmultiplicity= 'QUARTET'
    elif reactmultiplicity == str(5):
      reactmultiplicity= 'QUINTET'
    else:
      reactmultiplicity= 'SEXTET'

##homo-lumo energy gap calculation    
  if methodology == 'HOMO-LUMO':  
    if theory == ' ' :
      yasara.run('QuantumMechanics AM1')
      keys="DENSITY"
      yasara.run('LogAs '+(str(macrotarget))+'/'+str(nameobj)+'_qm_log,Append=No,RunMOPACObj 1,'+str(keys))    
      with open(macrotarget+'/'+str(nameobj)+'_qm_log.log',"r") as fin, open(macrotarget+'/'+str(nameobj)+'_qm_first.txt',"w") as fout:
           string = 'EIGENVALUES'
           for line in fin:
               if string in line:
                  fout.write(line)
                  try: 
                     while 'ATOMIC ORBITAL ELECTRON POPULATIONS' not in line:
                         line = next(fin)
                         fout.write(line)
                  except StopIteration:
                      pass  # ran out of file to read
                
      with open(macrotarget+'/'+str(nameobj)+'_qm_first.txt',"r") as fin, open(macrotarget+'/'+str(nameobj)+'_EIGENVALUES.txt',"w") as fout:
           string = 'EIGENVALUES'
           for line in fin:
               if string in line:
                  fout.write(line)
                  try: 
                     while 'NET ATOMIC CHARGES AND DIPOLE CONTRIBUTIONS' not in line:
                         line = next(fin)
                         fout.write(line)
                  except StopIteration:
                      pass  # ran out of file to read                
      remove_words=['NET']
      with open(macrotarget+'/'+str(nameobj)+'_EIGENVALUES.txt') as oldfile, open(macrotarget+'/'+str(nameobj)+'_EIGENVALUES_filter.txt', 'w') as newfile:
          for line in oldfile:
              if not any(remove_word in line for remove_word in remove_words):
                  newfile.write((line).replace('EIGENVALUES',''))

      os.remove(macrotarget+'/'+str(nameobj)+'_EIGENVALUES.txt')
      with open(macrotarget+'/'+str(nameobj)+'_EIGENVALUES_filter.txt') as reader, open(macrotarget+'/'+str(nameobj)+'_EIGENVALUES_filter.txt', 'r+') as writer:
        for line in reader:
          if line.strip():
            writer.write((line).replace('\n',''))
        writer.truncate()

      with open(macrotarget+'/'+str(nameobj)+'_qm_log.log',"r") as fin, open(macrotarget+'/'+str(nameobj)+'_qm_value.txt',"w") as fout:
           string = 'IONIZATION POTENTIAL'
           for line in fin:
               if string in line:
                  fout.write(line)
                  try: 
                     while 'NO. OF FILLED LEVELS' not in line:
                         line = next(fin)
                         fout.write(str(line).replace('IONIZATION POTENTIAL    =         ','').replace('NO. OF FILLED LEVELS    =         ',''))
                  except StopIteration:
                      pass  # ran out of file to read
      with open (macrotarget+'/'+str(nameobj)+'_qm_value.txt',"r") as f:
          data=f.readlines()
          p=((data[1]).strip('\n').strip('          '))
          print(p)
          f.close()
      p=int(p)
      m= p-1
      m=str(m)


      eigenarr = np.genfromtxt(macrotarget+'/'+str(nameobj)+'_EIGENVALUES_filter.txt')
      eigenarr=np.array(eigenarr)
  #eigenarr=np.array(eigenarr)
  #x=eigenarr[eigenarr < 0]
      a= eigenarr[int(p)]
      print(a)
      b= eigenarr[int(m)]
      print(b)
      a=float(a)
      b=float(b)
      energydiff=(a-b)
      homolumodiff= round(energydiff,3)
      lumo = round(a,3)
      homo = round(b,3)
      os.remove(macrotarget+'/'+str(nameobj)+'_EIGENVALUES_filter.txt')
      yasara.ShowMessage(" HOMO " + (str(homo)) + " LUMO " + (str(lumo)) + " gap: " + (str(homolumodiff))+ " eV")
    else:

      fh = open(macrotarget+'/'+str(nameobj)+'.xyz', "r")
      gh = open(macrotarget+'/'+str(nameobj)+'_xyz.txt', "w")
      for line in fh:
         if line.strip():
            gh.write("\t".join(line.split()[1:]) + "\n")

      fh.close()
      gh.close()
      x= open(macrotarget+'/'+str(nameobj)+'_xyz.txt','r')
      data=x.read()

      y=open(macrotarget+'/'+str(nameobj)+'_xyz.txt','w+')
      y.write(str(data).replace("	","0 0	").replace("\n","0 0\n"))
      y.close()
      fh = open(macrotarget+'/'+str(nameobj)+'.xyz', "r")
      gh = open(macrotarget+'/'+str(nameobj)+'_atomname.txt', "w")
      for line in fh:
         if line.strip():
            gh.write("\t".join(line.split()[:1]) + "\n")

      fh.close()
      gh.close()

      combine =[]

      with open(macrotarget+'/'+str(nameobj)+'_xyz.txt') as xh:
        with open(macrotarget+'/'+str(nameobj)+'_atomname.txt') as yh:
          with open(macrotarget+'/'+str(nameobj)+'.txt',"w") as zh:
             #Read first file
             xlines = xh.readlines()
               #Read second file
             ylines = yh.readlines()
               #Combine content of both lists
               #combine = list(zip(ylines,xlines))
               #Write to third file
             for i in range(len(xlines)):
                line = ylines[i].strip('\n') + '    ' + xlines[i]
                zh.write(line)
      os.chdir(plgpath)
      os.chdir(macrotarget)                    
      with open(macrotarget+'/'+str(nameobj)+'.txt', 'r') as fin:
         data = fin.read().splitlines(True)
      with open(macrotarget+'/'+str(nameobj)+'.txt', 'w') as fout:
         fout.writelines(data[1:])
         fout.close()
      f = open((macrotarget)+'/'+str(nameobj)+'.txt', "r")
      molcontent= f.read()
      f.close()
      inp=open(macrotarget+'/'+str(nameobj)+'.mop', 'w+')  
      inp.write(" ")
      inp.write(str(firstkey))  
      inp.write(str(reactcharge)) 
      inp.write(" ")
      inp.write(str(reactmultiplicity))
      inp.write(" ")
      inp.write(str(secondkey))
      inp.write(" ")
      inp.write(str(theory))
      inp.write(" ")      
      inp.write(str(thirdkey))
      inp.write(" ")
      inp.write(str(hf))
      inp.write("\n\n\n")  
      inp.write(str(molcontent)) 
      inp.write("\n")    
      inp.close()
      print(mopac)
      with open(macrotarget+'/'+str(nameobj)+'.mop') as f, open(macrotarget+'/'+str(nameobj)+'_edit.mop', "w") as working:    
          for line in f:   
             if ".xyz" not in line:  
                 working.write(line)  
      os.remove(macrotarget+'/'+str(nameobj)+'.mop')  
      os.rename(macrotarget+'/'+str(nameobj)+'_edit.mop', macrotarget+'/'+str(nameobj)+'.mop')       
      
      os.chdir(plgpath)
      os.chdir(macrotarget)      
      os.system(mopac+' '+macrotarget+'/'+str(nameobj)+'.mop')
      energygapline= open(macrotarget+'/'+str(nameobj)+'.out')
      for line in energygapline:
          if "HOMO LUMO ENERGIES (EV) = " in line:
             print(line)
             line=str(line).strip("\n").strip("   ")
             ev=open(macrotarget+'/'+str(nameobj)+'_homo-lumo.txt', 'w+')
             ev.write((str(line)).replace('HOMO LUMO ENERGIES (EV) =        ','').replace(' ','\n'))
             ev.close()
             with open((macrotarget)+'/'+str(nameobj)+'_homo-lumo.txt', 'r+') as fd:
                 lines = fd.readlines()
                 fd.seek(0)
                 fd.writelines(line for line in lines if line.strip())
                 fd.truncate()             
             
             evgap=open(macrotarget+'/'+str(nameobj)+'_homo-lumo.txt')
             evgaplines=evgap.readlines()
             evgap.close()
             homo=(evgaplines[0]).strip('\n')
             lumo=(evgaplines[1]).strip('\n')

             homo=float(homo)
             lumo=float(lumo)
             energydiff=(lumo-homo)
             homolumodiff= round(energydiff,3)
             yasara.ShowMessage(" HOMO " + (str(homo)) + " LUMO " + (str(lumo)) + " gap: " + (str(homolumodiff))+ " eV")
             #yasara.ShowMessage(str(line))
             #os.remove(macrotarget+'/'+str(nameobj)+'_homo-lumo.txt')
             yasara.plugin.end()


  elif methodology == 'Single-point': 

      fh = open(macrotarget+'/'+str(nameobj)+'.xyz', "r")
      gh = open(macrotarget+'/'+str(nameobj)+'_xyz.txt', "w")
      for line in fh:
         if line.strip():
            gh.write("\t".join(line.split()[1:]) + "\n")

      fh.close()
      gh.close()
      x= open(macrotarget+'/'+str(nameobj)+'_xyz.txt','r')
      data=x.read()

      y=open(macrotarget+'/'+str(nameobj)+'_xyz.txt','w+')
      y.write(str(data).replace("	","0 0	").replace("\n","0 0\n"))
      y.close()

      fh = open(macrotarget+'/'+str(nameobj)+'.xyz', "r")
      gh = open(macrotarget+'/'+'atomname.txt', "w")
      for line in fh:
         if line.strip():
            gh.write("\t".join(line.split()[:1]) + "\n")

      fh.close()
      gh.close()

      combine =[]

      with open(macrotarget+'/'+str(nameobj)+'_xyz.txt') as xh:
        with open(macrotarget+'/'+'atomname.txt') as yh:
          with open(macrotarget+'/'+str(nameobj)+'.txt',"w") as zh:
             #Read first file
             xlines = xh.readlines()
               #Read second file
             ylines = yh.readlines()
               #Combine content of both lists
               #combine = list(zip(ylines,xlines))
               #Write to third file
             for i in range(len(xlines)):
                line = ylines[i].strip('\n') + '    ' + xlines[i]
                zh.write(line)
      os.chdir(plgpath)
      os.chdir(macrotarget)                    
      with open(macrotarget+'/'+str(nameobj)+'.txt', 'r') as fin:
         data = fin.read().splitlines(True)
      with open(macrotarget+'/'+str(nameobj)+'.txt', 'w') as fout:
         fout.writelines(data[1:])
         fout.close()
      #with open(macrotarget+'/'+'inputmolecule.txt', 'r') as ffin:
         #fdata = ffin.read().splitlines(True)
      #with open(macrotarget+'/'+'datainputmolecule.txt', 'w') as ffout:
         #ffout.writelines(fdata[1:])
         #ffout.close()

      #yasara.run("wait continuebutton")
      #os.remove(macrotarget+'/'+str(nameobj)+'_xyz.txt')
      f = open((macrotarget)+'/'+str(nameobj)+'.txt', "r")
      molcontent= f.read()
      f.close()
      inp=open(macrotarget+'/'+str(nameobj)+'.mop', 'w+')  
      inp.write(" ")
      inp.write(str(firstkey))  
      inp.write(str(reactcharge)) 
      inp.write(" ")
      inp.write(str(reactmultiplicity))
      inp.write(" ")
      inp.write(str(secondkey))
      inp.write(" ")
      inp.write(str(theory))
      inp.write(" ")      
      inp.write(str(thirdkey))
      inp.write(" ")
      inp.write(str(hf))
      inp.write("\n\n\n")  
      inp.write(str(molcontent)) 
      inp.write("\n")    
      inp.close()
      #print(mopac)
      with open(macrotarget+'/'+str(nameobj)+'.mop') as f, open(macrotarget+'/'+str(nameobj)+'_edit.mop', "w") as working:    
          for line in f:   
             if ".xyz" not in line:  
                 working.write(line)  
      os.remove(macrotarget+'/'+str(nameobj)+'.mop')  
      os.rename(macrotarget+'/'+str(nameobj)+'_edit.mop', macrotarget+'/'+str(nameobj)+'.mop')       
      
      os.chdir(plgpath)
      os.chdir(macrotarget)      
      os.system(mopac+' '+macrotarget+'/'+str(nameobj)+'.mop')
      errorline= open(macrotarget+'/'+str(nameobj)+'.out')
      for line in errorline:
          if "CORRECT" in line:
             print(line)
             line=str(line).strip("\n").strip("   ")
             yasara.ShowMessage(str(line))
             yasara.plugin.end()
          else: 
             print('OK')
      yasara.run('DelObj all')
      yasara.run('Loadpdb '+macrotarget+'/'+str(nameobj)+'.pdb')
      yasara.ShowMessage('Single point calculation is complete and results are saved in :'+str(macrotarget)) 

  elif methodology == 'Equilibrium-geometry': 

      fh = open(macrotarget+'/'+str(nameobj)+'.xyz', "r")
      gh = open(macrotarget+'/'+str(nameobj)+'_xyz.txt', "w")
      for line in fh:
         if line.strip():
            gh.write("\t".join(line.split()[1:]) + "\n")

      fh.close()
      gh.close()
      x= open(macrotarget+'/'+str(nameobj)+'_xyz.txt','r')
      data=x.read()

      y=open(macrotarget+'/'+str(nameobj)+'_xyz.txt','w+')
      y.write(str(data).replace("	","1 1	").replace("\n","1 1\n"))
      y.close()

      fh = open(macrotarget+'/'+str(nameobj)+'.xyz', "r")
      gh = open(macrotarget+'/'+str(nameobj)+'_atomname.txt', "w")
      for line in fh:
         if line.strip():
            gh.write("\t".join(line.split()[:1]) + "\n")

      fh.close()
      gh.close()

      combine =[]

      with open(macrotarget+'/'+str(nameobj)+'_xyz.txt') as xh:
        with open(macrotarget+'/'+str(nameobj)+'_atomname.txt') as yh:
          with open(macrotarget+'/'+str(nameobj)+'.txt',"w") as zh:
             #Read first file
             xlines = xh.readlines()
               #Read second file
             ylines = yh.readlines()
               #Combine content of both lists
               #combine = list(zip(ylines,xlines))
               #Write to third file
             for i in range(len(xlines)):
                line = ylines[i].strip('\n') + '    ' + xlines[i]
                zh.write(line)
                   
      os.chdir(plgpath)
      os.chdir(macrotarget)                    
      with open(macrotarget+'/'+str(nameobj)+'.txt', 'r') as fin:
         data = fin.read().splitlines(True)
      with open(macrotarget+'/'+str(nameobj)+'_edit.txt', 'w') as fout:
         fout.writelines(data[1:])
         fout.close()
      #with open(macrotarget+'/'+'inputmolecule_edit.txt', 'r') as ffin:
         #fdata = ffin.read().splitlines(True)
      #with open(macrotarget+'/'+'datainputmolecule.txt', 'w') as ffout:
         #ffout.writelines(fdata[1:])
         #ffout.close()
      #os.remove(macrotarget+'/'+str(nameobj)+'_xyz.txt')
      f = open((macrotarget)+'/'+str(nameobj)+'_edit.txt', "r")
      molcontent= f.read()
      f.close()
      inp=open(macrotarget+'/'+str(nameobj)+'.mop', 'w+')  
      inp.write(" ")
      inp.write(str(firstkey))  
      inp.write(str(reactcharge)) 
      inp.write(" ")
      inp.write(str(reactmultiplicity))
      inp.write(" ")
      inp.write(str(secondkey))
      inp.write(" ")
      inp.write(str(theory))
      inp.write(" ")      
      inp.write(str(thirdkey))
      inp.write(" ")
      inp.write(str(hf))
      inp.write("\n\n\n")  
      inp.write(str(molcontent)) 
      inp.write("\n")    
      inp.close()
      print(mopac)
      with open(macrotarget+'/'+str(nameobj)+'.mop') as f, open(macrotarget+'/'+str(nameobj)+'_edit.mop', "w") as working:    
          for line in f:   
             if ".xyz" not in line:  
                 working.write(line)  
      os.remove(macrotarget+'/'+str(nameobj)+'.mop')  
      os.rename(macrotarget+'/'+str(nameobj)+'_edit.mop', macrotarget+'/'+str(nameobj)+'.mop') 

      os.chdir(plgpath)
      os.chdir(macrotarget)
      os.system(mopac+' '+macrotarget+'/'+str(nameobj)+'.mop')
      if os.path.isfile(macrotarget+'/'+str(nameobj)+'.pdb'):
         yasara.ShowMessage('Geometry equilibration is complete and results are saved in :'+str(macrotarget))   
         yasara.run('DelObj all')
         yasara.run('LoadPDB '+macrotarget+'/'+str(nameobj)+'.pdb')
         #os.rename(macrotarget+'/'+str(nameobj)+'.xyz',macrotarget+'/'+'output.xyz') 
         yasara.plugin.end()
      else:
         yasara.ShowMessage('Geometry equilibration failed,please see the output files in :'+str(macrotarget))    

  else:
    os.chdir(plgpath)
    os.chdir(macrotarget)   
    os.system(mopac+' '+macrotarget+'/'+ownfile)
    yasara.ShowMessage('Calculation is complete and results are saved in :'+str(macrotarget)) 
#yasara.ShowMessage('Please use different project name for the calculations') 
yasara.plugin.end()
