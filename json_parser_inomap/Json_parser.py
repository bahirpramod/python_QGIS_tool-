import pyproj
import psycopg2
import json
import os
import sys
# import tkinter
# import postgres_to_Json_parser
import datetime
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtWidgets import*
# from tkinter import END, filedialog, ttk, messagebox


class JsonParser:

    
    def __init__(self, mainpath, Dbconnection,iFace):
        try:
            self.mainpath = mainpath
            self.host = Dbconnection.host
            self.database = Dbconnection.databas
            self.user = Dbconnection.user
            self.password = Dbconnection.pwd
            self.port = int(Dbconnection.port)
            self.db_link = Dbconnection.curs
            self.connection_db = Dbconnection.conn
            self.tbl_schema = Dbconnection.schem
            self.dlg=Dbconnection.dlg
            self.iface=iFace
            self.lable=Dbconnection
            print("self.tbl_schema pramod",self.tbl_schema)
            self.lable.set_Lable_schema(self.tbl_schema)
                     
            self.file_name(self.mainpath)
                       
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #print(exc_type, fname, exc_tb.tb_lineno)
            self.iface.messageBar().pushMessage("Error",fname,level=Qgis.Critical)

    def file_name_sublevel(self, dirpath):
        try:
            for path in dirpath:
                #print(path)
                return
                segments = []
                zones = []
                for file in os.listdir(path):
                    if file.endswith('.segment') and (not file.startswith('._')):
                        segments.append(path + '\\' + str(file))
                    elif file.endswith('.zone') and (not file.startswith('._')):
                        zones.append(path + '\\' + str(file))
                # if len(segments) > 0:
                    self.segment_parser(segments)
                #     pass
                    # print(segments)
                if len(zones) > 0:
                    self.zone_parser(zones)
                    pass
                    # print(zones)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.iface.messageBar().pushMessage("Error",fname,level=Qgis.Critical)
            # print(exc_type, fname, exc_tb.tb_lineno)

    def file_name(self, dirpath):
        try:
            segments = []
            zones = []
            
            for file in os.listdir(dirpath):
                if file.endswith('.segment') and (not file.startswith('._')):
                    segments.append(dirpath + '\\' + str(file))
                elif file.endswith('.zone') and (not file.startswith('._')):
                    zones.append(dirpath + '\\' + str(file))
            file_count=int(len(segments))
            # print("count",count)
            if len(segments) > 0:
                # print("pramod",segments)
                self.flag=self.segment_parser(segments,file_count)
                pass
                #print(segments)
                
            if len(zones) > 0:
                #print(zones)
                self.zone_parser(zones)
                pass
                #print(zones)
            print("self.flag",self.flag)
            if self.flag==0:
                    QMessageBox.information(self.dlg,'Information','Data Imported Successfully.')
            else:
                QMessageBox.critical(self.dlg,'Critical','Data Not Imported .')
            return
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            #print(exc_type, fname, exc_tb.tb_lineno)
            self.iface.messageBar().pushMessage("Error",fname,level=Qgis.Critical)

        # print("self.flag",self.flag)
        # if self.flag==0:
        #         QMessageBox.information(self.dlg,'Information','Data Imported Successfully.')
        # else:
        #     QMessageBox.critical(self.dlg,'Critical','Data Not Imported .')

    def segment_parser(self, segments,file_count):
        # print("jhfjg11")
        self.dlg.progressBar.show()
        flag=0
        # item = QListWidgetItem()
        # print("jhfjg")

        try:
            # print("1245+65")
            counter = 0
            prg = 0 
            for segment in segments:
                counter = counter + 1
                # print(segment)
                with open(segment) as f:
                    data = json.load(f)
                segment_id = ''
                nav_path_id = ''
                speed_limit = ''
                #preferred_speed_limit = ''
                road_code = ''
                

                for key, value in data.items():

                    # print(key, value)
                    if key == 'id':
                        segment_id = data[key]['s']
                        # print(counter," - segment_id",segment_id)
                        self.lable.Lable_changed(counter,segment_id)
                        # item.setText(segment_id)
                        # self.dlg.listWidget.addItem(item)
                    if key == 'nav_path_id':
                        nav_path_id = data[key]['s']
                        # print(nav_path_id)
                    if key == 'road_class':
                        # print("data[key]",data[key])
                        if isinstance(data[key], int):
                            # print("test")
                            # print("data[key]",data[key])
                            sql4 ="select description  from  {self.tbl_schema}.road_class where id ='{0}' ;".format(data[key])
                            self.db_link.execute(sql4)
                            road_code_class_desc  = self.db_link.fetchone()[0]
                            # print("road_class_desc",road_code_class_desc)
                            data[key]=road_code_class_desc
                            # print("data[key]",data[key])
                        road_code_class = data[key].capitalize()
                        # if data[key]is_integer()==True:
                        #     road_code_class = data[key]
                        # else:
                        #     road_code_class = data[key].capitalize()

                        road_code_class = road_code_class.split('(')
                        # print(str(road_code_class[0]))
                        sql = "SELECT id from " + self.tbl_schema + "." + "road_class where description = " + "'" + \
                              str(road_code_class[0]) + "'"

                        # print("sql",sql)
                        self.db_link.execute(sql)
                        road_code = self.db_link.fetchone()[0]
                        # road_code = road_code_class
                        # print("road_code",road_code)
                        # return
                    if key == 'speed_limit':
                        speed_limit = data[key]
                        # print(speed_limit)
                    
                    if key == 'lanes':
                        lanes = data[key]
                        for lane in range(len(lanes)):
                            lane_id = ''
                            left_lane_line_id = ''
                            right_lane_line_id = ''
                            # maybe_left_lane_line_reversed_id = ''
                            # maybe_right_lane_line_reversed_id = ''
                            left_adj_lane_id = ''
                            right_adj_lane_id = ''
                            lane_class = ''
                            lane_direction = ''
                            
                            for lane_key in lanes[lane]:
                                if lane_key == 'id':
                                    lane_id = lanes[lane][lane_key]['s']
                                    #print(lane_id)

                                if lane_key == 'left_lane_line_id':
                                    left_lane_line_id = lanes[lane][lane_key]['s']
                                    # print(left_lane_line_id)
                                    # return

                                if lane_key == 'right_lane_line_id':
                                    right_lane_line_id = lanes[lane][lane_key]['s']
                                    # print(right_lane_line_id)

                               
                                if lane_key == 'left_adj_lane_id':
                                    left_adj_lane_id = lanes[lane][lane_key]['s']
                                    # print(left_adj_lane_id)

                                if lane_key == 'right_adj_lane_id':
                                    right_adj_lane_id = lanes[lane][lane_key]['s']
                                    # print(right_adj_lane_id)

                                if lane_key == 'transitions':
                                    transition_num = 0
                                    for transition in lanes[lane][lane_key]:
                                        transition_id = ''
                                        entrance_id = ''
                                        exit_id = ''
                                        
                                        for transition_key in transition:

                                            if transition_key == 'id':
                                                transition_id = lanes[lane][lane_key][transition_num][transition_key]['s']
                                                # print(transition_id)

                                            if transition_key == 'entrance':
                                                entrance_id = lanes[lane][lane_key][transition_num][transition_key]['s']
                                                # print(entrance_id)

                                            if transition_key == 'exit':
                                                # print(transition_num)
                                                exit_id = lanes[lane][lane_key][transition_num][transition_key]['s']
                                                # print(exit_id)

                                            

                                        transition_num+= 1

                                        tabl = 'transitions'

                                        sql3 = "insert into " + self.tbl_schema + "." + tabl + " (transition_id,entrance_id,exit_id) " \
                                                                                               "values (%s,%s,%s)"
                                        # sql3 = "insert into " + self.tbl_schema + "." + tabl + " (transition_id,entrance_id,exit_id,zone,ref_path,control_type,turn_type,entrance_endside,exit_endside,meta_has_qc,meta_fake,meta_preferred,meta_has_traffic_guard,right_of_way,oncoming_traffic,no_turn_on_red,ego_non_drivable) " \
                                        #                                                       "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                                        # print("sql3",sql3)

                                        self.db_link.execute(sql3, (
                                            str(transition_id), str(entrance_id), str(exit_id)))

                                       
                                        # self.connection_db.commit()

                                if lane_key == 'lane_class':
                                    lane_class = lanes[lane][lane_key]
                                    # print(lane_class)

                                if lane_key == 'lane_direction':
                                    lane_direction = lanes[lane][lane_key]
                                    # print(lane_direction)

                                if lane_key == 'meta':
                                    lane_meta_has_qc = lanes[lane][lane_key]['has_qc']
                                    lane_meta_fake = lanes[lane][lane_key]['fake']
                                    lane_meta_preferred = lanes[lane][lane_key]['preferred']
                                    lane_meta_has_traffic_guard = lanes[lane][lane_key]['has_traffic_guard']

                                    # print(lane_meta)

                                if lane_key == 'num_total_transitions':
                                    num_total_transitions = lanes[lane][lane_key]
                                    # print(num_total_transitions)
                            tabl = 'lanes'
                            sql3 = "insert into " + self.tbl_schema + "." + tabl + " (lane_id,left_lane_id,right_lane_id,left_adj_lane_id,right_adj_lane_id,lane_class,lane_direction,segment_id) " \
                                                                                   "values (%s,%s,%s,%s,%s,%s,%s,%s)"
                            
                            self.db_link.execute(sql3, (
                                str(lane_id), str(left_lane_line_id), str(right_lane_line_id),
                                str(left_adj_lane_id), str(right_adj_lane_id), str(lane_class), str(lane_direction),
                                str(segment_id)))
                           
                            # self.connection_db.commit()
                    if key == 'lane_lines':
                        lane_lines = data[key]
                        # with open(id + '.csv', 'w', encoding='UTF8', newline='') as f:
                        for lane_line in range(len(lane_lines)):
                            # header = ['index', 'lane_line_key', 'Lat', 'Long', 'altitude']
                            # writer = csv.writer(f)
                            # writer.writerow(header)
                            lane_line_key_id = ''
                            lane_line_type = ''
                            # lane_line_meta_has_qc = ''
                            # lane_line_meta_fake = ''
                            # lane_line_meta_preferred = ''
                            # lane_line_meta_has_traffic_guard = ''
                            line_cordinate = []
                            for lane_line_key in lane_lines[lane_line]:
                                index = 1
                                if lane_line_key == 'id':
                                    lane_line_key_id = lane_lines[lane_line][lane_line_key]['s']
                                    # print(lane_line_key_id)
                                    lane_line_inde = lane_line_key_id

                                if lane_line_key == 'polyline':
                                    polyline = lane_lines[lane_line][lane_line_key]['waypoints']
                                    for point in polyline:
                                        x = point['matrix'][0][0]
                                        y = point['matrix'][0][1]
                                        z = point['matrix'][0][2]
                                        index += 1
                                        lat1, lon1, alt1 = self.transform(x, y, z)
                                        cord = [lat1, lon1, alt1]
                                        line_cordinate.append(cord)
                                        # print(lat1, lon1, alt1)
                                        # row = [index, lane_line_inde, lat1, lon1, alt1]
                                        # writer.writerow(row)

                                if lane_line_key == 'type':
                                    lane_line_type = lane_lines[lane_line][lane_line_key]
                                    # print(lane_line_type)

                               
                            # print(line_cordinate)
                            tabl = 'lane_lines'
                            # print(line_cordinate)
                            points = []
                            for i in line_cordinate:
                                sql1 = f"SELECT st_makepoint{str(i[0]), str(i[1]), str(i[2])}"
                                # print(sql1)
                                self.db_link.execute(sql1)
                                points.append(self.db_link.fetchall())
                            geomstring = ''
                            points_len = len(points)
                            count = 0
                            for point in points:
                                count += 1
                                for p in point:
                                    if count < points_len:
                                        geomstring += str("'" + p[0] + "'" + ",")
                                    else:
                                        geomstring += str("'" + p[0] + "'")
                            sql2 = f"SELECT ST_MakeLine(ARRAY[{geomstring}])"
                            # print(sql2)
                            self.db_link.execute(sql2)
                            lane_geom = self.db_link.fetchall()
                            # print(segment_geom)

                            sql3 = "insert into " + self.tbl_schema + "." + tabl + " (lane_id,geom,type) " \
                                                                                   "values (%s,%s,%s)"

                            # sql3 = "insert into " + self.tbl_schema + "." + tabl + " (lane_id,geom,type,meta_has_qc,meta_fake,meta_preferred,meta_has_traffic_guard) " \
                            #                                                        "values (%s,%s,%s,%s,%s,%s,%s)"

                            # print(sql3)
                            self.db_link.execute(sql3, (
                                str(lane_line_key_id), lane_geom[0][0], str(lane_line_type)))

                            # self.connection_db.commit()
                tabl = 'segment'
                sql3 = "insert into " + self.tbl_schema + "." + tabl + " (segment_id,nav_path_id,road_code,speed_limit) " \
                                                                       "values (%s,%s,%s,%s)"
                # sql3 = "insert into " + self.tbl_schema + "." + tabl + " (segment_id,nav_path_id,road_code,speed_limit,preferred_speed_limit,adjusted_speed_limit,meta_has_qc,meta_fake,meta_preferred,meta_has_traffic_guard,lane_line_directions_resolved) " \
                #                                                        "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                # print(sql3)
                self.db_link.execute(sql3, (
                    str(segment_id), str(nav_path_id), str(road_code),
                    str(speed_limit)))
               
                
                percent = prg / float(file_count) * 100
                self.dlg.progressBar.setValue(percent+1)
                prg += 1
            if flag==0:
                self.connection_db.commit()
                # QMessageBox.information(self.dlg,'Information','Data Imported Successfully.')
                
            
        except Exception as e:
            # print(e)
            flag=1
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            self.iface.messageBar().pushMessage("Error segment_id- ",f"{str(segment_id)} {str(e)}",level=Qgis.Critical)
            self.connection_db.rollback()
            # QMessageBox.critical(self.dlg,'Critical','Data Not Imported ')
            # self.connection_db.close()
        return flag
        
        

    def zone_parser(self, zones):
        try:
            for zone in zones:
                with open(zone) as f:
                    # print(zone)
                    data = json.load(f)
                    line_cordinate = []
                    zone_id = ''
                    meta_has_qc = ''
                    meta_fake = ''
                    meta_preferred = ''
                    meta_has_traffic_guard = ''
                    edge_meta_is_crosswalk_entrance = ''
                    edge_meta_is_crossable = ''
                    traffic_lights = ''
                    type = ''
                    sub_zones = ''
                    for key, value in data.items():
                        if key == 'id':
                            zone_id = data[key]['s']
                            # print(zone_id)

                        # if key == 'meta':
                        #     meta = data[key]
                        #     meta_has_qc = data[key]['has_qc']
                        #     meta_fake = data[key]['fake']
                        #     meta_preferred = data[key]['preferred']
                        #     meta_has_traffic_guard = data[key]['has_traffic_guard']

                        if key == 'boundaries':
                            edges = data[key][0]['edges'][0]['waypoints']
                            # with open(id_key + '.csv', 'w', encoding='UTF8', newline='') as f:
                            # header = ['index', 'Lat', 'Long', 'altitude']
                            # writer = csv.writer(f)
                            # writer.writerow(header)
                            index = 1

                            for edge in edges:
                                x = edge['matrix'][0][0]
                                y = edge['matrix'][0][1]
                                z = edge['matrix'][0][2]
                                index += 1
                                lat1, lon1, alt1 = self.transform(x, y, z)
                                cord = [str(lat1), str(lon1), str(alt1)]
                                line_cordinate.append(cord)
                                # row = [index, lat1, lon1, alt1]
                                # writer.writerow(row)
                            # print(line_cordinate)
                            # edge_meta = data[key][0]['edge_meta']
                            # edge_meta_is_crosswalk_entrance = data[key][0]['edge_meta'][0]['is_crosswalk_entrance']
                            # edge_meta_is_crossable = data[key][0]['edge_meta'][0]['is_crossable']

                        # if key == 'traffic_lights':
                        #     traffic_lights = ''
                        #     # print(data[key])
                        #     if len(data[key]) > 0:
                        #         traffic_lights = data[key]
                        #         # print("traffic_lights",traffic_lights)
                        #         for traff in data[key]:
                        #             traff_id = traff['id']['s']
                        #             # print(traff_id)
                        #             se3 = traff['se3']['so3']
                        #             # print('se3',se3)
                        #             translation = traff['se3']['translation']['matrix']
                        #             covariance = traff['covariance']['matrix']
                        #             # print('covariance',covariance)
                        #             major_id = traff['rule_book_id']['major_id']
                        #             mod_id = traff['rule_book_id']['mod_id']
                        #             meta = traff['meta']
                        #             traffic_has_qc = meta['has_qc']
                        #             traffic_fake = meta['fake']
                        #             traffic_preferred = meta['preferred']
                        #             traffic_has_traffic_guard = meta['has_traffic_guard']
                        #             x = translation[0][0]
                        #             y = translation[0][1]
                        #             z = translation[0][2]
                        #
                        #             lat1, lon1, alt1 = self.transform(x, y, z)
                        #
                        #             sql1 = f"SELECT st_makepoint{str(lat1), str(lon1), str(alt1)}"
                        #             # print(sql1)
                        #             self.db_link.execute(sql1)
                        #             geom = self.db_link.fetchone()[0]
                        #
                        #             sql3 = "insert into " + self.tbl_schema + ".traffic_light (traffic_light_id, zone_id,so3,geom,covariance,meta_has_qc,meta_fake,meta_preferred,meta_has_traffic_guard,rule_book_major_id,rule_book_mod_id) " \
                        #                                                       "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                        #
                        #             self.db_link.execute(sql3, (
                        #                 str(traff_id), str(zone_id), json.dumps(se3), geom, covariance,
                        #                 str(traffic_has_qc),
                        #                 str(traffic_fake), str(traffic_preferred), str(traffic_has_traffic_guard),
                        #                 str(major_id), str(mod_id)))
                        #             # print(str(zone_id), str(meta_has_qc),str(meta_fake),str(meta_preferred),str(meta_has_traffic_guard),str(edge_meta_is_crosswalk_entrance),str(edge_meta_is_crossable),str(traffic_lights),str(type),str(sub_zones),str(zone_geom[0][0]))
                        #             self.connection_db.commit()
                        #             # print(covariance)
                        #             ########bulbs data
                        #             bulbs_data = traff['bulbs']
                        #             for bulbs_data in bulbs_data:
                        #                 bulb_id = bulbs_data['id']['s']
                        #                 color = bulbs_data['color']
                        #                 bulb_type = bulbs_data['type']
                        #                 arrow_direction = bulbs_data['arrow_direction']
                        #                 # meta=bulbs_data['meta']
                        #                 has_qc = bulbs_data['meta']['has_qc']
                        #                 fake = bulbs_data['meta']['fake']
                        #                 preferred = bulbs_data['meta']['preferred']
                        #                 has_traffic_guard = bulbs_data['meta']['has_traffic_guard']
                        #                 sql4 = "insert into " + self.tbl_schema + ".bulbs (bulb_id, traffic_light_id,color,bulb_type,arrow_direction,meta_has_qc,meta_fake,meta_preferred,meta_has_traffic_guard) " \
                        #                                                           "values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                        #
                        #                 self.db_link.execute(sql4, (
                        #                     str(bulb_id), str(traff_id), str(color), str(bulb_type),
                        #                     str(arrow_direction),
                        #                     str(has_qc),
                        #                     str(fake), str(preferred), str(has_traffic_guard)))
                        #
                        #             ######bulbs_group_data
                        #             bulbs_group_data = traff['bulb_groups']
                        #             for bulbs_gr in bulbs_group_data:
                        #                 bulb_group_id = bulbs_gr['id']['s']
                        #                 bulbs = bulbs_gr['bulbs']
                        #                 bulb_list = [f['s'] for f in bulbs]
                        #                 bulbs_group_has_qc = bulbs_gr['meta']['has_qc']
                        #                 bulbs_group_fake = bulbs_gr['meta']['fake']
                        #                 bulbs_group_preferred = bulbs_gr['meta']['preferred']
                        #                 bulbs_group_has_traffic_guard = bulbs_gr['meta']['has_traffic_guard']
                        #                 # print('bulb_group_id',bulbs_group_has_traffic_guard)
                        #
                        #                 sql5 = "insert into " + self.tbl_schema + ".bulb_group (bulb_group_id, bulb_ids,meta_has_qc,meta_fake,meta_preferred,meta_has_traffic_guard) " \
                        #                                                           "values (%s,%s,%s,%s,%s,%s)"
                        #
                        #                 self.db_link.execute(sql5, (
                        #                     str(bulb_group_id), bulb_list,
                        #                     str(bulbs_group_has_qc),
                        #                     str(bulbs_group_fake), str(bulbs_group_preferred),
                        #                     str(bulbs_group_has_traffic_guard)))
                        #     else:
                        #         traffic_lights = ''
                        #     # print(traffic_lights)

                        if key == 'type':
                            type = data[key]
                            # print(type_Intersection)

                        # if key == 'sub_zones':
                        #     if len(data[key]) > 0:
                        #         sub_zones = data[key][0]
                        #     else:
                        #         sub_zones = ''
                            # print(sub_zones)

                    tabl = 'zone'
                    # print(line_cordinate)
                    points = []
                    for i in line_cordinate:
                        sql1 = f"SELECT st_makepoint{str(i[0]), str(i[1]), str(i[2])}"
                        # print(sql1)
                        self.db_link.execute(sql1)
                        points.append(self.db_link.fetchall())

                    geomstring = ''
                    points_len = len(points)
                    count = 0
                    for point in points:
                        count += 1
                        for p in point:
                            if count < points_len:
                                geomstring += str("'" + p[0] + "'" + ",")
                            else:
                                geomstring += str("'" + p[0] + "'")

                    sql2 = f"SELECT ST_MakeLine(ARRAY[{geomstring}])"
                    # print(sql2)
                    self.db_link.execute(sql2)
                    zone_geom = self.db_link.fetchall()
                    # print("zone_geom",zone_geom)
                    # sql3 = "insert into " + self.tbl_schema + "." + tabl + " (zone_id, meta_has_qc,meta_fake,meta_preferred,meta_has_traffic_guard,edge_meta_is_crosswalk_entrance,edge_meta_is_crossable,type,sub_zones,geom) " \
                    #                                                        "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    #
                    # # print(sql3)
                    # self.db_link.execute(sql3, (
                    #     str(zone_id), str(meta_has_qc), str(meta_fake), str(meta_preferred),
                    #     str(meta_has_traffic_guard),
                    #     str(edge_meta_is_crosswalk_entrance), str(edge_meta_is_crossable), str(type), str(sub_zones),
                    #     zone_geom[0][0]))

                    sql3 = "insert into " + self.tbl_schema + "." + tabl + " (zone_id,type,geom) " \
                                                                           "values (%s,%s,%s)"
                    #print(sql3)
                    print(str(zone_id),  str(type),
                          str(zone_geom[0][0]))
                    self.db_link.execute(sql3, (
                        str(zone_id), str(type),
                        zone_geom[0][0]))
                    #print(str(zone_id), str(meta_has_qc),str(meta_fake),str(meta_preferred),str(meta_has_traffic_guard),str(edge_meta_is_crosswalk_entrance),str(edge_meta_is_crossable),str(traffic_lights),str(type),str(sub_zones),str(zone_geom[0][0]))
                    if flag ==0:
                        self.connection_db.commit()

        except Exception as e:
            flag=1
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            self.connection_db.rollback()
            

    def transform(self, x, y, z):
        transformer = pyproj.Transformer.from_crs(
            {"proj": 'geocent', "ellps": 'WGS84', "datum": 'WGS84'},
            {"proj": 'latlong', "ellps": 'WGS84', "datum": 'WGS84'},

        )
        lon1, lat1, alt1 = transformer.transform(x, y, z, radians=False)
        return lon1, lat1, alt1






# class loadargs:
#     try:
#         path2 = os.path.dirname(__file__)
#         path2 = path2.replace("\\", "/")
#         path = os.path.join(path2, "AppConfig.json")
#         if os.path.exists(path):
#             with open(path, encoding='utf-8') as json_file:
#                 data = json.load(json_file)
#                 pass
#             pass

#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#     # print("data", data)

# class DatabaseConnection:
#     def __init__(self, databasestrings):
#         self.host = databasestrings['host']
#         self.port = databasestrings['port']
#         self.user = databasestrings['user']
#         self.pwd = databasestrings['pwd']
#         self.databas = databasestrings['db']
#         self.schem = databasestrings['schema']
#         try:
#             self.conn = psycopg2.connect(database=self.databas, user=self.user, password=self.pwd, host=self.host,
#                                          port=int(self.port))
#             self.curs = self.conn.cursor()
#         except Exception as e:
#             print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
#             return

# class InoMap:
#     def __init__(self, tw):
#         try:
#             self.percentage = None
#             self.percentage_postgres = None
#             self.tw = tw
#             self.tw.title("InoMap App")
#             screenwidth = tw.winfo_screenwidth()
#             screenheight = tw.winfo_screenheight()
#             width = screenwidth
#             height = screenheight
#             self.tw.configure(bg='black')
#             #self.tw.geometry("1200x500")
#             #self.tw.eval('tk::PlaceWindow . center')
#             self.tw.geometry(f"{width-50}x{200}")
#             self.tw.resizable(True, False)
#             self.tabControl = ttk.Notebook(self.tw,width=width-20, height=height-60)
#             self.tab1 = ttk.Frame(self.tabControl)
#             self.tab2 = ttk.Frame(self.tabControl)
#             self.tabControl.add(self.tab1, text='JSON to Postgres')
#             self.tabControl.add(self.tab2, text='Postgres to JSON')
#             self.tabControl.grid(row=0, column=2, columnspan=3, pady=5, padx=5)
#             # Local widgets
#             # TODO: JSon to Postgres UI
#             self.l1 = tkinter.Label(self.tab1, text="Input Path : ", font=("HelvLight", 16))
#             self.l1.grid(row=0, column=1, pady=5, padx=5)
#             self.imagepath = tkinter.Entry(self.tab1, font=("HelvLight", 16), width=80, bg='white', borderwidth=0)
#             self.imagepath.insert(0, "Input Path")
#             self.imagepath.grid(row=0, column=2, columnspan=3, pady=5, padx=5)
#             self.imagepath.bind("<Button-1>", lambda event: self.clear_entry(self.imagepath))

#             self.folderbrowsebutton = tkinter.Button(self.tab1, text="Browse", command=self.getdirpath, borderwidth=0,
#             font=("HelvLight", 16),
#             bg='white')
#             self.folderbrowsebutton.grid(row=0, column=13, pady=5, padx=5)

#             self.btn1 = tkinter.Button(self.tab1, text="RUN",height=1,width=20 ,command=self.jsontopostgress, font=("HelvLight", 16),
#             bg='white')
#             self.btn1.grid(row=6, column=2, pady=10, padx=10)

#             self.btn2 = tkinter.Button(self.tab1, text="Cancel",height=1,width=20, command=self.finish, font=("HelvLight", 16),
#             bg='white')
#             self.btn2.grid(row=6, column=3, pady=10, padx=10)

#             self.pb = ttk.Progressbar(
#                 self.tab1,
#                 orient='horizontal',
#                 mode='determinate',
#                 length=560
#             )
#             self.pb.grid(row=8, column=2, pady=5, padx=5)
#             # label
#             self.value_label = ttk.Label(self.tab1, text=self.update_progress_label())
#             self.value_label.grid(row=9, column=2, pady=5, padx=5)
#             # TODO: Postgres to JSon UI
#             self.l1 = tkinter.Label(self.tab2, text="Input Path : ", font=("HelvLight", 16))
#             self.l1.grid(row=0, column=1, pady=5, padx=5)
#             self.imagepathpostgres = tkinter.Entry(self.tab2, font=("HelvLight", 16), width=80, bg='white', borderwidth=0)
#             self.imagepathpostgres.insert(0, "Input Path")
#             self.imagepathpostgres.grid(row=0, column=2, columnspan=3, pady=5, padx=5)
#             self.imagepathpostgres.bind("<Button-1>", lambda event: self.clear_entry(self.imagepathpostgres))

#             self.folderbrowsebutton = tkinter.Button(self.tab2, text="Browse", command=self.getdirpathpostgres, borderwidth=0,
#                                                      font=("HelvLight", 16),
#                                                      bg='white')
#             self.folderbrowsebutton.grid(row=0, column=13, pady=5, padx=5)

#             self.btn1 = tkinter.Button(self.tab2, text="RUN", height=1, width=20, command=self.postgresstojson,
#                                        font=("HelvLight", 16),
#                                        bg='white')
#             self.btn1.grid(row=6, column=2, pady=10, padx=10)

#             self.btn2 = tkinter.Button(self.tab2, text="Cancel", height=1, width=20, command=self.finish,
#                                        font=("HelvLight", 16),
#                                        bg='white')
#             self.btn2.grid(row=6, column=3, pady=10, padx=10)

#             self.pb1 = ttk.Progressbar(
#                 self.tab2,
#                 orient='horizontal',
#                 mode='determinate',
#                 length=560
#             )
#             self.pb1.grid(row=8, column=2, pady=5, padx=5)
#             # label
#             self.value_label1 = ttk.Label(self.tab1, text=self.update_progresstojson_label())
#             self.value_label1.grid(row=9, column=2, pady=5, padx=5)
#         except Exception as E:
#             messagebox.showwarning('UnSuccesful Run', 'Got error...')
#             self.tw.destroy()
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             print( str(exc_tb.tb_lineno) + str(E))

#     def jsontopostgress(self):
#         jsonparser = JsonParser(self.dirpath, DatabaseConnection)
#         messagebox.showinfo("Successful Run", "Data Imported Successfully.")
#         dt_string = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
#         print('Endtime: ', dt_string)

#     def postgresstojson(self):
#         jsonparser = postgres_to_Json_parser.JsonParser(self.dirpathpostgres, DatabaseConnection)
#         messagebox.showinfo("Successful Run", "Data Exported Successfully.")
#         dt_string = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
#         print('Endtime: ', dt_string)

#     def getdirpath(self):
#         try:
#             self.dirpath = filedialog.askdirectory()
#             self.imagepath.delete(0, END)
#             self.imagepath.insert(END,self.dirpath)
#         except Exception as E:
#             messagebox.showwarning('UnSuccesful Run', 'Got error...')
#             self.tw.destroy()
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             print(exc_tb.tb_lineno)
#             return str(E)

#     def getdirpathpostgres(self):
#         try:
#             self.dirpathpostgres = filedialog.askdirectory()
#             self.imagepathpostgres.delete(0, END)
#             self.imagepathpostgres.insert(END,self.dirpathpostgres)
#         except Exception as E:
#             messagebox.showwarning('UnSuccesful Run', 'Got error...')
#             self.tw.destroy()
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             print(exc_tb.tb_lineno)
#             return str(E)

#     def update_progress_label(self):
#         return f"Current Progress: {self.percentage}%"

#     def update_progresstojson_label(self):
#         return f"Current Progress: {self.percentage_postgres}%"

#     def clear_entry(self, entry):
#         try:
#             entry.delete(0, END)
#         except Exception as E:
#             messagebox.showwarning('UnSuccesful Run', 'Got error...')
#             self.tw.destroy()
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             print(exc_tb.tb_lineno)
#             return str(E)

#     def finish(self):
#         self.tw.destroy()

# if __name__ == "__main__":
#     dt_string = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
#     print('Starttime: ',dt_string)
#     tw = tkinter.Tk()
#     App = InoMap(tw)
#     DatabaseConnection = DatabaseConnection(loadargs.data['database'])
#     tw.mainloop()



