# -*- coding: utf-8 -*-
"""
/***************************************************************************
 NNJoin_engine
                          NNJoinEngine of the NNJoin plugin
 Nearest neighbour spatial join
                             -------------------
        begin                : 2014-09-04
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Håvard Tveite
        email                : havard.tveite@nmbu.no
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from qgis.core import *
from qgis.gui import *

# QGIS 3
from qgis.PyQt import QtCore
from qgis.PyQt.QtCore import QCoreApplication, QVariant


import os.path
import processing

MESSAGE_CATEGORY = 'Topology Checker'


class RandomIntegerSumTask(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description, algos,tool):
        super().__init__(description, QgsTask.CanCancel)
        self.algos=algos
        self.tool=tool
        self.total = len(self.algos)
        self.iterations = 0
        self.result=[]
        self.output=''
        self.duration=20
        self.errorCount=0
        self.exception = None
        self.errorMsg=None
        self.cancelled=False
        self.taskCompleted.connect(self.taskDone)
        self.taskTerminated.connect(self.taskDone)

    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully
        abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them
        internally and raise them in self.finished
        """
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.description()),
            MESSAGE_CATEGORY, Qgis.Info)
        wait_time = self.duration / 100
        self.output = ''
        i=0
        self.setProgress(i * 100 / self.total)
        try:
            for algo in self.algos:
                if self.cancelled:
                    break
                #print(algo[0], algo[1], algo[2])
                try:
                    output = processing.run(algo[3], algo[4], context=algo[5])
                    for grid_id in  algo[6]:
                        self.addError(algo[0], algo[1], algo[2],grid_id)
                        pass

                    if output['OUTPUT']:
                        self.result.append([algo[0], algo[1], algo[2], output['OUTPUT']])
                        pass
                    pass
                except:
                    #print([algo[0], algo[1], algo[2]])
                    pass
                i+=1
                self.setProgress(i * 100 / self.total)
                pass
            # vlayer = self.iface.addVectorLayer(uri.uri(), 'myLayer', 'postgres')
            pass
        except Exception as e:
            import traceback
            QgsMessageLog.logMessage(
                'Task "{name}" Exception: {exception}'.format(
                    name=self.description,
                    exception=traceback.format_exc()),
                MESSAGE_CATEGORY, Qgis.Critical)
            self.errorMsg = traceback.format_exc()
            return False
            pass
        return True

    def finished(self, result):
        """
        This function is automatically called when the task has
        completed (successfully or not).
        You implement finished() to do whatever follow-up stuff
        should happen after the task is complete.
        finished is always called from the main thread, so it's safe
        to do GUI operations and raise Python exceptions here.
        result is the return value from self.run.
        """
        # self.dlg.progressBar.setVisible(False)
        if result:
            QgsMessageLog.logMessage(
                'Task  "{name}" completed Successfully.\n{errorcount}'.format(name=self.description(),errorcount=self.errorCount),
                MESSAGE_CATEGORY, Qgis.Success)
        else:
            if self.exception is None:
                QgsMessageLog.logMessage(
                    'Task "{name}" is not successful but without ' \
                    'exception (probably the task was manually ' \
                    'canceled by the user)'.format(
                        name=self.description()),
                    MESSAGE_CATEGORY, Qgis.Warning)
            else:
                QgsMessageLog.logMessage(
                    'Task "{name}" Exception: {exception}'.format(
                        name=self.description(),
                        exception=self.exception),
                    MESSAGE_CATEGORY, Qgis.Critical)
                # raise self.exception

    def cancel(self):
        self.cancelled = True
        QgsMessageLog.logMessage(
            'Task "{name}" was canceled'.format(
                name=self.description()),
            MESSAGE_CATEGORY, Qgis.Info)
        super().cancel()

    def taskDone(self):
        self.errorCount=self.tool.loadResult(self.result)
        self.tool.done(self.errorCount)
        pass

    def addError(self,input,rule,target,grid_id):
        try:
            # x = requests.get(url, params=param)
            self.loadData()
            from PyQt5.QtSql import QSqlDatabase,QSqlQuery
            db = QSqlDatabase.addDatabase(self.data['dbtype'])
            db.setHostName(self.data['host'])
            db.setDatabaseName(self.data['db'])
            db.setPort(int(self.data['port']))
            db.setUserName(self.data['user'])
            db.setPassword(self.decrypt(self.data['pwd']))
            db_open=db.open()
            if not db_open:
                #print(db.lastError().databaseText())
                return
            input="'"+input+"'"
            rule = "'" + rule + "'"
            grid_id = "'" + str(grid_id) + "'"

            if target != None:
                target = "'" + target + "'"
                pass
            else:
                target="NULL"
            # query the table
            try:
                qry2 = str(self.data['insert_must_pass_query']).format(input_lyr=input, error_type=rule, grid_id=grid_id, target_lyr=target)
                # print(qry2)
                query2 = db.exec(qry2)
                #print(query2.lastError().databaseText())
                query2.finish()
                qry2 = str(self.data['delete_query']).format(input_lyr=input, error_type=rule,
                                                                       grid_id=grid_id, target_lyr=target)
                # print(qry2)
                query2 = db.exec(qry2)
                #(query2.lastError().databaseText())
                query2.finish()
                db.commit()
                pass
            except:
                db.rollback()
                import traceback
                traceback.print_exc()
                pass
            pass
        except:
            import traceback
            traceback.print_exc()
            pass
        pass

    def decrypt(self,message):
        newS = ''
        for car in message:
            newS = newS + chr(ord(car) - 2)
        return newS

    def loadData(self):
        import json
        self.data = {}
        path2 = self.tool.plugin_dir
        path = os.path.join(path2, "AppConfig.json")
        path=path.replace("\\","/")
        #print(path)
        try:
            if os.path.exists(path):
                with open(path) as json_file:
                    self.data = json.load(json_file)
                    pass
                # print (self.data)
                pass
        except Exception as e:
            err1 = "unable read data:-\n" + str(e)
            QMessageBox.information(None, 'Error', err1)
            import traceback
            traceback.print_exc()
            pass
            pass
        # return data
        pass