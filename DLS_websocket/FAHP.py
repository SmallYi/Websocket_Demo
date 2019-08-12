
import numpy as np
import pandas as pd
import csv

class FAHP():
    def __init__(self):
        pass

    def get_global_weight(self,total_matrix):
        m = total_matrix[0].shape[0]
        n = len(total_matrix)
        weight = []
        for i in range(0,n):
            if self.judge_consistency(total_matrix[i]):
                w = self.get_weight(total_matrix[i])
            else:
                total_matrix[i] = self.turn_consistency(total_matrix[i])
                w = self.get_weight(total_matrix[i])
            if i == 0:
                w0 = w
            else:
                for j in range(0,len(w)):
                    w[j] = round((w[j] * w0[i-1]),4)
                weight += w
        return weight




    def get_weight(self,judge_matrix):
        n = len(judge_matrix)
        a = []
        weigh = []
        if self.judge_consistency(judge_matrix):
            pass
        else:
            judge_matrix = self.turn_consistency(judge_matrix)
        for i in range(0,n):
            temp = 0
            for j in range(0,n):
                temp += judge_matrix[i,j]
            w = round((temp + n / 2 - 1) / (n * (n - 1)), 2)
            weigh.append(w)
        weigh = self.Vector_normal(weigh)
        return weigh


    def judge_consistency(self,matrix):
        n = len(matrix)
        for i in range(0,n):
            for j in range(0,n):
                for k in range(0,n):
                    if matrix[i,j] == round((matrix[i,k] - matrix[j,k] + 0.5),1):
                        pass
                    else:
                        return 0
        return 1

    def turn_consistency(self,martix):
        r = []
        n = len(martix)
        for i in range(0,n):
            temp = 0
            for k in range(0,n):
                temp += martix[i,k]
            r.append(temp)
        for i in range(0,n):
            for j in range(0,n):
                martix[i,j] = round((((r[i] - r[j])/(2*(n-1))) + 0.5),2)
        return martix


    def Vector_normal(self,vec):
        n = len(vec)
        s = sum(vec)
        for i in range(0,n):
            vec[i] /= s
        return vec


class Evaluation():
    def __init__(self):
        pass

    def Membership_function(self,judge_set,indicator):
        n = len(judge_set)
        if judge_set[0] > judge_set[1]:
            tend = 0
        else:
            tend = 1
        menbership_vector = []
        for i in range(0,n):
            member = 0
            if i-1 >= 0 and indicator >= judge_set[i-1] and indicator < judge_set[i]:
                member = round((indicator - judge_set[i-1]) / (judge_set[i] - judge_set[i-1]), 2)
            elif i+1 <= n-1 and indicator >= judge_set[i] and indicator < judge_set[i+1]:
                member = round((judge_set[i+1] - indicator) / (judge_set[i+1] - judge_set[i]), 2)
            elif tend == 1:
                if indicator < judge_set[0] and i == 0:
                    member = 1
                elif indicator > judge_set[-1] and i == n-1:
                    member = 1
                else:
                    member = 0
            elif tend == 0:
                if indicator < judge_set[-1] and i == n-1:
                    member = 1
                elif indicator > judge_set[0] and i == 0:
                    member = 1
                else:
                    member = 0
            menbership_vector.append(member)
        return menbership_vector


    def Membership_matrix(self,matrix_level,vector_indicator):
        matrix_len = len(matrix_level)
        matrix_degree = []
        for i in range(0,matrix_len):
            level = matrix_level[i]
            indicator = vector_indicator[i]
            degree = self.Membership_function(level,indicator)
            matrix_degree.append(degree)
        return matrix_degree


    def fuzzy_evaluate_result(self,weight_vector,matrix_degree):
        result = []
        len_index = len(weight_vector)
        for i in range(4):
            v = 0
            for j in range(len_index):
                v += weight_vector[j] * matrix_degree[j][i]
            result.append(round(v,2))
        s = sum(result)
        for i in range(4):
            result[i] = round((result[i] / s),2)
        return result



A = []

A0 = np.array([
    [0.5,0.3,0.1],\
    [0.7,0.5,0.3],\
    [0.9,0.7,0.5]
])
A.append(A0)

A1 = np.array([
    [0.5,0.8,0.9,0.2],\
    [0.2,0.5,0.8,0.1],\
    [0.1,0.2,0.5,0.1],\
    [0.8,0.9,0.9,0.5]
])
A.append(A1)

A2 = np.array([
    [0.5,0.2,0.6],\
    [0.8,0.5,0.9],\
    [0.4,0.1,0.5]
])
A.append(A2)

A3 = np.array([
    [0.5,0.6,0.3],\
    [0.4,0.5,0.2],\
    [0.7,0.8,0.5]
])
A.append(A3)

matrix_level = np.array([
    [0.1,0.3,0.55,0.85],\
    [0.1,0.3,0.55,0.85],\
    [0.1,0.3,0.55,0.85],\
    [0.1,0.3,0.55,0.85],\
    [0.5,1.5,2.5,3], \
    [0.1, 0.3, 0.55, 0.85], \
    [0.5,1.5,2.5,3], \
    [0.5,1.5,2.5,3], \
    [0.5,1.5,2.5,3], \
    [0.85,0.75,0.5,0.3]
])
print('A',A)

c = []
c0 = [0.18,0.35,0.08,0.05,0.2,0,0.1,0.4,0.5,1]
c.append(c0)
c1 = [0.4,0.42,0.1,0.75,0.5,0.07,0.8,0.4,0.5,1]
c.append(c1)
c2 = [0.53,0.46,0.11,0.9,1.4,0.25,1.3,2.7,2,0.85]
c.append(c2)
c3 = [0.6,0.5,0.35,0.9,2.2,0.32,1.1,1.8,2.4,0.73]
c.append(c3)
c4 = [0.64,0.46,0.12,0.95,1.8,0.3,2,4.3,2.1,0.7]
c.append(c4)
c5 = [0.68,0.51,0.11,0.99,2.2,0.5,2.6,3.1,2.7,0.65]
c.append(c5)
c6 = [0.68,0.49,0.12,0.97,2.1,0.3,2.4,3.7,2.5,0.6]
c.append(c6)
c7 = [0.8,0.6,0.2,1,4,0.8,5.4,10.6,5,0.2]
c.append(c7)

head = []
for i in range(0,10):
	head.append('i'+str(i))
dataframec = pd.DataFrame(c,columns = head)
head0 = head[0:3]
dataframe0 = pd.DataFrame(A0,columns = head0)
head1 = head[0:4]
dataframe1 = pd.DataFrame(A1,columns = head1)
dataframe2 = pd.DataFrame(A2,columns = head0)
dataframe3 = pd.DataFrame(A3,columns = head0)
data = pd.DataFrame(matrix_level,columns = head1)


dataframe0.to_csv("A0.csv", index=False, sep=',')
dataframe1.to_csv("A1.csv", index=False, sep=',')
dataframe2.to_csv("A2.csv", index=False, sep=',')
dataframe3.to_csv("A3.csv", index=False, sep=',')
dataframec.to_csv("c.csv", index=False, sep=',')
data.to_csv("Matrix_level.csv",index=False,sep=',')


F = FAHP()
# print('global',F.get_global_weight(A))
weight = F.get_global_weight(A)
E = Evaluation()
cpu_judge = [0.1,0.3,0.55,0.85]
degree = E.Membership_matrix(matrix_level,c7)
eva_result = E.fuzzy_evaluate_result(weight,degree)
print('weight:',weight)
print('degree:',degree)
print('result:',eva_result)





data = pd.read_csv('c.csv')
print(data.values)
