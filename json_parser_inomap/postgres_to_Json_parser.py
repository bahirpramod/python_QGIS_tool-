import pyproj
import os
import sys
import psycopg2
import json
import shutil
import  datetime
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtWidgets import*
# import tkinter
# from tkinter import END, filedialog, ttk, messagebox
# from collections import defaultdict
from copy import deepcopy

class JsonParser1:
    def __init__(self,mainpath ,Dbconnection,iFace):
        # try:
            self.mainpath = mainpath
            self.host = Dbconnection.host
            self.database = Dbconnection.databas
            self.user = Dbconnection.user
            self.password = Dbconnection.pwd
            self.port = int(Dbconnection.port)
            self.db_link = Dbconnection.curs
            self.connection_db = Dbconnection.conn
            # self.tbl_schema = Dbconnection.schem
            self.tbl_schema = Dbconnection.schem
            self.dlg=Dbconnection.dlg
            self.lable=Dbconnection
            self.iface=iFace
            print("tbl_schema",self.tbl_schema)
            self.lable.set_Lable_schema_2(self.tbl_schema)
            # subdir = [name for name in os.listdir(self.mainpath) if os.path.isdir(self.mainpath+"\\" +name)]
            # print(subdir)
            # datafolder = []
            # for i in subdir:
            #     # if i[0] == 'r':
            #     subpath = self.mainpath+"\\" + i
            #     datadir = [name for name in os.listdir(subpath) if os.path.isdir(subpath + "\\" + name)]
            #     print('datadir',datadir)
            #     for datapath in datadir:
            #         if datapath == 'uncurated.ino':
            #             datafolder.append(subpath+'\\'+datapath)
            # print('datafolder',datafolder)
            # if len(subdir) > 0:
            subdir=''
            self.file_name(subdir)
        # except Exception as e:
        #     exc_type, exc_obj, exc_tb = sys.exc_info()
        #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #     print(exc_type, fname, exc_tb.tb_lineno)

    def file_name(self,dirpath):
        # try:
            segments = []
            zones = []
            # path="D:/inomap/data/json_files"
            path=self.mainpath+"/test.zone"

            #path = self.mainpath

            # shutil.copy(original, rename)
            # for file in os.listdir(path):
            #     if file.endswith('.segment') and (not file.startswith('._')):
            #         segments.append(path + '\\' + str(file))
            #     elif file.endswith('.zone') and (not file.startswith('._')):
            #         zones.append(path + '\\' + str(file))
                # if len(segments) > 0 :
                #     self.segment_parser(segments)
                #     pass
                    #print(segments)

            # sql2 = f"SELECT distinct(zone_id) from {self.tbl_schema}.zone"
            # print(sql2)
            # self.db_link.execute(sql2)
            # zone_id_data = self.db_link.fetchall()
            # # print('zone_id_data', zone_id_data)

            # for zn_id in zone_id_data:

            #     zon_id=zn_id[0]
            #     print("zon_id",zon_id)
            #     rename = self.mainpath + '/' + zon_id + '.zone'
            #     shutil.copy(path, rename)
            #     self.zone_parser(path,rename,zon_id)
                #break
            sql3 = f"SELECT distinct(segment_id) from {self.tbl_schema}.segment"
            
            #print(sql3)

            #sql3 = f"SELECT segment_id from segment where segment_id='1a08c683-4927-43d9-bcf1-a72f7c69f0a6'"
            # print(sql2)
            self.db_link.execute(sql3)
            segment_id_data = self.db_link.fetchall()

            # get the count 
            sql4 = f"SELECT count(segment_id) from {self.tbl_schema}.segment"
            self.db_link.execute(sql4)
            total_count = self.db_link.fetchall()
            # print("total_count",total_count[0][0])
            file_path = self.mainpath + "/sample_segment.segment"

            counter = 0
            
            for segment_id in segment_id_data:
                #print(segment_id)
                segm_id = segment_id[0]
                # print("segm_id",segm_id)
                # sql_seg=f"SELECT segment_id from lanes where segment_id='segment_id[0]'"
                sql_seg="select segment_id  from {0}.lanes where segment_id ='{1}' ;".format(self.tbl_schema,segment_id[0])
                # print(("sql_seg",sql_seg))
                self.db_link.execute(sql_seg)
                segment_id_inLane = self.db_link.fetchall()
                # print("segment_id_inLane",segment_id_inLane)
                # print("segment_id_inLane",len(segment_id_inLane))
                file_count=int(len(segment_id_inLane))
                # print("file_count",file_count)
                if len(segment_id_inLane)>=1 :
                    seg_rename = self.mainpath + '/' + segm_id + '.segment'
                    shutil.copy(file_path, seg_rename)
                    self.flag=self.segment_parser(file_path,seg_rename,segm_id,file_count)
                    counter = counter + 1
                    # print(counter, " - segm_id", segm_id)
                    self.lable.Lable_2_changed(counter,segm_id)
            # print("self.flag",self.flag)
            if self.flag==0:
                QMessageBox.information(self.dlg,'Information','Data Exported Successfully.')
            else:
                QMessageBox.critical(self.dlg,'Critical','Data Not Exported .')

            
                #break
            # if len(zones) > 0:
            #     self.zone_parser(zones)
            #     pass
                    #print(zones)
        # except Exception as e:
        #     exc_type, exc_obj, exc_tb = sys.exc_info()
        #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #     print(exc_type, fname, exc_tb.tb_lineno)

    def segment_parser(self,path,rename,zon_id,file_count):
            self.dlg.progressBar_2.show()
            prg=0
            flag=0
            try:
                sql2 = f"SELECT * from {self.tbl_schema}.segment where segment_id='" + zon_id + "'"
                # print("sql2",sql2)
                # sql2 = f"SELECT * from segment where segment_id='1a08c683-4927-43d9-bcf1-a72f7c69f0a6'"
                # print(sql2)
                self.db_link.execute(sql2)
                segment_data = self.db_link.fetchone()
                # print("segment_data",segment_data)
                f = open(path, "r")
                # print(zone)
                data = json.load(f)

                f.close()
                segment_id = segment_data[1]
                if str(segment_id).lower().strip() in ['none','null','']:
                    segment_id="00000000-0000-0000-0000-000000000000"
                nav_path_id = segment_data[2]

                if str(nav_path_id).lower().strip() in ['none', 'null', '']:
                    nav_path_id = "00000000-0000-0000-0000-000000000000"
                road_code = segment_data[3]
                if isinstance(segment_data[3], int):
                    sql4 = "select description  from {self.tbl_schema}.road_class where id ={0} ;".format(segment_data[3])
                    self.db_link.execute(sql4)
                    road_code_class_desc = self.db_link.fetchone()[0]
                    road_code= road_code_class_desc
                if str(road_code).lower().strip() in ['none', 'null', '']:
                    road_code = "unlabeled(0)"

                speed_limit = segment_data[4]
                if str(speed_limit).lower().strip() in ['none', 'null', '']:
                    speed_limit = ""
                else:
                    speed_limit=int(speed_limit)

                # preferred_speed_limit = speed_limit
                # # if str(segment_data[5]) != 'None':
                # #     # print('segment_data[5]', segment_data[5])
                # #     preferred_speed_limit = int(segment_data[5])

                # adjusted_speed_limit=speed_limit
                # # if str(segment_data[6]) != 'None':
                # #     adjusted_speed_limit = int(segment_data[6])
                # segment_meta_has_qc = segment_data[7]
                # segment_meta_fake = segment_data[8]
                # segment_meta_preferred = segment_data[9]
                # segment_meta_has_traffic_guard = segment_data[10]
                # lane_line_directions_resolved = segment_data[11]

                lanes_list = []

                lane_lines_list = []
                lanes_dict = data['lanes'][0]
                lane_line_dict = data['lane_lines'][0]

                lanes_dict_trans1 = data['lanes'][0]['transitions']
                lanes_dict_trans=lanes_dict_trans1[0]
                # print('lanes_dict_trans',lanes_dict_trans )
                for key, value in data.items():
                    if key == 'id':
                        data[key]['s'] = segment_id
                    if key == 'nav_path_id':
                        data[key]['s'] = nav_path_id
                        #print(nav_path_id)

                    if key == 'road_class':

                        data[key] = road_code

                    if key == 'speed_limit':
                        #print('speed_limit', speed_limit)
                        if str(speed_limit).lower().strip() not in ['none','','null']:
                            data[key] = int(speed_limit)

                    # if key == 'preferred_speed_limit':
                    #     if str(preferred_speed_limit).lower().strip() not in ['none','','null']:
                    #         data[key] = preferred_speed_limit
                    #
                    # if key == 'adjusted_speed_limit':
                    #     if str(adjusted_speed_limit).lower().strip() not in ['none','','null']:
                    #         data[key] = adjusted_speed_limit
                    #
                    # if key == 'meta':
                    #     data[key]['has_qc'] = segment_meta_has_qc
                    #     data[key]['fake'] = segment_meta_fake
                    #     data[key]['preferred'] = segment_meta_preferred
                    #     data[key]['has_traffic_guard'] = segment_meta_has_traffic_guard
                    #
                    # if key == 'lane_line_directions_resolved':
                    #     data[key] = lane_line_directions_resolved

                    if key == 'lanes':
                        # print('gulab')
                        sql2 = f"SELECT * from {self.tbl_schema}.lanes where segment_id='" + zon_id + "'"
                        # print("sql2_lane",sql2)
                        # print(sql2)
                        self.db_link.execute(sql2)
                        lanes = self.db_link.fetchall()
                        # print("sql lanes",lanes)
                        # print("len(lanes) lanes",len(lanes))

                        left_right_list = []

                        for lane_key in lanes:
                            # print(("lane_key",lane_key))
                            lane_id=lane_key[1]
                            if str(lane_id).lower().strip() in ['none', 'null', '']:
                                lane_id = "00000000-0000-0000-0000-000000000000"
                            # print('lane_id',lane_id)
                            # print('lanes_dict',lanes_dict)
                            lanes_dict['id']['s']=lane_id
                            # print("lanes_dict",lanes_dict)

                            left_lane_line_id = lane_key[2]
                            if str(left_lane_line_id).lower().strip() not in ['null','none','']:
                                if left_lane_line_id not in left_right_list:
                                    left_right_list.append(left_lane_line_id)
                                    # print('left_lane_line_id',left_lane_line_id)
                            if str(left_lane_line_id).lower().strip() in ['none', 'null', '']:
                                left_lane_line_id = "00000000-0000-0000-0000-000000000000"
                            lanes_dict['left_lane_line_id']['s'] = left_lane_line_id

                            right_lane_line_id = lane_key[3]
                            if str(right_lane_line_id).lower().strip() not in ['null','none','']:
                                if right_lane_line_id not in left_right_list:
                                    left_right_list.append(right_lane_line_id)

                            if str(right_lane_line_id).lower().strip() in ['none', 'null', '']:
                                right_lane_line_id = "00000000-0000-0000-0000-000000000000"
                            lanes_dict['right_lane_line_id']['s'] = right_lane_line_id

                            # maybe_left_lane_line_reversed_id = lane_key[4]
                            # if str(maybe_left_lane_line_reversed_id).lower().strip() in ['none', '']:
                            #     lanes_dict['maybe_left_lane_line_reversed_id'] = None
                            # else:
                            #     lanes_dict['maybe_left_lane_line_reversed_id'] = maybe_left_lane_line_reversed_id
                            #
                            #
                            # maybe_right_lane_line_reversed_id = lane_key[5]
                            # if str(maybe_right_lane_line_reversed_id).lower().strip() in ['none', '']:
                            #     lanes_dict['maybe_right_lane_line_reversed_id'] = None
                            # else:
                            #     lanes_dict['maybe_right_lane_line_reversed_id'] = maybe_right_lane_line_reversed_id

                            #left_adj_lane_id = lane_key[6]
                            left_adj_lane_id = lane_key[4]
                            if str(left_adj_lane_id).lower().strip() in ['none', 'null', '']:
                                left_adj_lane_id = "00000000-0000-0000-0000-000000000000"
                            lanes_dict['left_adj_lane_id']['s'] = left_adj_lane_id

                            #right_adj_lane_id = lane_key[7]
                            right_adj_lane_id = lane_key[5]
                            if str(right_adj_lane_id).lower().strip() in ['none', 'null', '']:
                                right_adj_lane_id = "00000000-0000-0000-0000-000000000000"
                            lanes_dict['right_adj_lane_id']['s'] = right_adj_lane_id

                            #lane_class = lane_key[8]
                            lane_class = lane_key[6]
                            lanes_dict['lane_class'] = lane_class

                            #lane_direction = lane_key[9]
                            lane_direction = lane_key[7]
                            lanes_dict['lane_direction'] = lane_direction

                            # lane_meta_has_qc = lane_key[10]
                            # lanes_dict['meta']['has_qc'] = lane_meta_has_qc
                            #
                            # lane_meta_fake = lane_key[11]
                            # lanes_dict['meta']['fake'] = lane_meta_fake
                            #
                            # lane_meta_preferred = lane_key[12]
                            # lanes_dict['meta']['preferred'] = lane_meta_preferred
                            #
                            # lane_meta_has_traffic_guard = lane_key[13]
                            # lanes_dict['meta']['has_traffic_guard'] = lane_meta_has_traffic_guard
                            #
                            # num_total_transitions = lane_key[14]
                            # lanes_dict['num_total_transitions'] = num_total_transitions
                            # print('lanes_dict',lanes_dict)
                            # data['lanes'].append(deepcopy(lanes_dict))
                            # lanes_list.append(deepcopy(lanes_dict))
                            sql_tar = f"SELECT * from {self.tbl_schema}.transitions where entrance_id='" + lane_id + "'"
                            #print(sql_tar)
                            self.db_link.execute(sql_tar)
                            transition = self.db_link.fetchall()
                            transition_list=[]
                            for tras in transition:
                                transition_id=tras[1]
                                if str(transition_id).lower().strip() in ['none', 'null', '']:
                                    transition_id = "00000000-0000-0000-0000-000000000000"
                                lanes_dict_trans['id']['s']=transition_id
                                entrance_id=tras[2]
                                if str(entrance_id).lower().strip() in ['none', 'null', '']:
                                    entrance_id = "00000000-0000-0000-0000-000000000000"
                                lanes_dict_trans['entrance']['s'] = entrance_id
                                exit_id = tras[3]
                                if str(exit_id).lower().strip() in ['none', 'null', '']:
                                    exit_id = "00000000-0000-0000-0000-000000000000"
                                lanes_dict_trans['exit']['s'] = exit_id
                                # zone = tras[4]
                                # if str(zone).lower().strip() in ['none', 'null', '']:
                                #     zone = "00000000-0000-0000-0000-000000000000"
                                # lanes_dict_trans['zone']['s'] = zone
                                # bulb_groups = tras[5]
                                # if str(bulb_groups).lower().strip() not in ['none','null',''] :
                                #     bulb_groups=tras[5]
                                # else:
                                #     bulb_groups=[]
                                # lanes_dict_trans['bulb_groups'] = bulb_groups
                                # ref_path = tras[6]
                                # if str(ref_path).lower().strip() in ['none', '']:
                                #     lanes_dict_trans['ref_path'] = None
                                # else:
                                #     lanes_dict_trans['ref_path'] = ref_path
                                # left_boundary = tras[7]
                                # lanes_dict_trans['left_boundary'] = left_boundary
                                # right_boundary = tras[8]
                                # lanes_dict_trans['right_boundary'] = right_boundary
                                # control_type = tras[9]
                                # if str(control_type).lower().strip() in ['none', 'null', '']:
                                #     control_type = "None"
                                # lanes_dict_trans['control_type'] = control_type
                                # turn_type = tras[10]
                                # if str(turn_type).lower().strip() in ['none', 'null', '']:
                                #     turn_type = "Continue(0)"
                                # lanes_dict_trans['turn_type'] = turn_type
                                # entrance_endside = tras[11]
                                # if str(entrance_endside).lower().strip() in ['none', 'null', '']:
                                #     entrance_endside = "back(1)"
                                # lanes_dict_trans['entrance_endside'] = entrance_endside
                                # exit_endside = tras[12]
                                # if str(exit_endside).lower().strip() in ['none', 'null', '']:
                                #     exit_endside = "front(0)"
                                # lanes_dict_trans['exit_endside'] = exit_endside
                                # transition_meta_has_qc = tras[13]
                                # lanes_dict_trans['meta']['has_qc'] = transition_meta_has_qc
                                # transition_meta_fake = tras[14]
                                # lanes_dict_trans['meta']['fake'] = transition_meta_fake
                                # transition_meta_preferred = tras[15]
                                # lanes_dict_trans['meta']['preferred'] = transition_meta_preferred
                                # transition_meta_has_traffic_guard = tras[16]
                                # lanes_dict_trans['meta']['has_traffic_guard'] = transition_meta_has_traffic_guard
                                # right_of_way = tras[17]
                                # if str(right_of_way).lower().strip() in ['none', 'null', '']:
                                #     right_of_way='unlabeled'
                                # lanes_dict_trans['right_of_way'] = right_of_way
                                # oncoming_traffic = tras[18]
                                # if str(oncoming_traffic).lower().strip() in ['none', 'null', '']:
                                #     oncoming_traffic='false'
                                # lanes_dict_trans['oncoming_traffic'] = oncoming_traffic
                                # no_turn_on_red = tras[19]
                                # lanes_dict_trans['no_turn_on_red'] = no_turn_on_red
                                # ego_non_drivable = tras[20]
                                # if str(ego_non_drivable).lower().strip() in ['false']:
                                #     ego_non_drivable = False
                                # lanes_dict_trans['ego_non_drivable'] = ego_non_drivable
                                transition_list.append(deepcopy(lanes_dict_trans))

                            lanes_dict['transitions'] = transition_list
                            # lanes_dict['num_total_transitions'] = len(transition_list)
                            lanes_list.append(deepcopy(lanes_dict))

                    if key == 'lane_lines':
                        # print('left_right_list',left_right_list)
                        for lane_ids in left_right_list:
                            crds = f"SELECT ST_AsGeoJSON(geom):: json from {self.tbl_schema}.lane_lines where lane_id='" + lane_ids + "'"
                            #print(crds)
                            self.db_link.execute(crds)
                            lane_line_geom = self.db_link.fetchone()
                            lane_line_geom_json = lane_line_geom[0]['coordinates']
                            sql4 = f"SELECT * from {self.tbl_schema}.lane_lines where lane_id='" + lane_ids + "'"
                            #print(sql4)
                            self.db_link.execute(sql4)
                            lane_line_data = self.db_link.fetchone()
                            if str(lane_ids).lower().strip() in ['none', 'null', '']:
                                lane_ids = "00000000-0000-0000-0000-000000000000"
                            lane_line_dict['id']['s'] = lane_ids
                            lane_line_type=lane_line_data[3]
                            line_cordinate = []
                            for i in lane_line_geom_json:
                                # print(i)
                                x = i[0]
                                y = i[1]
                                z = i[2]
                                lat1, lon1, alt1 = self.transform(x, y, z)
                                final_matrix = {
                                    "matrix": [
                                        [
                                            lat1,
                                            lon1,
                                            alt1
                                        ]
                                    ]
                                }
                                line_cordinate.append(deepcopy(final_matrix))
                            lane_line_dict['polyline']['waypoints'] = line_cordinate
                            lane_line_dict['type'] = lane_line_type
                            # lane_line_meta_has_qc=lane_line_data[4]
                            # lane_line_dict['meta']['has_qc'] = lane_line_meta_has_qc
                            # lane_line_meta_fake=lane_line_data[5]
                            # lane_line_dict['meta']['fake'] = lane_line_meta_fake
                            # lane_line_meta_preferred=lane_line_data[6]
                            # lane_line_dict['meta']['preferred'] = lane_line_meta_preferred
                            # lane_line_meta_has_traffic_guard=lane_line_data[7]
                            # lane_line_dict['meta']['has_traffic_guard'] = lane_line_meta_has_traffic_guard
                            lane_lines_list.append(deepcopy(lane_line_dict))
                            pass
                    percent = prg / float(file_count) * 100
                    self.dlg.progressBar_2.setValue(percent+1)
                    prg += 1
                # if len(lanes_list)!=0:
                data['lanes']=lanes_list
                data['lane_lines']=lane_lines_list
                jsonFile = open(rename, "w+")
                jsonFile.write(json.dumps(data))
                jsonFile.close()
                self.dlg.progressBar_2.setValue(100)
                # self.dlg.progressBar_2.hide()
                
            except Exception as e:
                flag=1
                print(e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                # self.iface.messageBar().pushMessage(exc_type, fname, exc_tb.tb_lineno,level=Qgis.Critical)
                self.connection_db.rollback()
                self.iface.messageBar().pushMessage("Error segment_id - ",f"{str(segment_id)}   {str(e)}",level=Qgis.Critical)
                # QMessageBox.critical(self.dlg,'Critical','Data Not Exported .')
                # self.connection_db.close()
            return flag
            

    def zone_parser(self,path,rename,zon_id):
        # try:
            sql2 = f"SELECT * from {self.tbl_schema}.zone where zone_id='" + zon_id +"'"
            #print(sql2)
            self.db_link.execute(sql2)
            zone_data = self.db_link.fetchone()
            # print("zone_data",zone_data)

            sql3 = f"SELECT ST_AsGeoJSON(geom):: json from {self.tbl_schema}.zone where zone_id='" + zon_id +"'"
            self.db_link.execute(sql3)
            zone_geom = self.db_link.fetchone()
            geom_json=zone_geom[0]['coordinates']
            # print('geom_json',geom_json)
            # for zone in zones:
            # print('zone',zone)

            f=open(path, "r")
            # print(zone)
            data = json.load(f)
            line_cordinate = []
            zone_id = zone_data[1]
            # meta_has_qc = zone_data[2]
            # meta_fake = zone_data[3]
            # meta_preferred = zone_data[4]
            # meta_has_traffic_guard = zone_data[5]
            # edge_meta_is_crosswalk_entrance = zone_data[6]
            # edge_meta_is_crossable = zone_data[7]
            # traffic_lights = zone_data[8]
            traffic_lights = []
            type = zone_data[3]
            # sub_zones = zone_data[10]
            #sub_zones = []
            for key, value in data.items():
                if key == 'id':
                    data[key]['s'] = zone_id
                    # print(zone_id)

                # if key == 'meta':
                #     # meta = data[key]
                #     data[key]['has_qc'] = meta_has_qc
                #     data[key]['fake'] = meta_fake
                #     data[key]['preferred'] = meta_preferred
                #     data[key]['has_traffic_guard'] = meta_has_traffic_guard

                # if key == 'edge_meta':
                #     # data[key] = type
                #     data[key]['is_crosswalk_entrance'] = edge_meta_is_crosswalk_entrance
                #     data[key]['is_crossable'] = edge_meta_is_crossable
                #     # print(type_Intersection)

                if key == 'type':
                    data[key] = type

                if key == 'traffic_lights':
                    data[key] = traffic_lights

                # if key == 'sub_zones':
                #     data[key] = sub_zones
                #     # if len(data[key]) > 0:
                #     #     sub_zones = data[key][0]
                #     # else:
                #     #     sub_zones = ''
                if key == 'boundaries':
                    for i in geom_json:
                        # print(i)
                        x = i[0]
                        y = i[1]
                        z = i[2]
                        lat1, lon1, alt1 = self.transform(x, y, z)
                        final_matrix = {
                            "matrix": [
                                [
                                    lat1,
                                    lon1,
                                    alt1
                                ]
                            ]
                        }
                        line_cordinate.append(deepcopy(final_matrix))
                    data[key][0]['edges'][0]['waypoints'] = line_cordinate

            f.close()
            jsonFile = open(rename, "w+")
            jsonFile.write(json.dumps(data))
            jsonFile.close()
        # except Exception as e:
        #     exc_type, exc_obj, exc_tb = sys.exc_info()
        #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #     print(exc_type, fname, exc_tb.tb_lineno)
        #     self.connection_db.rollback()

    def transform(self , x ,y ,z):
        transformer = pyproj.Transformer.from_crs(
            {"proj": 'latlong', "ellps": 'WGS84', "datum": 'WGS84'},
            {"proj": 'geocent', "ellps": 'WGS84', "datum": 'WGS84'},

        )
        lon1, lat1, alt1 = transformer.transform(x, y, z, radians=False)
        return lon1, lat1, alt1

class loadargs:
    try:
        path2 = os.path.dirname(__file__)
        path2 = path2.replace("\\", "/")
        path = os.path.join(path2, "PostgresAppConfig.json")
        #print(path)
        if os.path.exists(path):
            with open(path, encoding='utf-8') as json_file:
                data = json.load(json_file)
                pass
            pass
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
    # print("data", data)

class DatabaseConnection:
    def __init__(self,databasestrings):
        self.host = databasestrings['host']
        self.port = databasestrings['port']
        self.user = databasestrings['user']
        self.pwd = databasestrings['pwd']
        self.databas = databasestrings['db']
        self.schem = databasestrings['schema']
        try:
            self.conn = psycopg2.connect(database=self.databas,user=self.user, password=self.pwd,host=self.host,port=int(self.port))
            self.curs = self.conn.cursor()
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            return

if __name__ == "__main__":
    DatabaseConnection = DatabaseConnection(loadargs.data['database'])






