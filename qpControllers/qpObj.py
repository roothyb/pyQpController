import pydart2 as pydart

import numpy as np
from cvxopt import normal, uniform
from numpy import array

import logging

from manipulatorTasks import positionTask


class qpObj:
    def __init__(self, skel, jointUnitWeight):

        # if logger is None:
        #     raise Exception("Logger is not set")
        # else:
        #     self.logger = logger

        self.tasks = []
        self.robot = skel
        self.dof = self.robot.ndofs
        #self.logger = logger


        self.dofWeightMatrix = np.identity(2*self.dof)

        # set the weights of the joint, descend from base to end
        for ii in range(0,self.dof):
            #self.dofWeightMatrix[ii,ii] = (self.dof - ii)*jointUnitWeight
            self.dofWeightMatrix[ii, ii] = jointUnitWeight
            
        for ii in range(self.dof, 2*self.dof):
            # We need to maximize the delta QP 
            self.dofWeightMatrix[ii, ii] = -jointUnitWeight
            

    def numTasks(self):
        return len(self.tasks)

    def weightMatrix(self):
        return self.dofWeightMatrix

    def addTask(self, task):
        self.tasks.append(task)

    def removeTask(self, task):
        self.tasks.remove(task)

    def calcMatricies(self):

        Q = np.zeros((2*self.dof, 2*self.dof))
        P = np.zeros(( 1, 2*self.dof))
        C = 0.0
        Q += self.dofWeightMatrix

        for ii in range(0, len(self.tasks)):
            [Q_add, P_add, C_add ] = self.tasks[ii].calcMatricies()
            Q += Q_add
            P += P_add
            C += C_add

        return [Q, P, C]





if __name__ == "__main__":

    print('Hello, PyDART!')

    pydart.init()

    test_world = pydart.World(1.0 / 2000.0, "../data/skel/two_cubes.skel")

    test_robot = test_world.add_skeleton("../data/KR5/KR5_sixx_R650.urdf")



    test_desiredPosition = array([0.1, 0.2, 0.3]).reshape((3,1))

    test_task = positionTask.positionTask(test_robot, test_desiredPosition)

    [Q, P, C] = test_task.calcMatricies()

    # print "The jacobian is: ", '\n', jacobian
    # print "The jacobian derivative is: ", '\n', jacobian_dot
    print "The Q matrix is: ", '\n', Q
    print "The P matrix is: ", '\n', P
    print "The C matrix is: ", '\n', C

    test_obj = qpObj(test_robot)
    test_obj.addTask(test_task)


    print "The weight matrix is: ", '\n', test_obj.dofWeightMatrix
    print "The numer of tasks is: ", test_obj.numTasks()




    transform = test_robot.bodynodes[-1].world_transform()
    rotation = transform[:3, :3]
    current_quat = pydart.utils.transformations.quaternion_from_matrix(rotation)


    # test_desiredPosition = array([0.1, 0.2, 0.3]).reshape((3,1))
    taskWeight = 1000

    test_orientationTask = orientationTask.orientationTask(test_robot, current_quat, taskWeight, Kd=5, Kp=10, bodyNodeIndex=-1)

    test_obj.addTask(test_orientationTask)
    print "The weight matrix is: ", '\n', test_obj.dofWeightMatrix
    print "The numer of tasks is: ", test_obj.numTasks()


    [Q_obj, P_obj, C_obj] = test_obj.calcMatricies()
    print "The Q_obj matrix is: ", '\n', Q_obj
    print "The P_obj matrix is: ", '\n', P_obj
    print "The C_obj matrix is: ", '\n', C_obj
