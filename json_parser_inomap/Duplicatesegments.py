import os
import json
from PyQt5.QtWidgets import *
from qgis.PyQt.QtWidgets import*

class duplicate :
    def __init__(self, mainpath,Dbconnection,iFace):
        self.path=mainpath
        self.dlg=Dbconnection.dlg
        self.iface=iFace
        self.lable=Dbconnection
        # print("self.path",self.path)
        self. Duplicatesegments()
    def Duplicatesegments(self):
        self.dlg.progressBar_3.show()
        prg = 0
        flag=0
        # Set the directory path
        dir_path = self.path

        # Get a list of all files in the directory
        files = os.listdir(dir_path)
        file_count=len(files)
        list=[]

        laneline_id_to_seg = {}
        # Loop through the files and do something with each one
        for file in files:
            percent = prg / float(file_count) * 100
            self.dlg.progressBar_3.setValue(percent+1)
            prg += 1
            if file.endswith('.segment'):
                # Open the JSON file
                with open(os.path.join(dir_path,file), 'r') as f:
                    # Load the JSON data into a Python dictionary
                    segment = json.load(f)
                    segment_id = segment['id']
                    lanelines = segment['lane_lines']
                    for laneline in lanelines:
                        laneline_id = laneline['id']
                        laneline_id = (laneline_id['s'])
                        if laneline_id in laneline_id_to_seg:
                            flag=1
                            self.lable.Lable_3_changed(laneline_id,segment_id,laneline_id_to_seg)
                            self.iface.messageBar().pushMessage("Error  - ",f"found duplicated lane line {laneline_id} in {segment_id} and {laneline_id_to_seg[laneline_id]}",level=Qgis.Critical)
                            print(f'found duplicated lane line {laneline_id} in {segment_id} and {laneline_id_to_seg[laneline_id]}')
                        else:
                            laneline_id_to_seg[laneline_id]=segment_id
                            # QMessageBox.information(self.dlg,'Information',' Checks_duplicated Successfully.')
            
        
        # self.lable.Lable_3_changed(list)
        if flag==0:
            QMessageBox.information(self.dlg,'Information','Checks_duplicated Successfully.')
        else:
            QMessageBox.critical(self.dlg,'Critical',' UnSuccessfully')

        # print("laneline_id_to_seg")